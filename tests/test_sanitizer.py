"""
Tests for GHOSTMAP Sanitizer.
"""

import pytest
from ghostmap.sanitizer.sanitizer import FootprintSanitizer


@pytest.fixture
def sanitizer():
    return FootprintSanitizer()


@pytest.fixture
def strict_sanitizer():
    return FootprintSanitizer(strict=True)


@pytest.fixture
def sample_data():
    return {
        "meta": {"tool": "ghostmap", "version": "1.0.0"},
        "endpoints": [
            {
                "url": "https://example.com/api/v1/users?token=abc123&email=test@test.com",
                "sources": ["wayback"],
            },
            {
                "url": "https://example.com/api/v1/health",
                "sources": ["commoncrawl"],
            },
            {
                "url": "https://example.com/api/debug?session_id=sess_xyz789",
                "sources": ["wayback"],
            },
        ],
    }


class TestSanitizer:
    """Test the sanitization engine."""

    def test_sanitize_removes_tokens(self, sanitizer, sample_data):
        result = sanitizer.sanitize(sample_data)
        endpoints = result["endpoints"]
        # Token param should be removed
        for ep in endpoints:
            assert "token=abc123" not in ep.get("url", "")

    def test_sanitize_removes_emails(self, sanitizer):
        data = {
            "endpoints": [
                {"url": "https://example.com/api?q=admin@company.com"},
            ]
        }
        result = sanitizer.sanitize(data)
        report = sanitizer.get_report()
        assert report["emails_removed"] > 0

    def test_sanitize_jwt_tokens(self, sanitizer):
        data = {
            "endpoints": [
                {
                    "url": "/api/data",
                    "extra": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456",
                },
            ]
        }
        result = sanitizer.sanitize(data)
        assert "eyJ" not in str(result)

    def test_sanitize_aws_keys(self, sanitizer):
        data = {
            "endpoints": [
                {"url": "/api/data", "extra": "key=AKIAIOSFODNN7EXAMPLE"},
            ]
        }
        result = sanitizer.sanitize(data)
        assert "AKIAIOSFODNN7EXAMPLE" not in str(result)

    def test_strict_mode_strips_all_query_values(self, strict_sanitizer):
        data = {
            "endpoints": [
                {"url": "https://example.com/api?page=1&limit=10"},
            ]
        }
        result = strict_sanitizer.sanitize(data)
        url = result["endpoints"][0]["url"]
        assert "REDACTED" in url or "page=1" not in url

    def test_strict_mode_removes_internal_ips(self, strict_sanitizer):
        data = {
            "endpoints": [
                {"url": "/api/data", "extra": "host=192.168.1.100"},
            ]
        }
        result = strict_sanitizer.sanitize(data)
        assert "192.168.1.100" not in str(result)

    def test_suspicious_pattern_detection(self, sanitizer):
        data = {
            "endpoints": [
                {"url": "https://example.com/api?q=1 UNION SELECT * FROM users"},
            ]
        }
        result = sanitizer.sanitize(data)
        report = sanitizer.get_report()
        assert report["suspicious_patterns"] > 0

    def test_sanitize_preserves_structure(self, sanitizer, sample_data):
        result = sanitizer.sanitize(sample_data)
        assert "meta" in result
        assert "endpoints" in result
        assert isinstance(result["endpoints"], list)
        assert result["meta"]["sanitized"] is True

    def test_sanitize_session_ids(self, sanitizer, sample_data):
        result = sanitizer.sanitize(sample_data)
        for ep in result["endpoints"]:
            assert "session_id=sess_xyz789" not in ep.get("url", "")

    def test_json_validation(self, sanitizer, sample_data):
        result = sanitizer.sanitize(sample_data)
        assert sanitizer.validate_json(result) is True

    def test_report_counts(self, sanitizer, sample_data):
        sanitizer.sanitize(sample_data)
        report = sanitizer.get_report()
        assert report["total_processed"] == 3

    def test_empty_data(self, sanitizer):
        result = sanitizer.sanitize({"endpoints": []})
        assert result["endpoints"] == []
