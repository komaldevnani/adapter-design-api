from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class Settings:
    """Configuration for the adapter and its upstream browser session."""

    upstream_base_url: str = os.getenv("UNDERLYING_API_URL", "").rstrip("/")
    session_cookie: str = os.getenv("BROWSER_SESSION_COOKIE", "")
    index_path: str = os.getenv("UNDERLYING_INDEX_PATH", "/items")
    create_path: str = os.getenv("UNDERLYING_CREATE_PATH", "/items")
    item_path_template: str = os.getenv("UNDERLYING_ITEM_PATH", "/items/{item_id}")
    request_timeout_seconds: float = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "30"))

    def item_path(self, item_id: str) -> str:
        return self.item_path_template.format(item_id=quote(item_id, safe=""))


settings = Settings()