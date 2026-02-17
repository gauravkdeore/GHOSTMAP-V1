"""
GHOSTMAP Noise Filter — Remove false positives from scan results.

Identifies and filters out URLs that are public content (blogs, FAQs,
marketing pages) or tracking artifacts (UTM params, analytics).
"""

import re
import logging
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any

logger = logging.getLogger("ghostmap.auditor.noise_filter")

# ── Path prefixes that are almost always public content ──────────────
PUBLIC_CONTENT_PREFIXES = (
    "/blog", "/news", "/press", "/media", "/events",
    "/faq", "/help", "/support", "/kb", "/knowledge",
    "/docs", "/documentation", "/guide", "/tutorial", "/how-to",
    "/about", "/careers", "/jobs", "/team", "/contact",
    "/terms", "/privacy", "/legal", "/cookie", "/disclaimer",
    "/pricing", "/plans", "/features", "/product",
    "/category", "/tag", "/archive", "/author",
    "/sitemap", "/rss", "/feed", "/atom",
    "/wp-content", "/wp-includes", "/wp-json/wp",
    "/cdn-cgi",
)

# ── File extensions that are never interesting endpoints ─────────────
STATIC_EXTENSIONS = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".webm", ".mp3", ".wav",
    ".pdf", ".zip", ".gz", ".tar",
    ".map", ".min.js", ".min.css",
    ".xml", ".txt", ".webp", ".avif",
)

# ── Query params that are marketing / tracking noise ─────────────────
NOISE_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid",
    "ref", "source", "share", "lang", "locale", "page", "p",
    "sort", "order", "limit", "offset",
}

# ── Keywords that RESCUE an endpoint from being noise ────────────────
RESCUE_KEYWORDS = {
    "admin", "login", "auth", "token", "secret", "key", "config",
    "debug", "internal", "api", "graphql", "actuator", "console",
    "upload", "export", "import", "backup", "database", "sql",
    "webhook", "callback", "oauth", "session", "password", "cred",
}


class NoiseFilter:
    """Filter out false-positive / low-value endpoints."""

    def __init__(self, config=None):
        self.config = config
        self._stats = {"total": 0, "filtered": 0, "kept": 0}

    def filter_endpoints(
        self, endpoints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove noise endpoints from the list.

        Returns:
            Filtered list (noise removed). Each kept endpoint gets
            'is_noise': False. Removed ones are not returned.
        """
        self._stats = {"total": len(endpoints), "filtered": 0, "kept": 0}
        result = []

        for ep in endpoints:
            url = ep.get("url") or ep.get("normalized_url") or ep.get("endpoint", "")

            if self._is_noise(url):
                self._stats["filtered"] += 1
                continue

            # Strip tracking params from the URL for cleaner output
            clean_url = self._strip_noise_params(url)
            if clean_url != url:
                ep["url"] = clean_url
                ep["original_url"] = url

            ep["is_noise"] = False
            result.append(ep)

        self._stats["kept"] = len(result)
        logger.info(
            f"NoiseFilter: {self._stats['filtered']} noise removed, "
            f"{self._stats['kept']} kept out of {self._stats['total']}"
        )
        return result

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def _is_noise(self, url: str) -> bool:
        """Determine if a URL is noise (public content / static asset)."""
        if not url:
            return True

        parsed = urlparse(url)
        path = parsed.path.lower().rstrip("/")

        # 1. Static file extensions
        for ext in STATIC_EXTENSIONS:
            if path.endswith(ext):
                return True

        # 2. Check if ALL query params are tracking noise
        if parsed.query:
            params = parse_qs(parsed.query)
            param_names = set(k.lower() for k in params.keys())
            if param_names and param_names.issubset(NOISE_QUERY_PARAMS):
                # URL only differs by tracking params → noise
                return True

        # 3. Public content prefix check (with rescue)
        for prefix in PUBLIC_CONTENT_PREFIXES:
            if path.startswith(prefix):
                # Check if it contains a rescue keyword
                if any(kw in path for kw in RESCUE_KEYWORDS):
                    return False  # Rescued!
                return True  # Noise

        return False

    @staticmethod
    def _strip_noise_params(url: str) -> str:
        """Remove tracking/marketing query params from a URL."""
        parsed = urlparse(url)
        if not parsed.query:
            return url

        params = parse_qs(parsed.query, keep_blank_values=True)
        clean_params = {
            k: v for k, v in params.items()
            if k.lower() not in NOISE_QUERY_PARAMS
        }

        if not clean_params:
            # All params were noise → return URL without query
            return parsed._replace(query="").geturl()

        from urllib.parse import urlencode
        new_query = urlencode(clean_params, doseq=True)
        return parsed._replace(query=new_query).geturl()
