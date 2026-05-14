import json
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Viagest Scout API"
    app_env: str = "development"
    database_url: str = "sqlite:///./travel_strategy.db"
    flight_provider: str = "duffel"
    flight_providers: Annotated[list[str], NoDecode] = Field(default_factory=list)
    provider_timeouts: Annotated[dict[str, float], NoDecode] = Field(
        default_factory=lambda: {"duffel": 30.0, "amadeus": 25.0, "demo": 5.0}
    )
    default_currency: str = "USD"
    allowed_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:3000"])
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    amadeus_api_key: str | None = None
    amadeus_api_secret: str | None = None
    amadeus_base_url: str = "https://test.api.amadeus.com"
    duffel_api_token: str | None = None
    duffel_base_url: str = "https://api.duffel.com"
    duffel_version: str = "v2"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return json.loads(stripped)
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    @field_validator("flight_providers", mode="before")
    @classmethod
    def parse_flight_providers(cls, value):
        if isinstance(value, list):
            return [item.strip().lower() for item in value if str(item).strip()]
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return [item.strip().lower() for item in json.loads(stripped) if str(item).strip()]
            return [item.strip().lower() for item in stripped.split(",") if item.strip()]
        return value

    @field_validator("provider_timeouts", mode="before")
    @classmethod
    def parse_provider_timeouts(cls, value):
        if isinstance(value, dict):
            return {str(key).strip().lower(): float(raw_value) for key, raw_value in value.items()}
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return {}
            if stripped.startswith("{"):
                parsed = json.loads(stripped)
                return {str(key).strip().lower(): float(raw_value) for key, raw_value in parsed.items()}

            timeouts: dict[str, float] = {}
            for item in stripped.split(","):
                normalized_item = item.strip()
                if not normalized_item or ":" not in normalized_item:
                    continue
                provider_name, timeout_value = normalized_item.split(":", 1)
                provider_name = provider_name.strip().lower()
                timeout_value = timeout_value.strip()
                if provider_name and timeout_value:
                    timeouts[provider_name] = float(timeout_value)
            return timeouts
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
