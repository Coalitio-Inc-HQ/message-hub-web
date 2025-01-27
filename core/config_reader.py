import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки всего fastapi приложения
    """
    DB_TYPE: str
    DB_DRIVER: str
    DB_NAME: str
    DB_ECHO: bool

    APP_HOST: str
    APP_PORT: int

    BACKEND_CORS_ORIGINS: str
    @property
    def BACKEND_CORS_ORIGINS(self):
        return self.BACKEND_CORS_ORIGINS.split(",")

    LOG_FILE_PATH: str

    @property
    def FULL_DB_URL(self) -> str:
        return f"{self.DB_TYPE}+{self.DB_DRIVER}:///./data/{self.DB_NAME}"

    INTERNAL_BASE_DOMAIN: str
    INTERNAL_ROUTER_PREFIX: str
    INTERNAL_WS_LISTENER_PREFIX: str
    INTERNAL_GET_MESSAGE_PREFIX: str
    INTERNAL_GET_NOTIFICATION_PREFIX: str
    INTERNAL_UPLOAD_FILE_PREFIX:str

    SECRET_AUTH: str

    EXTERNAL_MAIN_BASE_URL: str

    S3_BUCKET_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../.env"))


config = Settings()
