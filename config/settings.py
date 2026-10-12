from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = Field(default="development")
    LLM_PROVIDER: str = Field(default="demo")
    LLM_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="demo-model")
    DATABASE_URL: str = Field(default="sqlite:///storage/app.db")
    MAX_AGENT_STEPS: int = Field(default=8)
    MAX_RETRIES: int = Field(default=3)
    TASK_TIMEOUT_SECONDS: int = Field(default=120)
    MAX_TOOL_CALLS: int = Field(default=20)
    MAX_UPLOAD_SIZE_MB: int = Field(default=20)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
