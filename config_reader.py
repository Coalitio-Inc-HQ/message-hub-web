from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    @property
    def URL(self):
        return "sqlite+aiosqlite:///./DB.db"

    ECHO: bool
    # model_config = SettingsConfigDict(
    #    env_file=os.path.join(os.path.dirname(__file__), ".env")
    # )


config = Settings()
