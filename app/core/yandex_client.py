from http import HTTPStatus
from typing import Optional

import httpx
from fastapi import HTTPException

from app.core.config import settings

YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk"
REPORTS_FOLDER = "QRKot Reports"


class YandexDiskClient:

    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"OAuth {token}"}
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.headers, trust_env=False
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.aclose()

    async def _create_folder(self) -> None:
        response = await self.client.put(
            f"{YANDEX_API_URL}/resources",
            params={"path": REPORTS_FOLDER},
        )
        if response.status_code == HTTPStatus.CONFLICT:
            return
        response.raise_for_status()

    async def create_excel_file(self, filename: str) -> tuple[str, str]:
        await self._create_folder()
        path = f"{REPORTS_FOLDER}/{filename}"
        response = await self.client.get(
            f"{YANDEX_API_URL}/resources/upload",
            params={"path": path, "overwrite": "true"},
        )
        response.raise_for_status()
        href = response.json().get("href")
        if not href:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Яндекс Диск не вернул ссылку для загрузки.",
            )
        return href, path

    async def upload_file(self, upload_url: str, file_content: bytes) -> None:
        response = await self.client.put(upload_url, content=file_content)
        response.raise_for_status()

    async def publish_file(self, path: str) -> str:
        response = await self.client.put(
            f"{YANDEX_API_URL}/resources/publish",
            params={"path": path},
        )
        response.raise_for_status()
        response = await self.client.get(
            f"{YANDEX_API_URL}/resources",
            params={"path": path, "fields": "public_url"},
        )
        response.raise_for_status()
        return response.json().get("public_url")


async def get_yandex_client() -> YandexDiskClient:
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Токен Яндекс Диска не настроен.",
        )
    return YandexDiskClient(settings.yandex_disk_token)
