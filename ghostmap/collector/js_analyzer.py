"""
GHOSTMAP JS Analyzer — Download JavaScript files and extract endpoints.
"""

import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin

from ghostmap.utils.http_client import RateLimitedClient
from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG
from ghostmap.collector.endpoint_extractor import EndpointExtractor

logger = logging.getLogger("ghostmap.collector.js_analyzer")


class JSAnalyzer:
    """
    Downloads JavaScript files and extracts API endpoints from their content.
    Discovers inline script endpoints from HTML pages too.
    """

    def __init__(self, config: Optional[GhostMapConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.client = RateLimitedClient(self.config)
        self.extractor = EndpointExtractor()

    def analyze_js_urls(
        self,
        js_urls: List[str],
        base_domain: str = "",
        callback=None,
    ) -> Dict[str, Any]:
        """
        Download and analyze multiple JS files for API endpoints.

        Args:
            js_urls: List of JS file URLs to download and analyze
            base_domain: Domain to filter endpoints by
            callback: Progress callback(url, index, total, endpoints_found)

        Returns:
            Dict with:
                - endpoints: List of {endpoint, source_file, pattern_name}
                - stats: {files_analyzed, files_failed, total_endpoints}
        """
        all_endpoints = []
        seen_endpoints = set()
        files_analyzed = 0
        files_failed = 0
        total = len(js_urls)

        logger.info(f"Analyzing {total} JavaScript files")

        for i, js_url in enumerate(js_urls):
            try:
                content = self._download_js(js_url)
                if content is None:
                    files_failed += 1
                    continue

                extracted = self.extractor.extract(content, base_domain)
                files_analyzed += 1

                for item in extracted:
                    ep = item["endpoint"]
                    if ep not in seen_endpoints:
                        seen_endpoints.add(ep)
                        all_endpoints.append({
                            "endpoint": ep,
                            "source_file": js_url,
                            "pattern_name": item["pattern_name"],
                        })

                if callback:
                    callback(js_url, i + 1, total, len(extracted))

            except Exception as e:
                logger.error(f"Error analyzing {js_url}: {e}")
                files_failed += 1

        result = {
            "endpoints": all_endpoints,
            "stats": {
                "files_analyzed": files_analyzed,
                "files_failed": files_failed,
                "total_endpoints": len(all_endpoints),
            },
        }

        logger.info(
            f"JS analysis complete: {files_analyzed} files analyzed, "
            f"{files_failed} failed, {len(all_endpoints)} unique endpoints found"
        )
        return result

    def extract_from_html(self, html_content: str, page_url: str = "", base_domain: str = "") -> Dict[str, Any]:
        """
        Extract endpoints from inline scripts and script src attributes in HTML.

        Args:
            html_content: Raw HTML content
            page_url: URL of the page (for resolving relative script srcs)
            base_domain: Domain to filter endpoints by

        Returns:
            Dict with endpoints and discovered JS URLs
        """
        import re

        # Extract inline script content
        inline_scripts = re.findall(
            r"<script[^>]*>(.*?)</script>",
            html_content,
            re.DOTALL | re.IGNORECASE,
        )

        # Extract script src URLs
        script_srcs = re.findall(
            r"""<script[^>]+src\s*=\s*['"]([^'"]+)['"]""",
            html_content,
            re.IGNORECASE,
        )

        # Analyze inline scripts
        all_text = "\n".join(inline_scripts)
        endpoints = self.extractor.extract(all_text, base_domain)

        # Resolve script src URLs
        js_urls = []
        for src in script_srcs:
            if src.startswith(("http://", "https://")):
                js_urls.append(src)
            elif page_url:
                js_urls.append(urljoin(page_url, src))

        return {
            "inline_endpoints": endpoints,
            "js_urls": js_urls,
        }

    def _download_js(self, url: str) -> Optional[str]:
        """
        Download a JS file with size limit enforcement.

        Args:
            url: URL of the JS file

        Returns:
            JS file content as string, or None on failure
        """
        try:
            response = self.client.get(url, timeout=self.config.request_timeout)
            response.raise_for_status()

            # Check content length
            content_length = len(response.content)
            if content_length > self.config.max_js_file_size:
                logger.warning(
                    f"JS file too large ({content_length} bytes), skipping: {url}"
                )
                return None

            return response.text

        except Exception as e:
            logger.debug(f"Failed to download JS: {url} — {e}")
            return None

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
