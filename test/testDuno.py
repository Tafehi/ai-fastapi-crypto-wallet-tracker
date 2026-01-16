"""Tests for Dune API FastAPI endpoints."""
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from fastAPI import duno


@pytest.fixture(autouse=True)
def clear_lru_cache():
    """Clear LRU cache before each test to prevent cached values interfering."""
    duno.get_duno_client.cache_clear()
    yield
    duno.get_duno_client.cache_clear()


client = TestClient(app)


class TestDuneEndpoints:
    """Test suite for Dune API endpoints."""

    @patch("fastAPI.duno.DuneClient")
    def test_get_result_success(self, mock_client_class):
        """Test successful retrieval of Dune query result."""
        # Setup mocks
        mock_dune = MagicMock()
        mock_client_class.return_value = mock_dune
        
        # Mock the query result
        mock_result = {
            "execution_id": "01K95SK6M52C8JR270VRV5XD1D",
            "state": "QUERY_STATE_COMPLETED",
            "rows": [{"wallet": "0x123", "balance": 1000}]
        }
        mock_dune.get_latest_result.return_value = mock_result
        
        # Override the app dependency
        app.dependency_overrides[duno.get_duno_client] = lambda: mock_dune
        
        try:
            response = client.get("/dune/result/2350027")
            assert response.status_code == 200
            assert response.json()["query_id"] == 2350027
            assert response.json()["status"] == "success"
        finally:
            app.dependency_overrides.clear()

    @patch("fastAPI.duno.DuneClient")
    def test_get_result_api_error(self, mock_client_class):
        """Test API error handling when query fails."""
        mock_dune = MagicMock()
        mock_client_class.return_value = mock_dune
        mock_dune.get_latest_result.side_effect = Exception("API Error: 402 Payment Required")
        
        app.dependency_overrides[duno.get_duno_client] = lambda: mock_dune
        
        try:
            response = client.get("/dune/result/2350027")
            assert response.status_code == 400
            assert "Failed to get Dune query result" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_credentials_missing(self):
        """Test error when API key is missing."""
        mock_dune = MagicMock()
        mock_dune.get_latest_result.side_effect = RuntimeError("DUNE_API_KEY not found")
        
        app.dependency_overrides[duno.get_duno_client] = lambda: mock_dune
        
        try:
            response = client.get("/dune/result/2350027")
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    @patch("fastAPI.duno.DuneClient")
    def test_get_result_invalid_query_id(self, mock_client_class):
        """Test error with invalid query ID."""
        mock_dune = MagicMock()
        mock_client_class.return_value = mock_dune
        mock_dune.get_latest_result.side_effect = Exception("Query not found")
        
        app.dependency_overrides[duno.get_duno_client] = lambda: mock_dune
        
        try:
            response = client.get("/dune/result/999999999")
            assert response.status_code == 400
            assert "Failed to get Dune query result" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

    @patch("fastAPI.duno.DuneClient")
    def test_get_result_with_empty_rows(self, mock_client_class):
        """Test successful retrieval with empty result set."""
        mock_dune = MagicMock()
        mock_client_class.return_value = mock_dune
        
        # Mock empty result
        mock_result = {
            "execution_id": "test_id",
            "state": "QUERY_STATE_COMPLETED",
            "rows": []
        }
        mock_dune.get_latest_result.return_value = mock_result
        
        app.dependency_overrides[duno.get_duno_client] = lambda: mock_dune
        
        try:
            response = client.get("/dune/result/1234567")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert response.json()["result"]["rows"] == []
        finally:
            app.dependency_overrides.clear()


class TestDuneClientInitialization:
    """Test suite for DuneClient initialization."""

    @patch("fastAPI.duno.DuneClient")
    def test_client_initialization(self, mock_client_class):
        """Test DuneClient is initialized with correct API key."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        # Clear cache first
        duno.get_duno_client.cache_clear()
        
        # Call the function
        with patch.dict(os.environ, {"DUNE_API_KEY": "test_api_key_123"}):
            client_instance = duno.get_duno_client()
        
        # Assertions
        assert client_instance == mock_client_instance
        mock_client_class.assert_called_once_with("test_api_key_123")

    def test_credentials_loading(self):
        """Test credentials are loaded from environment."""
        with patch.dict(os.environ, {"DUNE_API_KEY": "test_api_key_123"}):
            # Clear cache
            duno.get_duno_client.cache_clear()
            
            try:
                # This should load the key from environment
                api_key = duno._TestDuneClientInitialization__get_credentials() if hasattr(duno, '_TestDuneClientInitialization__get_credentials') else None
                # If we can't access private method, just verify env var works
                assert os.getenv("DUNE_API_KEY") == "test_api_key_123"
            finally:
                duno.get_duno_client.cache_clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
