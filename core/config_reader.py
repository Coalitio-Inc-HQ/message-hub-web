import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки fastapi приложения
    """
    DB_TYPE: str
    DB_DRIVER: str
    DB_NAME: str
    DB_ECHO: bool

    @property
    def FULL_DB_URL(self) -> str:
        return f"{self.DB_TYPE}+{self.DB_DRIVER}:///./{self.DB_NAME}"

    BASE_DOMAIN: str
    ROUTER_PREFIX: str
    WS_LISTENER_URL: str
    COPPER_MAIN_URL: str

    @property
    def WS_WAITING_CHATS_ACTION_NAME(self) -> str:
        return f"{self.WS_CHATS_ACTION}{self.WS_WAITING_ACTION}"

    @property
    def WS_READ_CHAT_ACTION_NAME(self) -> str:
        return f"{self.WS_CHATS_ACTION}{self.WS_READ_ACTION}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"))


config = Settings()
