"""
GHOSTMAP CommonCrawl Scraper — Query the CommonCrawl Index API for URLs.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from ghostmap.utils.http_client import RateLimitedClient
from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG

logger = logging.getLogger("ghostmap.collector.commoncrawl")

# CommonCrawl index collections API
CC_INDEX_LIST_URL = "https://index.commoncrawl.org/collinfo.json"


class CommonCrawlScraper:
    """
    Scrapes the CommonCrawl Index API for URLs associated with a target domain.
    Queries recent crawl indexes for historical page data.
    """

    def __init__(self, config: Optional[GhostMapConfig] = None, max_indexes: int = 3):
        """
        Args:
            config: GhostMapConfig instance
            max_indexes: Number of recent CC indexes to query (default: 3)
        """
        self.config = config or DEFAULT_CONFIG
        self.client = RateLimitedClient(self.config)
        self.max_indexes = max_indexes

    def _get_index_urls(self) -> List[str]:
        """Fetch the list of available CommonCrawl index API endpoints."""
        try:
            response = self.client.get(CC_INDEX_LIST_URL, timeout=self.config.commoncrawl_timeout)
            response.raise_for_status()
            indexes = response.json()
            # Return the most recent N index CDX API URLs
            api_urls = [idx["cdx-api"] for idx in indexes if "cdx-api" in idx]
            return api_urls[: self.max_indexes]
        except Exception as e:
            logger.error(f"Failed to fetch CommonCrawl index list: {e}")
            return []

    def fetch_urls(
        self,
        domain: str,
        limit: Optional[int] = None,
        callback=None,
    ) -> List[Dict[str, Any]]:
        """
        Query CommonCrawl indexes for URLs matching the target domain.

        Args:
            domain: Target domain (e.g., 'example.com')
            limit: Max results per index query
            callback: Progress callback function(index_name, batch_count, total_so_far)

        Returns:
            List of endpoint dicts: {url, timestamp, status_code, mime_type, source}
        """
        logger.info(f"Querying CommonCrawl for domain: {domain}")

        index_urls = self._get_index_urls()
        if not index_urls:
            logger.warning("No CommonCrawl indexes available")
            return []

        logger.info(f"Querying {len(index_urls)} CommonCrawl indexes")

        results = []
        total_fetched = 0

        for idx_url in index_urls:
            idx_name = idx_url.split("/")[-2] if "/" in idx_url else idx_url

            params = {
                "url": f"*.{domain}",
                "output": "json",
            }
            if limit:
                params["limit"] = str(limit)

            try:
                response = self.client.get(
                    idx_url,
                    params=params,
                    timeout=self.config.commoncrawl_timeout,
                )
                response.raise_for_status()
            except Exception as e:
                logger.warning(f"CommonCrawl index {idx_name} query failed: {e}")
                continue

            # CommonCrawl returns one JSON object per line (NDJSON)
            lines = response.text.strip().split("\n")
            batch_count = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    entry = {
                        "url": record.get("url", ""),
                        "timestamp": record.get("timestamp", ""),
                        "status_code": str(record.get("status", "")),
                        "mime_type": record.get("mime", ""),
                        "source": "commoncrawl",
                    }
                    if entry["url"]:
                        results.append(entry)
                        batch_count += 1
                except json.JSONDecodeError:
                    continue

            total_fetched += batch_count
            logger.info(f"CommonCrawl {idx_name}: fetched {batch_count} URLs (total: {total_fetched})")

            if callback:
                callback(idx_name, batch_count, total_fetched)

        logger.info(f"CommonCrawl scraping complete: {len(results)} URLs found for {domain}")
        return results

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
