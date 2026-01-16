"""Tests for Dune API FastAPI endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestDuneEndpoints:
    """Test suite for Dune API endpoints."""

    @patch("fastAPI.duno.get_duno_client")
    def test_get_result_success(self, mock_get_client):
        """Test successful retrieval of Dune query result."""
        # Mock the DuneClient
        mock_dune = MagicMock()
        mock_get_client.return_value = mock_dune
        
        # Mock the query result
        mock_result = {
            "execution_id": "01K95SK6M52C8JR270VRV5XD1D",
            "state": "QUERY_STATE_COMPLETED",
            "rows": [
                {"wallet": "0x123", "balance": 1000}
            ]
        }
        mock_dune.get_latest_result.return_value = mock_result
        
        # Make request
        response = client.get("/dune/result/2350027")
        
        # Assertions
        assert response.status_code == 200
        assert response.json()["query_id"] == 2350027
        assert response.json()["status"] == "success"
        assert response.json()["result"] == mock_result
        mock_dune.get_latest_result.assert_called_once_with(2350027)

    @patch("fastAPI.duno.get_duno_client")
    def test_get_result_api_error(self, mock_get_client):
        """Test API error handling when query fails."""
        mock_dune = MagicMock()
        mock_get_client.return_value = mock_dune
        
        # Mock API error
        mock_dune.get_latest_result.side_effect = Exception("API Error: 402 Payment Required")
        
        # Make request
        response = client.get("/dune/result/2350027")
        
        # Assertions
        assert response.status_code == 400
        assert "Failed to get Dune query result" in response.json()["detail"]

    @patch("fastAPI.duno.__get_credentials")
    def test_credentials_missing(self, mock_get_creds):
        """Test error when API key is missing."""
        mock_get_creds.side_effect = RuntimeError("Failed to load DUNE_API_KEY from environment")
        
        # Make request
        response = client.get("/dune/result/2350027")
        
        # Assertions
        assert response.status_code == 400

    @patch("fastAPI.duno.get_duno_client")
    def test_get_result_invalid_query_id(self, mock_get_client):
        """Test error with invalid query ID."""
        mock_dune = MagicMock()
        mock_get_client.return_value = mock_dune
        
        # Mock not found error
        mock_dune.get_latest_result.side_effect = Exception("Query not found")
        
        # Make request
        response = client.get("/dune/result/999999999")
        
        # Assertions
        assert response.status_code == 400
        assert "Failed to get Dune query result" in response.json()["detail"]

    @patch("fastAPI.duno.get_duno_client")
    def test_get_result_with_empty_rows(self, mock_get_client):
        """Test successful retrieval with empty result set."""
        mock_dune = MagicMock()
        mock_get_client.return_value = mock_dune
        
        # Mock empty result
        mock_result = {
            "execution_id": "test_id",
            "state": "QUERY_STATE_COMPLETED",
            "rows": []
        }
        mock_dune.get_latest_result.return_value = mock_result
        
        # Make request
        response = client.get("/dune/result/1234567")
        
        # Assertions
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["result"]["rows"] == []


class TestDuneClientInitialization:
    """Test suite for DuneClient initialization."""

    @patch("fastAPI.duno.DuneClient")
    @patch("fastAPI.duno.__get_credentials")
    def test_client_initialization(self, mock_get_creds, mock_client_class):
        """Test DuneClient is initialized with correct API key."""
        from fastAPI.duno import get_duno_client
        
        mock_get_creds.return_value = "test_api_key_123"
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        client_instance = get_duno_client()
        
        # Assertions
        mock_client_class.assert_called_once_with("test_api_key_123")
        assert client_instance == mock_client_instance

    @patch("fastAPI.duno.os.getenv")
    @patch("fastAPI.duno.load_dotenv")
    def test_credentials_loading(self, mock_load_dotenv, mock_getenv):
        """Test credentials are loaded from environment."""
        from fastAPI.duno import __get_credentials
        
        mock_getenv.return_value = "valid_api_key"
        
        # Call the function
        api_key = __get_credentials()
        
        # Assertions
        mock_load_dotenv.assert_called_once()
        mock_getenv.assert_called_once_with("DUNE_API_KEY")
        assert api_key == "valid_api_key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
