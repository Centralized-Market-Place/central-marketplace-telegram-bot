# client.py

import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from config import settings

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self, telegram_user_id: int):
        """
        :param telegram_user_id: Injected into every request as X-Telegram-User-Id
        """
        self._headers = {
            "X-Telegram-User-Id": str(telegram_user_id),
            "Accept": "application/json",
        }
        timeout = httpx.Timeout(10.0, connect=5.0)
        self._client = httpx.AsyncClient(
            base_url=settings.API_URL,
            headers=self._headers,
            timeout=timeout,
        )

    async def __aenter__(self) -> "ApiClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        """Cleanly close the HTTP session."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Internal helper to send an HTTP request and return parsed JSON.
        Raises on HTTP errors or network issues.
        """
        try:
            response = await self._client.request(
                method=method, url=path, params=params, json=json
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP %s %s → %s %s",
                         method, path,
                         exc.response.status_code,
                         exc.response.text)
            raise
        except httpx.RequestError as exc:
            logger.error("Network error during %s %s: %s", method, path, exc)
            raise


    async def list_categories(self) -> List[str]:
        return ["technology", "mobile", "fashion"]

    async def list_channels(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Union[int, str]] = {
            "page": page,
            "page_size": page_size,
        }
        if category:
            params["category"] = category
        if query:
            params["query"] = query
        return await self._request("GET", "/channels/", params=params)


    async def list_products(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Union[int, str]] = {
            "page": page,
            "page_size": page_size,
        }
        if category:
            params["category"] = category
        if query:
            params["query"] = query
        return await self._request("GET", "/products/", params=params)

    async def get_product(self, product_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/products/{product_id}")

    async def post_comment(self, product_id: str, text: str) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/products/{product_id}/comments",
            json={"text": text},
        )

    async def add_bookmark(self, product_id: str) -> Dict[str, Any]:
        return await self._request("POST", f"/bookmarks/{product_id}")

    async def remove_bookmark(self, product_id: str) -> None:
        await self._request("DELETE", f"/bookmarks/{product_id}")

    async def list_bookmarks(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        return await self._request("GET", "/bookmarks/", params=params)
