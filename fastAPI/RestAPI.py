from uuid import uuid4
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
import httpx

app = FastAPI()


class Link(BaseModel):
    """Link model for social/resource links."""
    type: str
    label: str
    url: HttpUrl


class TokenIn(BaseModel):
    """Token input model with validation."""
    url: HttpUrl
    chainId: str
    tokenAddress: str
    icon: HttpUrl
    header: HttpUrl
    description: str
    links: List[Link]


class TokenOut(BaseModel):
    """Token output model."""
    url: HttpUrl
    chainId: str
    tokenAddress: str
    icon: HttpUrl
    header: HttpUrl
    description: str
    links: List[Link]


class PriceData(BaseModel):
    """Price data from Birdeye API."""
    address: str
    price: float
    liquidity: Optional[float] = None
    lastTradeUnixTime: Optional[int] = None
    priceChange24h: Optional[float] = None


class GainerData(BaseModel):
    """Gainer token data from trader board."""
    address: str
    symbol: str
    name: str
    price: float
    priceChange: float
    priceChange24h: float
    liquidity: Optional[float] = None
    volume24h: Optional[float] = None


@app.post("/tokens/", response_model=TokenOut)
async def create_token(token: TokenIn):
    print(f"Creating token: {token.chainId}, Address: {token.tokenAddress}, Description: {token.description}")
    return token


@app.get("/birdeye/price")
async def get_token_price(
    address: str = Query(..., description="Token address"),
    api_key: str = Query(..., description="Birdeye API key")
):
    """
    Fetch token price from Birdeye API
    GET https://public-api.birdeye.so/defi/price
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://public-api.birdeye.so/defi/price",
            params={"address": address},
            headers={"X-API-KEY": api_key}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to fetch price: {response.status_code}"}


@app.get("/birdeye/trader-board/gainers")
async def get_trader_board_gainers(
    api_key: str = Query(..., description="Birdeye API key"),
    limit: int = Query(10, description="Number of gainers to fetch"),
    sort_by: str = Query("price_change_24h", description="Sort field")
):
    """
    Fetch top gainers from trader board
    https://birdeye.so/trader-board
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public-api.birdeye.so/defi/v3/token/top/gainers",
                params={"limit": limit, "sortBy": sort_by},
                headers={"X-API-KEY": api_key},
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                print(f"Fetched {limit} top gainers from Birdeye")
                return data
            return {"error": f"Failed to fetch gainers: {response.status_code}"}
        except Exception as e:
            print(f"Error fetching gainers: {str(e)}")
            return {"error": str(e)}
