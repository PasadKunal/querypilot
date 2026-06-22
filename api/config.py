from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    groq_api_key: str = ""

    database_url: str = ""
    sandbox_database_url: str = ""

    redis_url: str = "redis://localhost:6379"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()
