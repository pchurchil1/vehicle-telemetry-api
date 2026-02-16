from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "vehicle-telemetry-api"
    environment: str = "dev"  # dev|test|prod
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

settings = Settings()