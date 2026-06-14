from http import HTTPStatus
from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

HTTPX_TIMEOUT = 30.0
DISK_PREFIX = "disk:/"
UPLOAD_ENDPOINT = "/resources/upload"
PUBLISH_ENDPOINT = "/resources/publish"
RESOURCES_ENDPOINT = "/resources"


class YandexDiskClient:
    """Асинхронный клиент для работы с API Яндекс Диска."""

    def __init__(self, token: str):
        """Инициализация клиента с OAuth-токеном."""
        self.token = token
        self.base_url = settings.yandex_disk_api_url
        self.headers = {"Authorization": f"OAuth {token}"}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Открыть асинхронную сессию."""
        self._client = httpx.AsyncClient(timeout=HTTPX_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрыть асинхронную сессию."""
        if self._client:
            await self._client.aclose()

    async def create_excel_file(
            self, title: str, folder: str = None
    ) -> tuple[str, str]:
        """Получить ссылку для загрузки файла и путь к нему на Диске."""
        if folder is None:
            folder = settings.yandex_disk_folder

        await self._create_folder(folder)

        file_path = f"{DISK_PREFIX}{folder}/{title}.xlsx"

        response = await self._client.get(
            f"{self.base_url}{UPLOAD_ENDPOINT}",
            headers=self.headers,
            params={"path": file_path, "overwrite": "true"}
        )
        response.raise_for_status()

        data = response.json()
        upload_url = data.get("href")

        if not upload_url:
            raise ValueError("Не удалось получить ссылку для загрузки")

        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes):
        """Загрузить бинарное содержимое файла по ссылке."""
        response = await self._client.put(
            upload_url,
            content=content,
            headers={
                "Content-Type": (
                    "application/vnd.openxmlformats-officedocument"
                    ".spreadsheetml.sheet"
                )
            }
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        """Сделать файл публичным и вернуть ссылку на него."""
        response = await self._client.put(
            f"{self.base_url}{PUBLISH_ENDPOINT}",
            headers=self.headers,
            params={"path": file_path}
        )
        response.raise_for_status()

        response = await self._client.get(
            f"{self.base_url}{RESOURCES_ENDPOINT}",
            headers=self.headers,
            params={"path": file_path}
        )
        response.raise_for_status()

        data = response.json()
        public_url = data.get("public_url")

        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ссылка не была получена со стороны Яндекс Диска"
            )

        return public_url

    async def _create_folder(self, folder: str):
        """Создать папку на Диске, если её нет."""
        try:
            await self._client.put(
                f"{self.base_url}{RESOURCES_ENDPOINT}",
                headers=self.headers,
                params={"path": f"{DISK_PREFIX}{folder}"}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code != HTTPStatus.CONFLICT:
                raise


async def get_yandex_client():
    """Dependency для получения клиента Яндекс Диска."""
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Яндекс Диск не настроен. Добавьте YANDEX_DISK_TOKEN в .env"
        )

    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client