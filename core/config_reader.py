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

    @property
    def FULL_DB_URL(self) -> str:
        return f"{self.DB_TYPE}+{self.DB_DRIVER}:///./{self.DB_NAME}"

    INTERNAL_BASE_DOMAIN: str
    INTERNAL_ROUTER_PREFIX: str
    INTERNAL_WS_LISTENER_PREFIX: str
    INTERNAL_GET_MESSAGE_PREFIX: str
    INTERNAL_GET_NOTIFICATION_PREFIX: str

    @property
    def FULL_WEBHOOK_URL(self) -> str:
        return f'{self.INTERNAL_BASE_DOMAIN}{self.INTERNAL_GET_MESSAGE_PREFIX}'

    EXTERNAL_MAIN_BASE_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"))


config = Settings()
