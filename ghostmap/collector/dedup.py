"""
GHOSTMAP Deduplication Engine — Normalize and deduplicate discovered URLs/endpoints.
"""

import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime

logger = logging.getLogger("ghostmap.collector.dedup")


class DeduplicationEngine:
    """
    Normalizes URLs and deduplicates endpoint lists, merging metadata
    from multiple sources into a single canonical record per endpoint.
    """

    def __init__(self):
        self._seen = {}  # normalized_url -> merged record

    def normalize_url(self, url: str) -> str:
        """
        Normalize a URL for deduplication:
         - Lowercase scheme and host
         - Remove fragment
         - Sort query parameters
         - Strip trailing slash
         - Remove default ports (80, 443)

        Args:
            url: Raw URL string

        Returns:
            Normalized URL string
        """
        if not url:
            return ""

        # Handle relative paths
        url_lower = url.lower()
        if not url_lower.startswith(("http://", "https://", "ws://", "wss://")):
            # For relative paths, handle query params and sorting
            try:
                # Use a dummy scheme/host to parse relative paths with query params
                # This allow generic logic to handle sorting below
                dummy_url = f"http://dummy{url}" if url.startswith("/") else f"http://dummy/{url}"
                parsed = urlparse(dummy_url)
                # We will use the parsed object in the main flow, but we need to remember it was relative
                is_relative = True
            except Exception:
                # Fallback
                path = url.strip().rstrip("/")
                return path

        try:
            parsed = urlparse(url)
        except Exception:
            return url.strip()

        # Lowercase scheme and host
        scheme = parsed.scheme.lower()
        host = (parsed.hostname or "").lower()

        # Remove default ports
        port = parsed.port
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None
        netloc = f"{host}:{port}" if port else host

        # Clean path
        path = parsed.path.rstrip("/") or "/"

        # Sort query parameters
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        sorted_query = urlencode(
            sorted(
                [(k, v[0] if len(v) == 1 else v) for k, v in query_params.items()]
            ),
            doseq=True,
        )

        # Rebuild without fragment
        # Rebuild without fragment
        if 'is_relative' in locals() and is_relative:
             # Reconstruct relative path
             relative_path = f"{path}?{sorted_query}" if sorted_query else path
             return relative_path
        
        normalized = urlunparse((scheme, netloc, path, parsed.params, sorted_query, ""))
        return normalized

    def add(self, entry: Dict[str, Any]) -> bool:
        """
        Add an entry to the dedup engine. Merges if already seen.

        Args:
            entry: Dict with at minimum 'url' key. Optional:
                   'endpoint', 'timestamp', 'source', 'status_code', etc.

        Returns:
            True if this is a new unique entry, False if it was merged
        """
        url = entry.get("url") or entry.get("endpoint", "")
        if not url:
            return False

        normalized = self.normalize_url(url)
        if not normalized:
            return False

        if normalized in self._seen:
            # Merge: update existing record
            existing = self._seen[normalized]
            self._merge_entry(existing, entry)
            return False
        else:
            # New entry
            self._seen[normalized] = {
                "url": url,
                "normalized_url": normalized,
                "sources": [entry.get("source", "unknown")],
                "timestamps": [entry.get("timestamp", "")],
                "status_codes": [entry.get("status_code", "")],
                "mime_types": [entry.get("mime_type", "")],
                "pattern_names": [entry.get("pattern_name", "")],
                "source_files": [sf for sf in [entry.get("source_file", "")] if sf],
                "first_seen": entry.get("timestamp", datetime.now().isoformat()),
                "last_seen": entry.get("timestamp", datetime.now().isoformat()),
                "occurrence_count": 1,
            }
            return True

    def _merge_entry(self, existing: Dict, new_entry: Dict):
        """Merge a new entry into an existing deduplicated record."""
        existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1

        # Append unique sources
        source = new_entry.get("source", "unknown")
        if source not in existing["sources"]:
            existing["sources"].append(source)

        # Track timestamps
        ts = new_entry.get("timestamp", "")
        if ts and ts not in existing["timestamps"]:
            existing["timestamps"].append(ts)
            # Update last_seen
            if ts > existing.get("last_seen", ""):
                existing["last_seen"] = ts

        # Track status codes
        sc = new_entry.get("status_code", "")
        if sc and sc not in existing["status_codes"]:
            existing["status_codes"].append(sc)

        # Track source files
        sf = new_entry.get("source_file", "")
        if sf and sf not in existing.get("source_files", []):
            existing.setdefault("source_files", []).append(sf)

        # Track pattern names
        pn = new_entry.get("pattern_name", "")
        if pn and pn not in existing.get("pattern_names", []):
            existing.setdefault("pattern_names", []).append(pn)

    def add_many(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Add multiple entries and return stats.

        Args:
            entries: List of endpoint dicts

        Returns:
            Dict with 'new' and 'merged' counts
        """
        new_count = 0
        merged_count = 0

        for entry in entries:
            if self.add(entry):
                new_count += 1
            else:
                merged_count += 1

        logger.info(f"Dedup: {new_count} new, {merged_count} merged, {len(self._seen)} total unique")
        return {"new": new_count, "merged": merged_count}

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all deduplicated results.

        Returns:
            Sorted list of merged endpoint records
        """
        results = list(self._seen.values())

        # Clean up empty values in lists
        for r in results:
            r["timestamps"] = [t for t in r.get("timestamps", []) if t]
            r["status_codes"] = [s for s in r.get("status_codes", []) if s]
            r["mime_types"] = [m for m in r.get("mime_types", []) if m]
            r["pattern_names"] = [p for p in r.get("pattern_names", []) if p]
            r["source_files"] = [f for f in r.get("source_files", []) if f]

        # Sort by URL
        results.sort(key=lambda x: x.get("normalized_url", ""))
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        results = self.get_results()
        total_occurrences = sum(r.get("occurrence_count", 1) for r in results)
        sources = set()
        for r in results:
            sources.update(r.get("sources", []))

        return {
            "unique_endpoints": len(results),
            "total_occurrences": total_occurrences,
            "dedup_ratio": round(1 - len(results) / max(total_occurrences, 1), 2),
            "sources": sorted(sources),
        }

    def clear(self):
        """Reset the dedup engine."""
        self._seen.clear()
