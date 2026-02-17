"""
Tests for GHOSTMAP Deduplication Engine.
"""

import pytest
from ghostmap.collector.dedup import DeduplicationEngine


@pytest.fixture
def dedup():
    return DeduplicationEngine()


class TestURLNormalization:
    """Test URL normalization logic."""

    def test_lowercase_scheme_and_host(self, dedup):
        assert dedup.normalize_url("HTTP://EXAMPLE.COM/path") == "http://example.com/path"

    def test_remove_trailing_slash(self, dedup):
        assert dedup.normalize_url("http://example.com/api/") == "http://example.com/api"

    def test_remove_fragment(self, dedup):
        result = dedup.normalize_url("http://example.com/api#section")
        assert "#" not in result

    def test_sort_query_params(self, dedup):
        result = dedup.normalize_url("http://example.com/api?z=1&a=2")
        assert result == "http://example.com/api?a=2&z=1"

    def test_remove_default_port_80(self, dedup):
        result = dedup.normalize_url("http://example.com:80/api")
        assert ":80" not in result

    def test_remove_default_port_443(self, dedup):
        result = dedup.normalize_url("https://example.com:443/api")
        assert ":443" not in result

    def test_keep_non_default_port(self, dedup):
        result = dedup.normalize_url("http://example.com:8080/api")
        assert ":8080" in result

    def test_relative_path(self, dedup):
        result = dedup.normalize_url("/api/v1/users/")
        assert result == "/api/v1/users"

    def test_empty_input(self, dedup):
        assert dedup.normalize_url("") == ""


class TestDeduplication:
    """Test the deduplication logic."""

    def test_new_entry_returns_true(self, dedup):
        assert dedup.add({"url": "http://example.com/api/v1"}) is True

    def test_duplicate_returns_false(self, dedup):
        dedup.add({"url": "http://example.com/api/v1"})
        assert dedup.add({"url": "http://example.com/api/v1"}) is False

    def test_normalized_duplicates_detected(self, dedup):
        dedup.add({"url": "HTTP://EXAMPLE.COM/api/v1/"})
        assert dedup.add({"url": "http://example.com/api/v1"}) is False

    def test_different_urls_both_added(self, dedup):
        assert dedup.add({"url": "/api/v1"}) is True
        assert dedup.add({"url": "/api/v2"}) is True

    def test_metadata_merging(self, dedup):
        dedup.add({"url": "/api/v1", "source": "wayback", "timestamp": "2023-01-01"})
        dedup.add({"url": "/api/v1", "source": "commoncrawl", "timestamp": "2024-01-01"})

        results = dedup.get_results()
        assert len(results) == 1
        assert "wayback" in results[0]["sources"]
        assert "commoncrawl" in results[0]["sources"]
        assert results[0]["occurrence_count"] == 2

    def test_add_many_returns_stats(self, dedup):
        entries = [
            {"url": "/api/v1"},
            {"url": "/api/v2"},
            {"url": "/api/v1"},  # duplicate
        ]
        stats = dedup.add_many(entries)
        assert stats["new"] == 2
        assert stats["merged"] == 1

    def test_get_results_sorted(self, dedup):
        dedup.add({"url": "/z/endpoint"})
        dedup.add({"url": "/a/endpoint"})
        results = dedup.get_results()
        assert results[0]["normalized_url"] < results[1]["normalized_url"]

    def test_get_stats(self, dedup):
        dedup.add({"url": "/api/v1", "source": "wayback"})
        dedup.add({"url": "/api/v1", "source": "commoncrawl"})
        dedup.add({"url": "/api/v2", "source": "wayback"})

        stats = dedup.get_stats()
        assert stats["unique_endpoints"] == 2
        assert stats["total_occurrences"] == 3

    def test_clear(self, dedup):
        dedup.add({"url": "/api/v1"})
        dedup.clear()
        assert dedup.get_results() == []
