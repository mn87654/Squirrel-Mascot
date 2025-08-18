# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./squirrel.db"
    MAIN_CHANNEL_ID: str = ""
    DAILY_REWARD: int = 100
    REFERRAL_REWARD: int = 200
    TASK_JOIN_REWARD: int = 100
    TIMEZONE: str = "UTC"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
