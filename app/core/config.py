from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    app_title: str = "Благотворительный фонд поддержки котиков QRKot"
    app_description: str = "Сервис для поддержки котиков"
    database_url: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    auth_secret: str = "supersecretkey123!@#"
    auth_token_lifetime_seconds: int = 3600
    yandex_disk_token: Optional[str] = None
    report_format: str = "%Y/%m/%d %H:%M:%S"

    class Config:
        """Конфигурация загрузки переменных из .env файла."""

        env_file = ".env"


settings = Settings()
