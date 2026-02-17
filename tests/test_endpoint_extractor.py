"""
Tests for GHOSTMAP Endpoint Extractor.
"""

import pytest
from ghostmap.collector.endpoint_extractor import EndpointExtractor


@pytest.fixture
def extractor():
    return EndpointExtractor()


class TestEndpointExtractor:
    """Test the regex-based endpoint extraction engine."""

    def test_extract_rest_api_paths(self, extractor):
        text = '''
        const url = "/api/v1/users";
        const another = '/api/v2/products/list';
        fetch("/api/v3/orders");
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/v1/users" in endpoints
        assert "/api/v2/products/list" in endpoints
        assert "/api/v3/orders" in endpoints

    def test_extract_fetch_calls(self, extractor):
        text = '''
        fetch('/api/data');
        fetch("/users/profile");
        fetch('/v1/orders/create');
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/data" in endpoints
        assert "/users/profile" in endpoints

    def test_extract_axios_calls(self, extractor):
        text = '''
        axios.get('/api/users');
        axios.post('/api/orders', data);
        axios.delete('/api/items/123');
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/users" in endpoints
        assert "/api/orders" in endpoints

    def test_extract_xhr_calls(self, extractor):
        text = '''
        xhr.open('GET', '/api/data');
        xhr.open('POST', '/api/submit');
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/data" in endpoints
        assert "/api/submit" in endpoints

    def test_extract_express_routes(self, extractor):
        text = '''
        app.get('/api/health', handler);
        router.post('/api/users/create', createUser);
        app.delete('/api/sessions/:id', deleteSession);
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/health" in endpoints
        assert "/api/users/create" in endpoints

    def test_extract_jquery_ajax(self, extractor):
        text = '''
        $.ajax('/api/data');
        $.getJSON('/api/config');
        $.post('/api/submit');
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/api/data" in endpoints
        assert "/api/config" in endpoints

    def test_extract_absolute_urls(self, extractor):
        text = '''
        const api = "https://example.com/api/v1/users";
        const ws = "wss://example.com/ws/notifications";
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert any("example.com/api/v1/users" in e for e in endpoints)

    def test_exclude_static_assets(self, extractor):
        text = '''
        const img = "/images/logo.png";
        const css = "/static/style.css";
        const api = "/api/data";
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert not any(".png" in e for e in endpoints)
        assert not any(".css" in e for e in endpoints)
        assert "/api/data" in endpoints

    def test_domain_filter(self, extractor):
        text = '''
        const a = "https://example.com/api/data";
        const b = "https://other.com/api/data";
        const c = "/api/local";
        '''
        endpoints = extractor.extract_endpoints_only(text, base_domain="example.com")
        # Relative paths always match
        assert "/api/local" in endpoints
        # example.com should match
        assert any("example.com" in e for e in endpoints)

    def test_graphql_endpoints(self, extractor):
        text = '''
        const gql = "/graphql";
        const gql2 = "/graphql/v2";
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert "/graphql" in endpoints

    def test_empty_input(self, extractor):
        endpoints = extractor.extract_endpoints_only("")
        assert endpoints == []

    def test_deduplication(self, extractor):
        text = '''
        fetch('/api/data');
        fetch('/api/data');
        fetch('/api/data');
        '''
        endpoints = extractor.extract_endpoints_only(text)
        assert endpoints.count("/api/data") == 1


class TestEndpointExtractorMetadata:
    """Test metadata returned by extract()."""

    def test_extract_returns_pattern_names(self, extractor):
        text = '''fetch('/api/users');'''
        results = extractor.extract(text)
        assert len(results) > 0
        assert all("pattern_name" in r for r in results)
        assert all("endpoint" in r for r in results)
