"""
Tests for GHOSTMAP Swagger/OpenAPI Comparator.
"""

import json
import os
import tempfile
import pytest
from ghostmap.auditor.swagger_compare import SwaggerComparator


@pytest.fixture
def comparator():
    return SwaggerComparator()


@pytest.fixture
def sample_spec():
    """Create a temporary OpenAPI spec file."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://api.example.com/v1"}],
        "paths": {
            "/users": {"get": {"summary": "List users"}},
            "/users/{id}": {"get": {"summary": "Get user"}},
            "/products": {"get": {"summary": "List products"}},
            "/orders": {"post": {"summary": "Create order"}},
        },
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(spec, f)
        return f.name


class TestSwaggerComparator:
    """Test the Swagger/OpenAPI comparison engine."""

    def test_load_spec(self, comparator, sample_spec):
        endpoints = comparator.load_spec(sample_spec)
        assert len(endpoints) == 4
        os.unlink(sample_spec)

    def test_load_spec_with_base_path(self, comparator, sample_spec):
        endpoints = comparator.load_spec(sample_spec)
        # Should include base path from servers
        assert any("/v1/users" in e for e in endpoints)
        os.unlink(sample_spec)

    def test_compare_finds_ghosts(self, comparator, sample_spec):
        comparator.load_spec(sample_spec)

        collected = [
            {"url": "/v1/users"},
            {"url": "/v1/admin/debug"},      # Ghost!
            {"url": "/v1/internal/metrics"},  # Ghost!
        ]

        result = comparator.compare(collected)
        assert result["stats"]["ghost_count"] >= 2
        assert len(result["ghost"]) >= 2
        os.unlink(sample_spec)

    def test_compare_finds_documented(self, comparator, sample_spec):
        comparator.load_spec(sample_spec)

        collected = [
            {"url": "/v1/users"},
            {"url": "/v1/products"},
        ]

        result = comparator.compare(collected)
        assert result["stats"]["documented_found"] == 2
        os.unlink(sample_spec)

    def test_compare_finds_spec_only(self, comparator, sample_spec):
        comparator.load_spec(sample_spec)

        collected = [{"url": "/v1/users"}]

        result = comparator.compare(collected)
        # /products, /users/{id}, /orders are documented but not collected
        assert result["stats"]["spec_only_count"] >= 2
        os.unlink(sample_spec)

    def test_parameter_normalization(self, comparator, sample_spec):
        comparator.load_spec(sample_spec)

        # /users/123 should match /users/{id} in the spec
        collected = [{"url": "/v1/users/123"}]
        result = comparator.compare(collected)
        assert result["stats"]["documented_found"] >= 1
        os.unlink(sample_spec)

    def test_nonexistent_spec_file(self, comparator):
        endpoints = comparator.load_spec("/nonexistent/file.json")
        assert endpoints == set()

    def test_get_spec_details(self, comparator, sample_spec):
        comparator.load_spec(sample_spec)
        details = comparator.get_spec_details()
        assert details["title"] == "Test API"
        assert details["version"] == "1.0.0"
        assert details["endpoint_count"] == 4
        os.unlink(sample_spec)
