"""
GHOSTMAP Endpoint Prober — Probe endpoints to determine their live status.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urljoin, urlparse

import aiohttp


from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG
from ghostmap.utils.throttler import AdaptiveThrottler


logger = logging.getLogger("ghostmap.auditor.prober")


class EndpointProber:
    """
    Probes discovered endpoints to determine if they are active,
    require authentication, or are dead.
    """

    def __init__(self, config: Optional[GhostMapConfig] = None):
        self.config = config or DEFAULT_CONFIG

    def probe_all(
        self,
        endpoints: List[Dict[str, Any]],
        base_url: str,
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Probe all endpoints against a base URL.

        Args:
            endpoints: List of endpoint dicts
            base_url: Base URL to probe against (e.g., http://localhost:8080)
            callback: Progress callback(index, total, url, status_code)

        Returns:
            Dict with 'active', 'auth_required', 'redirect', 'dead' counts
            and 'details' dict keyed by endpoint path
        """
        # Run the async probe loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self._probe_all_async(endpoints, base_url, callback)
            )
        finally:
            loop.close()

    async def _probe_all_async(
        self,
        endpoints: List[Dict[str, Any]],
        base_url: str,
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Async implementation of probe_all."""
        base_url = base_url.rstrip("/")

        results = {
            "active": 0,
            "auth_required": 0,
            "redirect": 0,
            "dead": 0,
            "error": 0,
            "soft_404": 0,
            "total": len(endpoints),
            "details": {},
        }
        
        # Soft 404 Baseline
        import uuid
        baseline = None
        try:
            rand_path = f"{base_url}/{uuid.uuid4()}"
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                 async with session.get(rand_path, allow_redirects=False, timeout=5) as resp:
                     baseline = {
                         "status": resp.status,
                         "length": len(await resp.read()),
                         "location": resp.headers.get("Location", "")
                     }
            logger.info(f"Prober Baseline: {baseline}")
        except Exception as e:
            logger.warning(f"Prober Baseline failed: {e}")

        # Extract unique paths
        paths = []
        for ep in endpoints:
            path = ep.get("url") or ep.get("normalized_url") or ep.get("endpoint", "")
            if path:
                # Extract just the path component
                if path.startswith(("http://", "https://")):
                    path = urlparse(path).path
                paths.append(path)

        paths = list(set(paths))
        total = len(paths)

        connector = aiohttp.TCPConnector(limit=self.config.probe_concurrency)
        timeout = aiohttp.ClientTimeout(total=self.config.probe_timeout)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            semaphore = asyncio.Semaphore(self.config.probe_concurrency)
            throttler = AdaptiveThrottler(initial_rate_limit=self.config.rate_limit)

            async def probe_one(idx: int, path: str):
                async with semaphore:
                    await throttler.wait()
                    
                    full_url = base_url + path
                    result = await self._probe_single(session, full_url)
                    
                    # Report status to throttler
                    await throttler.report_result(result.get("status_code", 0))
                    
                    results["details"][path] = result

                    # Categorize
                    status = result.get("status_code", 0)
                    is_soft_404 = False
                    
                    if baseline and status == baseline["status"]:
                        # Check redirect
                        if status in (301, 302, 307, 308):
                            loc = result.get("headers", {}).get("Location", "")
                            if loc == baseline["location"]:
                                is_soft_404 = True
                        # Check length for 200 and other statuses (403, 500, etc)
                        else:
                            length = result.get("response_size", 0)
                            if abs(length - baseline["length"]) < (baseline["length"] * 0.1) + 10:
                                is_soft_404 = True
                    
                    if is_soft_404:
                         results["soft_404"] += 1
                         result["is_soft_404"] = True
                         # Treat as dead/noise? Or just mark it?
                         # Let's count it as soft_404 but maybe not active?
                         # If we count it as active, it confuses users.
                         # Let's subtract from active if it was active.
                         # But wait, we categorize below.
                    
                    if is_soft_404:
                        # Don't count as active/redirect
                        pass 
                    elif 200 <= status < 300:
                        results["active"] += 1
                    elif status in (301, 302, 307, 308):
                        results["redirect"] += 1
                    elif status in (401, 403):
                        results["auth_required"] += 1
                    elif status == 0:
                        results["error"] += 1
                    else:
                        results["dead"] += 1

                    if callback:
                        callback(idx + 1, total, full_url, status)

            tasks = [probe_one(i, p) for i, p in enumerate(paths)]
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(
            f"Probing complete: {results['active']} active, "
            f"{results['auth_required']} auth-required, "
            f"{results['redirect']} redirect, "
            f"{results['dead']} dead, "
            f"{results['error']} errors"
        )
        return results

    async def _probe_single(
        self, session: aiohttp.ClientSession, url: str
    ) -> Dict[str, Any]:
        """
        Probe a single URL.

        Returns:
            Dict with status_code, headers, content_type, is_debug, response_size
        """
        result = {
            "url": url,
            "status_code": 0,
            "content_type": "",
            "response_size": 0,
            "is_debug": False,
            "is_admin": False,
            "has_auth": False,
            "error": None,
        }

        for method in self.config.probe_methods:
            try:
                async with session.request(
                    method, url, allow_redirects=False, ssl=False
                ) as response:
                    result["status_code"] = response.status
                    result["content_type"] = response.content_type or ""

                    # Check headers for interesting indicators
                    headers = dict(response.headers)
                    result["has_auth"] = any(
                        h.lower() in ("www-authenticate", "authorization")
                        for h in headers
                    )

                    # Read limited body for analysis
                    if method == "GET" and response.status == 200:
                        body = await response.read()
                        result["response_size"] = len(body)

                        # Check for debug/admin indicators
                        body_text = body[:5000].decode("utf-8", errors="ignore").lower()
                        debug_indicators = [
                            "debug", "stack trace", "traceback",
                            "exception", "phpinfo", "server info",
                            "environment variables", "django debug",
                        ]
                        admin_indicators = [
                            "admin panel", "dashboard", "control panel",
                            "management console", "admin login",
                        ]

                        result["is_debug"] = any(
                            ind in body_text for ind in debug_indicators
                        )
                        result["is_admin"] = any(
                            ind in body_text for ind in admin_indicators
                        )

                    # If HEAD succeeded, no need to try GET
                    if response.status != 405:
                        break

            except asyncio.TimeoutError:
                result["error"] = "timeout"
            except Exception as e:
                result["error"] = str(e)

        return result
