"""
GHOSTMAP Risk Scorer — Calculate risk scores for discovered endpoints.
"""

import re
import logging
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urlparse

from ghostmap.utils.config import GhostMapConfig, DEFAULT_CONFIG

logger = logging.getLogger("ghostmap.auditor.risk_scorer")


class RiskScorer:
    """
    Scores each endpoint on a 0–100 risk scale based on:
    - Documentation status (is it a ghost?)
    - Active/live status
    - Sensitive keyword presence
    - Authentication status
    - Staleness / age indicators
    """

    def __init__(self, config: Optional[GhostMapConfig] = None):
        self.config = config or DEFAULT_CONFIG

    def score_all(
        self,
        endpoints: List[Dict[str, Any]],
        documented_endpoints: Optional[Set[str]] = None,
        probe_results: Optional[Dict[str, Dict]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Score all endpoints.

        Args:
            endpoints: List of endpoint dicts
            documented_endpoints: Set of known/documented endpoint paths
            probe_results: Dict of probe results keyed by path

        Returns:
            List of endpoints with risk_score, risk_level, and risk_factors added
        """
        documented = documented_endpoints or set()
        probes = probe_results or {}

        scored = []
        for ep in endpoints:
            scored_ep = self._score_one(ep, documented, probes)
            scored.append(scored_ep)

        # Sort by risk score descending
        scored.sort(key=lambda x: x.get("risk_score", 0), reverse=True)

        high = sum(1 for e in scored if e.get("risk_score", 0) >= 70)
        medium = sum(1 for e in scored if 40 <= e.get("risk_score", 0) < 70)
        low = sum(1 for e in scored if e.get("risk_score", 0) < 40)

        logger.info(f"Risk scoring: {high} high, {medium} medium, {low} low")
        return scored

    def _score_one(
        self,
        endpoint: Dict[str, Any],
        documented: Set[str],
        probes: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """Score a single endpoint."""
        ep = dict(endpoint)  # Don't mutate original

        url = ep.get("url") or ep.get("normalized_url") or ep.get("endpoint", "")
        path = self._extract_path(url)
        path_lower = path.lower()

        score = 0
        factors = []

        # --- Factor 1: Documentation Status (weight: 30) ---
        is_documented = self._is_documented(path, documented)
        if not is_documented:
            score += self.config.weight_undocumented
            factors.append({
                "factor": "undocumented",
                "points": self.config.weight_undocumented,
                "detail": "Endpoint not found in API documentation",
            })

        # --- Factor 2: Active Status (weight: 25) ---
        probe_data = probes.get(path, {})
        status_code = probe_data.get("status_code", 0)

        if status_code and 200 <= status_code < 300:
            score += self.config.weight_active
            factors.append({
                "factor": "active",
                "points": self.config.weight_active,
                "detail": f"Endpoint returns HTTP {status_code}",
            })
        elif status_code in (401, 403):
            # Auth required — slightly less risky but still alive
            score += self.config.weight_active * 0.6
            factors.append({
                "factor": "active_auth_required",
                "points": int(self.config.weight_active * 0.6),
                "detail": f"Endpoint requires auth (HTTP {status_code})",
            })

        # --- Factor 3: Sensitive Keywords (weight: 20) ---
        sensitive_found = []
        # Use word-boundary matching to avoid false hits
        # e.g. "dev" should match "/dev/" but NOT "/.dev/" (TLD) or "/devices/"
        # "temp" should match "/temp/" but NOT "/template/"
        # "old" should match "/old-api/" but NOT "/holdings/"
        for keyword in self.config.sensitive_keywords:
            # Build pattern: keyword must be bounded by non-alphanumeric chars
            pattern = r'(?:^|[/\-_\.])' + re.escape(keyword) + r'(?:$|[/\-_\.])'
            if re.search(pattern, path_lower):
                sensitive_found.append(keyword)

        if sensitive_found:
            # Scale by number of matches, cap at full weight
            keyword_score = min(
                len(sensitive_found) * (self.config.weight_sensitive_keywords // 2),
                self.config.weight_sensitive_keywords,
            )
            score += keyword_score
            factors.append({
                "factor": "sensitive_keywords",
                "points": keyword_score,
                "detail": f"Contains: {', '.join(sensitive_found)}",
            })

        # --- Factor 4: Authentication (weight: 15) ---
        if probe_data:
            # If endpoint is active and has NO auth indicators
            if status_code and 200 <= status_code < 300 and not probe_data.get("has_auth"):
                score += self.config.weight_no_auth
                factors.append({
                    "factor": "no_auth",
                    "points": self.config.weight_no_auth,
                    "detail": "Endpoint accessible without authentication",
                })

        # --- Factor 5: Debug/Admin Detection (weight: bonus 10) ---
        if probe_data.get("is_debug"):
            score += 10
            factors.append({
                "factor": "debug_endpoint",
                "points": 10,
                "detail": "Response contains debug/diagnostic information",
            })
        if probe_data.get("is_admin"):
            score += 10
            factors.append({
                "factor": "admin_endpoint",
                "points": 10,
                "detail": "Response appears to be an admin panel",
            })

        # --- Factor 6: Staleness (weight: 10) ---
        sources = ep.get("sources", [])
        timestamps = ep.get("timestamps", [])
        if sources and "wayback" in sources and len(sources) == 1:
            # Only found in historical archives, not recent crawls
            score += self.config.weight_staleness
            factors.append({
                "factor": "stale",
                "points": self.config.weight_staleness,
                "detail": "Only found in historical archives (potentially forgotten)",
            })

        # Cap at 100
        score = min(score, 100)

        # Determine risk level
        if score >= 70:
            risk_level = "HIGH"
            risk_color = "red"
        elif score >= 40:
            risk_level = "MEDIUM"
            risk_color = "yellow"
        else:
            risk_level = "LOW"
            risk_color = "green"

        ep["risk_score"] = score
        ep["risk_level"] = risk_level
        ep["risk_color"] = risk_color
        ep["risk_factors"] = factors
        ep["is_documented"] = is_documented
        ep["is_ghost"] = not is_documented and score >= 40

        if probe_data:
            ep["probe_status"] = status_code
            ep["is_active"] = 200 <= status_code < 300
            ep["is_soft_404"] = probe_data.get("is_soft_404", False)

        return ep

    def _is_documented(self, path: str, documented: Set[str]) -> bool:
        """Check if a path is in the documented set (with normalization)."""
        if not documented:
            return False

        normalized = self._normalize_for_comparison(path)
        for doc_path in documented:
            if self._normalize_for_comparison(doc_path) == normalized:
                return True
        return False

    @staticmethod
    def _normalize_for_comparison(path: str) -> str:
        """Normalize a path for fuzzy comparison."""
        path = path.strip().lower().rstrip("/")
        # Replace parameter placeholders
        path = re.sub(r"\{[^}]+\}", "{param}", path)
        path = re.sub(r":([a-zA-Z_]+)", "{param}", path)
        path = re.sub(r"/\d+(?=/|$)", "/{param}", path)
        return path

    @staticmethod
    def _extract_path(url: str) -> str:
        """Extract path from URL."""
        if not url:
            return ""
        if url.startswith(("http://", "https://")):
            return urlparse(url).path
        return url
