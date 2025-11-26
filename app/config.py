"""Application configuration loaded from environment variables with fallbacks."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object with short, env-friendly aliases."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    APP_NAME: str = Field("CareSphere API", alias="APP_NAME")
    APP_VERSION: str = Field("1.0.0", alias="APP_VER")
    DEBUG: bool = Field(False, alias="APP_DEBUG")

    # Server
    API_HOST: str = Field("0.0.0.0", alias="API_HOST")
    API_PORT: int = Field(8000, alias="API_PORT")
    RELOAD: bool = Field(False, alias="API_RELOAD")

    # Database
    DATABASE_URL: str = Field(..., alias="DB_URL")
    DB_ECHO: bool = Field(False, alias="DB_ECHO")

    # Security
    JWT_SECRET: str = Field(..., alias="JWT_SECRET")
    JWT_ALG: str = Field("HS256", alias="JWT_ALG")
    JWT_EXP: int = Field(86400, alias="JWT_EXP")  # 24h
    JWT_REFRESH_EXP: int = Field(604800, alias="JWT_REFRESH_EXP")  # 7d
    BCRYPT_ROUNDS: int = Field(12, alias="HASH_ROUNDS")

    # CORS
    ALLOWED_ORIGINS: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    # Pagination / listing defaults
    PAGE_DEF: int = Field(1, alias="PAGE_DEF")
    PAGE_SIZE_DEF: int = Field(20, alias="PAGE_SIZE_DEF")
    PAGE_SIZE_MAX: int = Field(100, alias="PAGE_SIZE_MAX")
    LOG_LIMIT_DEF: int = Field(50, alias="LOG_LIMIT_DEF")
    LOG_LIMIT_MAX: int = Field(200, alias="LOG_LIMIT_MAX")

    # Messaging defaults
    MSG_SENDER_NAME: str = Field("CareSphere", alias="MSG_NAME")
    MSG_SENDER_EMAIL: str = Field("no-reply@caresphere.app", alias="MSG_EMAIL")
    MSG_SENDER_PHONE: str = Field("+10000000000", alias="MSG_PHONE")

    # EKDSend Email API
    EKDSEND_API_KEY: str = Field("", alias="EKDSEND_API_KEY")
    EKDSEND_API_URL: str = Field(
        "https://es.ekddigital.com/api/v1", alias="EKDSEND_API_URL")

    # Features
    ENABLE_DEMO_DATA: bool = Field(False, alias="FEATURE_DEMO")
    ENABLE_ANALYTICS: bool = Field(True, alias="FEATURE_ANALYTICS")
    ENABLE_AUTOMATION: bool = Field(True, alias="FEATURE_AUTOMATION")

    # Logging
    LOG_LEVEL: str = Field("info", alias="LOG_LEVEL")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Return list version of comma-separated origins."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
