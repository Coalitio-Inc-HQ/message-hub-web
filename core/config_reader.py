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

    LOG_FILE_PATH: str

    @property
    def FULL_DB_URL(self) -> str:
        return f"{self.DB_TYPE}+{self.DB_DRIVER}:///./data/{self.DB_NAME}"

    INTERNAL_BASE_DOMAIN: str
    INTERNAL_ROUTER_PREFIX: str
    INTERNAL_WS_LISTENER_PREFIX: str
    INTERNAL_GET_MESSAGE_PREFIX: str
    INTERNAL_GET_NOTIFICATION_PREFIX: str
    ALLOW_ORIGINS: str

    @property
    def ALLOW_ORIGINS_LIST(self) -> list[str]:
        return self.ALLOW_ORIGINS.split(',')

    SECRET_AUTH: str

    EXTERNAL_MAIN_BASE_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../.env"))


config = Settings()
