import pytest
from unittest.mock import MagicMock, patch
from ghostmap.auditor.tech_detector import TechDetector

@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.headers = {}
    resp.text = ""
    return resp

@patch("ghostmap.auditor.tech_detector.requests.get")
def test_detect_spring(mock_get, mock_response):
    mock_response.text = "Whitelabel Error Page"
    mock_get.return_value = mock_response
    
    detector = TechDetector()
    tags = detector.detect("http://example.com")
    
    assert "spring" in tags
    assert "common" in tags

@patch("ghostmap.auditor.tech_detector.requests.get")
def test_detect_php_headers(mock_get, mock_response):
    mock_response.headers = {"X-Powered-By": "PHP/7.4"}
    mock_get.return_value = mock_response
    
    detector = TechDetector()
    tags = detector.detect("http://example.com")
    
    assert "php" in tags

@patch("ghostmap.auditor.tech_detector.requests.get")
def test_detect_django_cookies(mock_get, mock_response):
    mock_response.headers = {"Set-Cookie": "csrftoken=xyz; Path=/"}
    mock_get.return_value = mock_response
    
    detector = TechDetector()
    tags = detector.detect("http://example.com")
    
    assert "django" in tags
