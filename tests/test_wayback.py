"""
Tests for GHOSTMAP Wayback Machine Scraper.
"""

import json
import pytest
import responses
from ghostmap.collector.wayback import WaybackScraper, WAYBACK_CDX_URL


@pytest.fixture
def scraper():
    return WaybackScraper()


class TestWaybackScraper:
    """Test the Wayback Machine CDX API scraper."""

    @responses.activate
    def test_fetch_urls_basic(self, scraper):
        """Test basic URL fetching from Wayback CDX."""
        mock_data = [
            ["original", "timestamp", "statuscode", "mimetype"],
            ["https://example.com/api/v1/users", "20230101120000", "200", "text/html"],
            ["https://example.com/api/v1/products", "20230201120000", "200", "application/json"],
        ]

        responses.add(
            responses.GET,
            WAYBACK_CDX_URL,
            json=mock_data,
            status=200,
        )
        # Add empty response for page 1 to stop pagination
        responses.add(
            responses.GET,
            WAYBACK_CDX_URL,
            json=[],
            status=200,
        )

        results = scraper.fetch_urls("example.com")
        assert len(results) == 2
        assert results[0]["url"] == "https://example.com/api/v1/users"
        assert results[0]["source"] == "wayback"

    @responses.activate
    def test_fetch_urls_empty_response(self, scraper):
        """Test handling of empty CDX response."""
        responses.add(
            responses.GET,
            WAYBACK_CDX_URL,
            json=[],
            status=200,
        )

        results = scraper.fetch_urls("nonexistent.com")
        assert results == []

    @responses.activate
    def test_extract_api_urls(self, scraper):
        """Test API URL filtering."""
        urls = [
            {"url": "https://example.com/api/v1/users", "status_code": "200"},
            {"url": "https://example.com/index.html", "status_code": "200"},
            {"url": "https://example.com/swagger/docs", "status_code": "200"},
            {"url": "https://example.com/about", "status_code": "200"},
        ]

        api_urls = scraper.extract_api_urls(urls)
        assert len(api_urls) == 2
        assert any("/api/" in u["url"] for u in api_urls)
        assert any("/swagger" in u["url"] for u in api_urls)

    @responses.activate
    def test_extract_js_urls(self, scraper):
        """Test JS URL extraction."""
        urls = [
            {"url": "https://example.com/static/app.js"},
            {"url": "https://example.com/bundle.min.js?v=123"},
            {"url": "https://example.com/api/data"},
            {"url": "https://example.com/module.mjs"},
        ]

        js_urls = scraper.extract_js_urls(urls)
        assert len(js_urls) == 3
        assert "https://example.com/static/app.js" in js_urls
        assert "https://example.com/module.mjs" in js_urls

    @responses.activate
    def test_fetch_urls_with_callback(self, scraper):
        """Test that progress callback is invoked."""
        mock_data = [
            ["original", "timestamp", "statuscode", "mimetype"],
            ["https://example.com/api/v1", "20230101", "200", "text/html"],
        ]
        responses.add(responses.GET, WAYBACK_CDX_URL, json=mock_data, status=200)
        responses.add(responses.GET, WAYBACK_CDX_URL, json=[], status=200)

        callback_calls = []
        def callback(batch, total):
            callback_calls.append((batch, total))

        scraper.fetch_urls("example.com", callback=callback)
        assert len(callback_calls) > 0

    @responses.activate
    def test_fetch_urls_handles_error(self, scraper):
        """Test graceful handling of HTTP errors."""
        responses.add(
            responses.GET,
            WAYBACK_CDX_URL,
            status=500,
        )

        results = scraper.fetch_urls("example.com")
        assert results == []
