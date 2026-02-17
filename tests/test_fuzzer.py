import pytest
from unittest.mock import MagicMock, patch
from ghostmap.auditor.fuzzer import GhostFuzzer
from ghostmap.utils.config import GhostMapConfig

@pytest.fixture
def config():
    return GhostMapConfig()

@patch("ghostmap.auditor.fuzzer.RateLimitedClient")
@patch("ghostmap.auditor.fuzzer.TechDetector")
def test_fuzzer_auto_spring(mock_detector_cls, mock_client_cls, config):
    # Setup TechDetector mock
    mock_detector = mock_detector_cls.return_value
    mock_detector.detect.return_value = ["spring"]
    
    # Setup HTTP Client mock
    mock_client = mock_client_cls.return_value
    mock_client.__enter__.return_value = mock_client
    
    # Response mock
    mock_response_found = MagicMock()
    mock_response_found.status_code = 200
    
    mock_response_404 = MagicMock()
    mock_response_404.status_code = 404
    
    # Side effect: /actuator found, others 404
    def side_effect(url, **kwargs):
        if "actuator" in url:
            return mock_response_found
        return mock_response_404
    
    mock_client.get.side_effect = side_effect
    
    fuzzer = GhostFuzzer(config)
    results = fuzzer.fuzz("http://example.com", mode="auto")
    
    # Should find actuator (from SPRING list)
    assert len(results) > 0
    found_paths = [r["endpoint"] for r in results]
    assert any("actuator" in p for p in found_paths)
    
    # Should NOT find phpinfo (from PHP list)
    assert not any("phpinfo" in p for p in found_paths)

@patch("ghostmap.auditor.fuzzer.RateLimitedClient")
def test_fuzzer_all_mode(mock_client_cls, config):
    # Setup HTTP Client mock
    mock_client = mock_client_cls.return_value
    mock_client.__enter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_client.get.return_value = mock_response
    
    fuzzer = GhostFuzzer(config)
    results = fuzzer.fuzz("http://example.com", mode="all")
    
    # Even if nothing found, we should see that it tried many URLs (implied by execution)
    # Here we just verify it runs without error
    assert results == []
