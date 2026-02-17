"""
GHOSTMAP Wayback Machine Scraper — Query the Wayback CDX API for historical URLs.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from ghostmap.utils.http_client import RateLimitedClient
from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG

logger = logging.getLogger("ghostmap.collector.wayback")

WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"


class WaybackScraper:
    """
    Scrapes the Wayback Machine CDX API for historical URLs
    associated with a target domain.
    """

    def __init__(self, config: Optional[GhostMapConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.client = RateLimitedClient(self.config)

    def fetch_urls(
        self,
        domain: str,
        match_type: str = "domain",
        filters: Optional[List[str]] = None,
        collapse: Optional[str] = "urlkey",
        limit: Optional[int] = None,
        callback=None,
    ) -> List[Dict[str, Any]]:
        """
        Query the Wayback CDX API and return discovered URLs.

        Args:
            domain: Target domain (e.g., 'example.com')
            match_type: CDX match type — 'exact', 'prefix', 'host', 'domain'
            filters: CDX filter expressions (e.g., ['statuscode:200'])
            collapse: Field to collapse results on (default: 'urlkey')
            limit: Max number of results
            callback: Progress callback function(batch_count, total_so_far)

        Returns:
            List of endpoint dicts: {url, timestamp, status_code, mime_type, source}
        """
        logger.info(f"Querying Wayback Machine for domain: {domain}")

        params = {
            "url": f"*.{domain}" if match_type == "domain" else domain,
            "output": "json",
            "fl": "original,timestamp,statuscode,mimetype",
            "matchType": match_type,
        }

        if collapse:
            params["collapse"] = collapse
        if limit:
            params["limit"] = str(limit)
        if filters:
            params["filter"] = filters

        results = []
        page = 0
        total_fetched = 0

        while True:
            params["page"] = str(page)

            try:
                response = self.client.get(
                    WAYBACK_CDX_URL,
                    params=params,
                    timeout=self.config.wayback_timeout,
                )
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Wayback CDX request failed (page {page}): {e}")
                break

            try:
                data = response.json()
            except json.JSONDecodeError:
                # Sometimes the last page returns empty/invalid JSON
                logger.debug(f"No more results at page {page}")
                break

            if not data or len(data) <= 1:
                # First row is the header, so <= 1 means no data rows
                break

            # First row is header: ["original", "timestamp", "statuscode", "mimetype"]
            header = data[0]
            for row in data[1:]:
                if len(row) < 4:
                    continue

                entry = {
                    "url": row[0],
                    "timestamp": row[1],
                    "status_code": row[2],
                    "mime_type": row[3],
                    "source": "wayback",
                }
                results.append(entry)

            batch_size = len(data) - 1
            total_fetched += batch_size
            logger.info(f"Wayback page {page}: fetched {batch_size} URLs (total: {total_fetched})")

            if callback:
                callback(batch_size, total_fetched)

            # If we got fewer results than expected, we've reached the end
            if batch_size < 10000:
                break

            page += 1

        logger.info(f"Wayback scraping complete: {len(results)} URLs found for {domain}")
        return results

    def extract_api_urls(self, urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter results to likely API endpoints based on URL patterns.

        Args:
            urls: Raw URL results from fetch_urls()

        Returns:
            Filtered list containing only likely API/endpoint URLs
        """
        api_indicators = [
            "/api/", "/api.", "/v1/", "/v2/", "/v3/", "/v4/",
            "/rest/", "/graphql", "/webhook", "/callback",
            "/oauth", "/auth/", "/login", "/signup",
            "/admin", "/debug", "/internal", "/health",
            ".json", ".xml", ".yaml", ".yml",
            "/swagger", "/openapi", "/docs/",
        ]

        api_urls = []
        for entry in urls:
            url_lower = entry["url"].lower()
            if any(indicator in url_lower for indicator in api_indicators):
                api_urls.append(entry)

        logger.info(f"Filtered to {len(api_urls)} likely API URLs from {len(urls)} total")
        return api_urls

    def extract_js_urls(self, urls: List[Dict[str, Any]]) -> List[str]:
        """
        Extract JavaScript file URLs from results for further analysis.

        Args:
            urls: Raw URL results from fetch_urls()

        Returns:
            List of unique JS file URLs
        """
        js_urls = set()
        for entry in urls:
            url = entry["url"]
            parsed = urlparse(url)
            path_lower = parsed.path.lower()
            if path_lower.endswith(".js") or path_lower.endswith(".mjs"):
                # Use the clean URL without query params for JS files
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                js_urls.add(clean_url)

        result = sorted(js_urls)
        logger.info(f"Found {len(result)} unique JS file URLs")
        return result

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
