"""
GHOSTMAP HTTP Client — Rate-limited, retry-capable HTTP client.
"""

import time
import random
import logging
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG
from ghostmap.utils.throttler import AdaptiveThrottler


logger = logging.getLogger("ghostmap.http")


class RateLimitedClient:
    """
    HTTP client with built-in rate limiting, automatic retries,
    exponential backoff, and User-Agent rotation.
    """

    def __init__(self, config: Optional[GhostMapConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.throttler = AdaptiveThrottler(initial_rate_limit=self.config.rate_limit)
        self._last_request_time = 0.0

        # Build session with retry strategy
        self.session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _wait_for_rate_limit(self):
        """Enforce rate limiting via adaptive throttler."""
        self.throttler.wait_sync()

    def _get_random_user_agent(self) -> str:
        """Select a random User-Agent string."""
        return random.choice(self.config.user_agents)

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Send a rate-limited GET request.

        Args:
            url: Target URL
            params: Query parameters
            headers: Additional headers (User-Agent auto-set if missing)
            timeout: Request timeout in seconds
            **kwargs: Extra args passed to requests.get

        Returns:
            requests.Response object

        Raises:
            requests.RequestException on failure after retries
        """
        self._wait_for_rate_limit()

        req_headers = {"User-Agent": self._get_random_user_agent()}
        if self.config.headers:
            req_headers.update(self.config.headers)
        if headers:
            req_headers.update(headers)

        timeout = timeout or self.config.request_timeout

        logger.debug(f"GET {url} params={params}")
        response = self.session.get(
            url, params=params, headers=req_headers, timeout=timeout, **kwargs
        )
        self.throttler.report_result_sync(response.status_code)
        return response

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        """Send a rate-limited HEAD request."""
        self._wait_for_rate_limit()

        req_headers = {"User-Agent": self._get_random_user_agent()}
        if self.config.headers:
            req_headers.update(self.config.headers)
        if headers:
            req_headers.update(headers)

        timeout = timeout or self.config.request_timeout

        logger.debug(f"HEAD {url}")
        response = self.session.head(
            url, headers=req_headers, timeout=timeout, **kwargs
        )
        self.throttler.report_result_sync(response.status_code)
        return response

    def close(self):
        """Close the underlying session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
