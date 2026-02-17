"""
GHOSTMAP Endpoint Extractor — Regex-based extraction of API endpoints from text.
"""

import re
import logging
from typing import List, Set, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger("ghostmap.collector.endpoint_extractor")


# --------------------------------------------------------------------------
# Compiled regex patterns for endpoint discovery
# --------------------------------------------------------------------------

PATTERNS: List[Dict[str, Any]] = [
    # REST API paths: /api/v1/users, /api/users/123
    {
        "name": "rest_api_path",
        "pattern": re.compile(
            r"""(?:['"`])(/(?:api|rest|v\d+)/[a-zA-Z0-9/_\-{}:.]+)(?:['"`])""",
            re.IGNORECASE,
        ),
    },
    # Absolute URL paths: https://example.com/api/endpoint
    {
        "name": "absolute_url",
        "pattern": re.compile(
            r"""(https?://[a-zA-Z0-9.\-]+(?::\d+)?/[a-zA-Z0-9/_\-?&=%.#{}:@]+)""",
            re.IGNORECASE,
        ),
    },
    # Relative paths starting with /
    {
        "name": "relative_path",
        "pattern": re.compile(
            r"""(?:['"`])(/[a-zA-Z0-9/_\-{}:.]+(?:\?[a-zA-Z0-9_=&]+)?)(?:['"`])""",
        ),
    },
    # fetch() calls: fetch('/api/data')
    {
        "name": "fetch_call",
        "pattern": re.compile(
            r"""fetch\s*\(\s*['"`]([^'"`\s]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # axios calls: axios.get('/api/data'), axios.post('/api/data')
    {
        "name": "axios_call",
        "pattern": re.compile(
            r"""axios\.(?:get|post|put|patch|delete|head|options)\s*\(\s*['"`]([^'"`\s]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # XMLHttpRequest: xhr.open('GET', '/api/data')
    {
        "name": "xhr_call",
        "pattern": re.compile(
            r"""\.open\s*\(\s*['"`](?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)['"`]\s*,\s*['"`]([^'"`\s]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # jQuery AJAX: $.ajax({url: '/api/data'})
    {
        "name": "jquery_ajax",
        "pattern": re.compile(
            r"""\$\.(?:ajax|get|post|getJSON)\s*\(\s*['"`]([^'"`\s]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # Route definitions: path: '/users', route: '/api/data'
    {
        "name": "route_definition",
        "pattern": re.compile(
            r"""(?:path|route|url|endpoint|uri)\s*[:=]\s*['"`]([/][a-zA-Z0-9/_\-{}:.]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # Express.js routes: app.get('/api/data', ...)
    {
        "name": "express_route",
        "pattern": re.compile(
            r"""(?:app|router)\.(?:get|post|put|patch|delete|all|use)\s*\(\s*['"`]([/][^'"`\s]+)['"`]""",
            re.IGNORECASE,
        ),
    },
    # GraphQL endpoints
    {
        "name": "graphql_endpoint",
        "pattern": re.compile(
            r"""['"`](/graphql[a-zA-Z0-9/_\-]*)['"`]""",
            re.IGNORECASE,
        ),
    },
    # WebSocket URLs: ws://host/path, wss://host/path
    {
        "name": "websocket_url",
        "pattern": re.compile(
            r"""(wss?://[a-zA-Z0-9.\-]+(?::\d+)?/[a-zA-Z0-9/_\-?&=%.]+)""",
            re.IGNORECASE,
        ),
    },
]


# Paths to exclude (static assets, common false positives)
EXCLUDED_EXTENSIONS = {
    ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".map", ".mp3", ".mp4", ".webm", ".ogg",
    ".pdf", ".zip", ".tar", ".gz",
}

EXCLUDED_PREFIXES = {
    "/static/", "/assets/", "/images/", "/img/", "/css/",
    "/fonts/", "/media/", "/public/", "/#", "/node_modules/",
}


class EndpointExtractor:
    """
    Extract API endpoints and paths from arbitrary text content
    using a library of regex patterns.
    """

    def __init__(self, additional_patterns: List[Dict[str, Any]] = None):
        """
        Args:
            additional_patterns: Extra patterns to add to the defaults.
                Each should have 'name' (str) and 'pattern' (compiled regex).
        """
        self.patterns = list(PATTERNS)
        if additional_patterns:
            self.patterns.extend(additional_patterns)

    def extract(self, text: str, base_domain: str = "") -> List[Dict[str, Any]]:
        """
        Extract all endpoints from text content.

        Args:
            text: Source text (HTML, JS, etc.)
            base_domain: Optional domain to filter results by

        Returns:
            List of dicts: {endpoint, pattern_name, raw_match}
        """
        found: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        for pat_info in self.patterns:
            matches = pat_info["pattern"].findall(text)
            for match in matches:
                endpoint = self._normalize_endpoint(match)
                if not endpoint or endpoint in seen:
                    continue
                if self._should_exclude(endpoint):
                    continue
                if base_domain and not self._matches_domain(endpoint, base_domain):
                    continue

                seen.add(endpoint)
                found.append({
                    "endpoint": endpoint,
                    "pattern_name": pat_info["name"],
                    "raw_match": match,
                })

        logger.debug(f"Extracted {len(found)} unique endpoints from text ({len(text)} chars)")
        return found

    def extract_endpoints_only(self, text: str, base_domain: str = "") -> List[str]:
        """
        Extract just the endpoint strings (no metadata).

        Args:
            text: Source text
            base_domain: Optional domain filter

        Returns:
            Sorted list of unique endpoint strings
        """
        results = self.extract(text, base_domain)
        return sorted(set(r["endpoint"] for r in results))

    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        """Clean up and normalize an extracted endpoint."""
        endpoint = endpoint.strip().rstrip("/")

        # Remove trailing punctuation that may have been captured
        endpoint = endpoint.rstrip(".,;:!?)'\"")

        # Skip if too short or doesn't look like a path
        if len(endpoint) < 2:
            return ""

        return endpoint

    @staticmethod
    def _should_exclude(endpoint: str) -> bool:
        """Check if endpoint should be excluded (static assets, etc.)."""
        lower = endpoint.lower()

        # Check file extensions
        for ext in EXCLUDED_EXTENSIONS:
            if lower.endswith(ext):
                return True

        # Check path prefixes
        path = urlparse(endpoint).path if "://" in endpoint else endpoint
        for prefix in EXCLUDED_PREFIXES:
            if path.lower().startswith(prefix):
                return True

        return False

    @staticmethod
    def _matches_domain(endpoint: str, base_domain: str) -> bool:
        """Check if an absolute URL matches the target domain."""
        if not endpoint.startswith(("http://", "https://", "ws://", "wss://")):
            # Relative paths always match
            return True

        parsed = urlparse(endpoint)
        host = parsed.hostname or ""
        return host.endswith(base_domain)
