"""
GHOSTMAP Swagger/OpenAPI Comparator — Compare collected endpoints against API specs.
"""

import json
import logging
import os
from typing import List, Dict, Any, Set, Optional

import yaml

logger = logging.getLogger("ghostmap.auditor.swagger_compare")


class SwaggerComparator:
    """
    Loads OpenAPI/Swagger specification files and compares documented
    endpoints against a collected footprint to identify ghost endpoints.
    """

    def __init__(self):
        self._spec_endpoints: Set[str] = set()
        self._spec_data: Optional[Dict] = None

    def load_spec(self, spec_path: str) -> Set[str]:
        """
        Load an OpenAPI/Swagger spec and extract documented endpoints.

        Args:
            spec_path: Path to the spec file (JSON or YAML)

        Returns:
            Set of documented endpoint paths
        """
        if not os.path.isfile(spec_path):
            logger.error(f"Spec file not found: {spec_path}")
            return set()

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                if spec_path.endswith((".yaml", ".yml")):
                    self._spec_data = yaml.safe_load(f)
                else:
                    self._spec_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse spec file: {e}")
            return set()

        self._spec_endpoints = self._extract_paths()
        logger.info(f"Loaded {len(self._spec_endpoints)} endpoints from {spec_path}")
        return self._spec_endpoints

    def _extract_paths(self) -> Set[str]:
        """Extract all endpoint paths from the loaded spec."""
        if not self._spec_data:
            return set()

        paths = set()
        spec_paths = self._spec_data.get("paths", {})

        # Handle OpenAPI 3.x base path via servers
        base_path = ""
        if "servers" in self._spec_data:
            servers = self._spec_data["servers"]
            if servers and isinstance(servers, list):
                from urllib.parse import urlparse
                server_url = servers[0].get("url", "")
                parsed = urlparse(server_url)
                base_path = parsed.path.rstrip("/")

        # Handle Swagger 2.0 basePath
        if "basePath" in self._spec_data:
            base_path = self._spec_data["basePath"].rstrip("/")

        for path_key in spec_paths:
            full_path = base_path + path_key if base_path else path_key
            normalized = self._normalize_path(full_path)
            paths.add(normalized)

        return paths

    def compare(
        self,
        collected_endpoints: List[Dict[str, Any]],
        documented: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare collected endpoints with documented ones.

        Args:
            collected_endpoints: List of endpoint dicts from the footprint
            documented: Set of documented endpoint paths (uses loaded spec if None)

        Returns:
            Dict with:
                - ghost: endpoints found in collection but NOT in docs (highest risk)
                - documented: endpoints found in both
                - undocumented: endpoints in docs but NOT in collection
                - stats: comparison statistics
        """
        documented = documented or self._spec_endpoints

        # Normalize all collected endpoints
        collected_paths = {}
        for ep in collected_endpoints:
            url = ep.get("url") or ep.get("normalized_url") or ep.get("endpoint", "")
            normalized = self._normalize_path(self._extract_path(url))
            if normalized:
                collected_paths[normalized] = ep

        collected_set = set(collected_paths.keys())
        documented_normalized = {self._normalize_path(p) for p in documented}

        # Find ghosts: in collection but NOT in docs
        ghost_paths = collected_set - documented_normalized
        # Found in both
        documented_found = collected_set & documented_normalized
        # In docs but not in collection
        undocumented_paths = documented_normalized - collected_set

        result = {
            "ghost": [
                {**collected_paths[p], "classification": "ghost"}
                for p in sorted(ghost_paths) if p in collected_paths
            ],
            "documented": [
                {**collected_paths[p], "classification": "documented"}
                for p in sorted(documented_found) if p in collected_paths
            ],
            "undocumented": [
                {"endpoint": p, "classification": "spec_only"}
                for p in sorted(undocumented_paths)
            ],
            "stats": {
                "total_collected": len(collected_set),
                "total_documented": len(documented_normalized),
                "ghost_count": len(ghost_paths),
                "documented_found": len(documented_found),
                "spec_only_count": len(undocumented_paths),
            },
        }

        logger.info(
            f"Comparison: {len(ghost_paths)} ghost, "
            f"{len(documented_found)} documented, "
            f"{len(undocumented_paths)} spec-only"
        )
        return result

    @staticmethod
    def _extract_path(url: str) -> str:
        """Extract path from a URL string."""
        if not url:
            return ""
        if url.startswith(("http://", "https://")):
            from urllib.parse import urlparse
            return urlparse(url).path
        return url

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize a path for comparison:
        - Lowercase
        - Strip trailing slash
        - Replace path parameters with a generic placeholder
        """
        if not path:
            return ""

        path = path.strip().lower().rstrip("/")

        # Replace common parameter patterns with {param}
        import re
        # {id}, {user_id}, etc.
        path = re.sub(r"\{[^}]+\}", "{param}", path)
        # :id, :user_id
        path = re.sub(r":([a-zA-Z_]+)", "{param}", path)
        # Numeric path segments that are likely IDs
        path = re.sub(r"/\d+(?=/|$)", "/{param}", path)

        return path or "/"

    def get_spec_details(self) -> Dict[str, Any]:
        """Get details about the loaded spec."""
        if not self._spec_data:
            return {}

        return {
            "title": self._spec_data.get("info", {}).get("title", "Unknown"),
            "version": self._spec_data.get("info", {}).get("version", "Unknown"),
            "endpoint_count": len(self._spec_endpoints),
            "endpoints": sorted(self._spec_endpoints),
        }
