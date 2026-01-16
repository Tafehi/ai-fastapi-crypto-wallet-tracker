"""duno endpoints for fetching data."""
import os
from typing import Optional, Literal
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from functools import lru_cache
from dune_client.client import DuneClient



router = APIRouter(prefix="/dune", tags=["Dune"])


class QueryParameterModel(BaseModel):
    """Pydantic model for query parameters."""
    name: str = Field(..., description="Parameter name")
    value: str | int | float = Field(..., description="Parameter value")
    param_type: Literal["text", "number", "date", "enum"] = Field(..., description="Parameter type")


class DuneQueryRequest(BaseModel):
    """Pydantic model for Dune query request."""
    query_id: int = Field(..., description="Dune query ID")



def __get_credentials():
    try:
        load_dotenv()
        duno_api_key = os.getenv("DUNE_API_KEY")
        if not duno_api_key:
            raise ValueError("DUNE_API_KEY not found in environment variables")
    except Exception as e:
        raise RuntimeError(f"Failed to load DUNE_API_KEY from environment: {e}")
    return duno_api_key


@lru_cache(maxsize=1)
def get_duno_client():
    """Get cached DuneClient instance."""
    api_key = __get_credentials()
    return DuneClient(api_key)


def _build_query_parameters(params: list[QueryParameterModel]) -> list:
    """Convert Pydantic models to DuneClient QueryParameter objects."""
    query_params = []
    for param in params:
        # Simplified - just collect params as dicts
        query_params.append({
            "name": param.name,
            "value": param.value,
            "type": param.param_type
        })
    return query_params


def query_builder(request: DuneQueryRequest):
    """Build a Dune query from a request model."""
    query_params = _build_query_parameters(request.params) if hasattr(request, 'params') and request.params else []
    return {
        "query_id": request.query_id,
        "params": query_params
    }



@router.get("/result/{query_id}")
async def get_query_result(query_id: int, dune: DuneClient = Depends(get_duno_client)):
    """Get the latest result for a Dune query by ID."""
    try:
        query_result = dune.get_latest_result(query_id)
        return {
            "query_id": query_id,
            "result": query_result,
            "status": "success"
        }
    except Exception as e:
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to get Dune query result: {str(e)}")