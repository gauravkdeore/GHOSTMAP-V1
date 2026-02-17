"""
Tests for GHOSTMAP Risk Scorer.
"""

import pytest
from ghostmap.auditor.risk_scorer import RiskScorer
from ghostmap.utils.config import GhostMapConfig


@pytest.fixture
def scorer():
    return RiskScorer()


class TestRiskScorer:
    """Test the risk scoring algorithm."""

    def test_undocumented_endpoint_scores_higher(self, scorer):
        endpoints = [{"url": "/api/debug", "sources": ["wayback"]}]
        # Not in documented set = ghost
        results = scorer.score_all(endpoints, documented_endpoints=set())
        assert results[0]["risk_score"] > 0
        assert not results[0]["is_documented"]

    def test_documented_endpoint_scores_lower(self, scorer):
        endpoints = [{"url": "/api/users", "sources": ["wayback"]}]
        documented = {"/api/users"}
        results = scorer.score_all(endpoints, documented_endpoints=documented)
        assert results[0]["is_documented"] is True

    def test_sensitive_keywords_add_score(self, scorer):
        endpoints = [
            {"url": "/api/users"},
            {"url": "/api/debug/admin"},
        ]
        results = scorer.score_all(endpoints)
        debug_ep = next(r for r in results if "debug" in r["url"])
        normal_ep = next(r for r in results if "users" in r["url"])
        assert debug_ep["risk_score"] > normal_ep["risk_score"]

    def test_active_endpoint_adds_score(self, scorer):
        endpoints = [{"url": "/api/data"}]
        probe_results = {
            "/api/data": {"status_code": 200, "has_auth": False}
        }
        results = scorer.score_all(
            endpoints,
            probe_results=probe_results,
        )
        assert results[0]["risk_score"] > 0

    def test_high_risk_classification(self, scorer):
        # Undocumented + active + sensitive keyword + no auth = very high
        endpoints = [{"url": "/api/admin/debug", "sources": ["wayback"]}]
        probe_results = {
            "/api/admin/debug": {
                "status_code": 200,
                "has_auth": False,
                "is_debug": True,
            }
        }
        results = scorer.score_all(
            endpoints,
            documented_endpoints=set(),
            probe_results=probe_results,
        )
        assert results[0]["risk_level"] == "HIGH"
        assert results[0]["risk_score"] >= 70

    def test_low_risk_documented_endpoint(self, scorer):
        endpoints = [{"url": "/api/users"}]
        documented = {"/api/users"}
        results = scorer.score_all(endpoints, documented_endpoints=documented)
        assert results[0]["risk_level"] == "LOW"
        assert results[0]["risk_score"] < 40

    def test_score_capped_at_100(self, scorer):
        # Create worst case scenario
        endpoints = [{"url": "/api/admin/debug/internal/secret", "sources": ["wayback"]}]
        probe_results = {
            "/api/admin/debug/internal/secret": {
                "status_code": 200,
                "has_auth": False,
                "is_debug": True,
                "is_admin": True,
            }
        }
        results = scorer.score_all(
            endpoints,
            documented_endpoints=set(),
            probe_results=probe_results,
        )
        assert results[0]["risk_score"] <= 100

    def test_risk_factors_populated(self, scorer):
        endpoints = [{"url": "/api/debug"}]
        results = scorer.score_all(endpoints)
        assert "risk_factors" in results[0]
        assert isinstance(results[0]["risk_factors"], list)
        for factor in results[0]["risk_factors"]:
            assert "factor" in factor
            assert "points" in factor
            assert "detail" in factor

    def test_results_sorted_by_score(self, scorer):
        endpoints = [
            {"url": "/api/users"},
            {"url": "/api/admin/debug"},
            {"url": "/api/health"},
        ]
        results = scorer.score_all(endpoints)
        scores = [r["risk_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_stale_endpoint_adds_score(self, scorer):
        endpoints = [
            {"url": "/api/old", "sources": ["wayback"]},
            {"url": "/api/new", "sources": ["wayback", "commoncrawl"]},
        ]
        results = scorer.score_all(endpoints)
        stale = next(r for r in results if "old" in r["url"])
        fresh = next(r for r in results if "new" in r["url"])
        assert stale["risk_score"] >= fresh["risk_score"]

    def test_parameter_normalization_for_documented_match(self, scorer):
        endpoints = [{"url": "/api/users/123"}]
        documented = {"/api/users/{id}"}
        results = scorer.score_all(endpoints, documented_endpoints=documented)
        assert results[0]["is_documented"] is True

    def test_empty_endpoints(self, scorer):
        results = scorer.score_all([])
        assert results == []
