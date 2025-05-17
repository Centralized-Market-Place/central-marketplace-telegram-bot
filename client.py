import httpx
from config import settings

class ApiClient:
    def __init__(self, telegram_user_id: int):
        headers = {"X-Telegram-User-Id": str(telegram_user_id)}
        self._client = httpx.AsyncClient(
            base_url=settings.API_URL,
            headers=headers,
            timeout=10.0
        )

    async def list_categories(self) -> list[str]:
        return ["technology", "mobile", "fashion"]

    async def list_channels(self, page: int = 1, page_size: int = 10, category: str | None = None):
        params = {"page": page, "page_size": page_size}
        if category:
            params["query"] = category
        response = await self._client.get("/channels/", params=params)
        return response.json()

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 10,
        category: str | None = None,
        query: str | None = None
    ):
        params = {"page": page, "page_size": page_size}
        if category:
            params["query"] = category
        if query:
            params["query"] = query
        response = await self._client.get("/products/", params=params)
        return response.json()

    async def get_product(self, product_id: str):
        response = await self._client.get(f"/products/{product_id}")
        return response.json()

    async def post_comment(self, product_id: str, text: str):
        payload = {"text": text}
        response = await self._client.post(
            f"/products/{product_id}/comments", json=payload
        )
        return response.json()

    async def add_bookmark(self, product_id: str):
        response = await self._client.post(f"/bookmarks/{product_id}")
        return response.json()

    async def remove_bookmark(self, product_id: str):
        await self._client.delete(f"/bookmarks/{product_id}")

    async def list_bookmarks(self, page: int = 1, page_size: int = 10):
        params = {"page": page, "page_size": page_size}
        response = await self._client.get("/bookmarks/", params=params)
        return response.json()