from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Временно без файла окружения.
    Для пока что не вижу смысла.
    """
    URL: str = "sqlite+aiosqlite:///./DB.db"
    ECHO: bool = True


config = Settings()
