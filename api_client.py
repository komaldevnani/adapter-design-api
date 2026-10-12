from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from config import Settings


@dataclass(frozen=True)
class UpstreamResult:
    body: str
    status_code: int
    url: str


class UpstreamApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class UpstreamApiClient:
    """Reusable HTTP client for an HTML-producing, cookie-authenticated API."""

    def __init__(self, config: Settings) -> None:
        if not config.upstream_base_url:
            raise ValueError("UNDERLYING_API_URL must be configured")
        if not config.session_cookie:
            raise ValueError("BROWSER_SESSION_COOKIE must be configured")

        self._client = httpx.AsyncClient(
            base_url=config.upstream_base_url,
            timeout=config.request_timeout_seconds,
            headers={
                "Accept": "text/html",
                "Cookie": config.session_cookie,
                "User-Agent": "adapter-design-api/1.0",
            },
        )

    async def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> UpstreamResult:
        try:
            response = await self._client.request(method, path, json=payload)
        except httpx.HTTPError as exc:
            raise UpstreamApiError(f"Unable to reach underlying API: {exc}") from exc

        if response.is_error:
            raise UpstreamApiError(
                f"Underlying API returned HTTP {response.status_code}",
                response.status_code,
            )

        return UpstreamResult(
            body=response.text,
            status_code=response.status_code,
            url=str(response.url),
        )

    async def close(self) -> None:
        await self._client.aclose()
