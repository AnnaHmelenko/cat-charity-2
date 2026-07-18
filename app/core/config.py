from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = "QRKot"
    app_description: str = "Благотворительный фонд поддержки котиков"
    database_url: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    yandex_disk_token: Optional[str] = None
    report_format: str = "%d.%m.%Y_%H-%M-%S"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
