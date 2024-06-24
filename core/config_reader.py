from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    @property
    def URL(self):
        return "sqlite+aiosqlite:///./DB.db"

    ECHO: bool


config = Settings()
