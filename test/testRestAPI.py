import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path

# Add fastAPI directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "fastAPI"))

from RestAPI import app, TokenIn, Link

client = TestClient(app)


class TestTokenEndpoint:
    """Test suite for POST /tokens/ endpoint"""
    
    def test_create_token_success(self):
        """Test successful token creation"""
        token_data = {
            "url": "https://example.com",
            "chainId": "solana",
            "tokenAddress": "EPjFWaLb3hyccqJ1yckorbQnjsd4j6TSKiUvNrYzLT7",
            "icon": "https://example.com/icon.png",
            "header": "https://example.com/header.png",
            "description": "USDC Token",
            "links": [
                {
                    "type": "website",
                    "label": "Website",
                    "url": "https://www.circle.com"
                },
                {
                    "type": "twitter",
                    "label": "Twitter",
                    "url": "https://twitter.com/circle"
                }
            ]
        }
        
        response = client.post("/tokens/", json=token_data)
        
        assert response.status_code == 200
        assert response.json()["chainId"] == "solana"
        assert response.json()["tokenAddress"] == "EPjFWaLb3hyccqJ1yckorbQnjsd4j6TSKiUvNrYzLT7"
        assert len(response.json()["links"]) == 2
    
    def test_create_token_missing_fields(self):
        """Test token creation with missing required fields"""
        token_data = {
            "url": "https://example.com",
            "chainId": "solana"
            # Missing other required fields
        }
        
        response = client.post("/tokens/", json=token_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_token_invalid_url(self):
        """Test token creation with invalid URL"""
        token_data = {
            "url": "not-a-url",
            "chainId": "solana",
            "tokenAddress": "test",
            "icon": "not-a-url",
            "header": "not-a-url",
            "description": "test",
            "links": []
        }
        
        response = client.post("/tokens/", json=token_data)
        assert response.status_code == 422  # Validation error


class TestBirdeyePriceEndpoint:
    """Test suite for GET /birdeye/price endpoint"""
    
    @patch("httpx.AsyncClient.get")
    def test_get_token_price_success(self, mock_get):
        """Test successful price fetch"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "address": "EPjFWaLb3hyccqJ1yckorbQnjsd4j6TSKiUvNrYzLT7",
            "price": 1.00,
            "liquidity": 1000000,
            "priceChange24h": 0.5
        })
        
        mock_get.return_value = mock_response
        
        response = client.get(
            "/birdeye/price",
            params={
                "address": "EPjFWaLb3hyccqJ1yckorbQnjsd4j6TSKiUvNrYzLT7",
                "api_key": "test_key"
            }
        )
        
        assert response.status_code == 200
    
    def test_get_token_price_missing_params(self):
        """Test price endpoint without required parameters"""
        response = client.get("/birdeye/price")
        assert response.status_code == 422  # Missing required parameters
    
    @patch("httpx.AsyncClient.get")
    def test_get_token_price_api_error(self, mock_get):
        """Test price endpoint API error handling"""
        mock_response = AsyncMock()
        mock_response.status_code = 401  # Unauthorized
        
        mock_get.return_value = mock_response
        
        response = client.get(
            "/birdeye/price",
            params={
                "address": "EPjFWaLb3hyccqJ1yckorbQnjsd4j6TSKiUvNrYzLT7",
                "api_key": "invalid_key"
            }
        )
        
        assert response.status_code == 200  # Our endpoint returns 200 with error message
        assert "error" in response.json()


class TestBirdeyeGainersEndpoint:
    """Test suite for GET /birdeye/trader-board/gainers endpoint"""
    
    @patch("httpx.AsyncClient.get")
    def test_get_gainers_success(self, mock_get):
        """Test successful gainers fetch"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "data": [
                {
                    "address": "token1",
                    "symbol": "TOK1",
                    "price": 0.50,
                    "priceChange24h": 150.0
                },
                {
                    "address": "token2",
                    "symbol": "TOK2",
                    "price": 0.25,
                    "priceChange24h": 120.0
                }
            ]
        })
        
        mock_get.return_value = mock_response
        
        response = client.get(
            "/birdeye/trader-board/gainers",
            params={"api_key": "test_key"}
        )
        
        assert response.status_code == 200
    
    def test_get_gainers_missing_api_key(self):
        """Test gainers endpoint without API key"""
        response = client.get("/birdeye/trader-board/gainers")
        assert response.status_code == 422  # Missing required parameter
    
    @patch("httpx.AsyncClient.get")
    def test_get_gainers_custom_params(self, mock_get):
        """Test gainers endpoint with custom parameters"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"data": []})
        
        mock_get.return_value = mock_response
        
        response = client.get(
            "/birdeye/trader-board/gainers",
            params={
                "api_key": "test_key",
                "limit": 20,
                "sort_by": "volume_24h"
            }
        )
        
        assert response.status_code == 200
    
    @patch("httpx.AsyncClient.get")
    def test_get_gainers_api_error(self, mock_get):
        """Test gainers endpoint API error handling"""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        mock_get.return_value = mock_response
        
        response = client.get(
            "/birdeye/trader-board/gainers",
            params={"api_key": "test_key"}
        )
        
        assert response.status_code == 200  # Our endpoint returns 200 with error message
        assert "error" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
