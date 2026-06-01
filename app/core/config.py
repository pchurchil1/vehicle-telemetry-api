from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "vehicle-telemetry-api"
    environment: str = "dev"  # dev|test|prod
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    auth_enabled: bool = False
    jwt_secret_key: str = "dev-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60
    database_url: str
    database_url_test: str | None = None

    @property
    def active_database_url(self) -> str:
        if self.environment == "test" and self.database_url_test:
            return self.database_url_test
        return self.database_url

settings = Settings()
