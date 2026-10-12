from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from pydantic import BaseModel, ConfigDict

from api_client import UpstreamApiClient, UpstreamApiError
from config import settings
from html_parser import parse_html


class ResourcePayload(BaseModel):
    """Payload forwarded to the upstream API."""

    model_config = ConfigDict(extra="allow")


class ParsedResponse(BaseModel):
    """Stable response shape returned by this adapter."""

    data: dict[str, Any]
    source_status_code: int
    source_url: str


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    client = UpstreamApiClient(settings)
    application.state.upstream_client = client
    try:
        yield
    finally:
        await client.close()


app = FastAPI(
    title="Flock meter Adapter Design - API",
    version="1.0.0",
    lifespan=lifespan,
)


def get_upstream_client(request: Request) -> UpstreamApiClient:
    return request.app.state.upstream_client


async def call_upstream(
    client: UpstreamApiClient,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> ParsedResponse:
    try:
        result = await client.request(method, path, payload)
    except UpstreamApiError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ParsedResponse(
        data=parse_html(result.body),
        source_status_code=result.status_code,
        source_url=result.url,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/items", response_model=ParsedResponse)
async def index_items(
    client: UpstreamApiClient = Depends(get_upstream_client),
) -> ParsedResponse:
    return await call_upstream(client, "GET", settings.index_path)


@app.post(
    "/items",
    response_model=ParsedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    payload: ResourcePayload,
    client: UpstreamApiClient = Depends(get_upstream_client),
) -> ParsedResponse:
    return await call_upstream(client, "POST", settings.create_path, payload.model_dump())


@app.get("/items/{item_id}", response_model=ParsedResponse)
async def get_item(
    item_id: str = Path(min_length=1),
    client: UpstreamApiClient = Depends(get_upstream_client),
) -> ParsedResponse:
    return await call_upstream(client, "GET", settings.item_path(item_id))


@app.put("/items/{item_id}", response_model=ParsedResponse)
async def update_item(
    item_id: str,
    payload: ResourcePayload,
    client: UpstreamApiClient = Depends(get_upstream_client),
) -> ParsedResponse:
    return await call_upstream(
        client,
        "PUT",
        settings.item_path(item_id),
        payload.model_dump(),
    )


@app.delete("/items/{item_id}", response_model=ParsedResponse)
async def delete_item(
    item_id: str,
    client: UpstreamApiClient = Depends(get_upstream_client),
) -> ParsedResponse:
    return await call_upstream(client, "DELETE", settings.item_path(item_id))
