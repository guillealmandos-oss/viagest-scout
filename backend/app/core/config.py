import json
from functools import lru_cache
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Viagest Scout API"
    app_env: str = "development"
    database_url: str = "sqlite:///./travel_strategy.db"
    flight_provider: str = "amadeus"
    flight_providers: Annotated[list[str], NoDecode] = Field(default_factory=list)
    allow_duffel_test: bool = False
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
    frontend_origin: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FRONTEND_ORIGIN", "frontend_origin"),
    )

    @staticmethod
    def _normalize_origin(origin: str) -> str:
        """Railway / paste mistakes often wrap origins or JSON in extra quotes."""
        o = origin.strip()
        while True:
            if len(o) >= 2 and o.startswith('"') and o.endswith('"'):
                o = o[1:-1].strip()
            elif len(o) >= 2 and o.startswith("'") and o.endswith("'"):
                o = o[1:-1].strip()
            else:
                break
        if o.startswith("http"):
            o = o.rstrip("/")
        return o

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, list):
            return [cls._normalize_origin(str(o)) for o in value if str(o).strip()]
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            while True:
                if len(stripped) >= 2 and stripped.startswith('"') and stripped.endswith('"'):
                    stripped = stripped[1:-1].strip()
                elif len(stripped) >= 2 and stripped.startswith("'") and stripped.endswith("'"):
                    stripped = stripped[1:-1].strip()
                else:
                    break
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, list):
                    return [cls._normalize_origin(str(item)) for item in parsed if str(item).strip()]
            return [cls._normalize_origin(part) for part in stripped.split(",") if part.strip()]
        return value

    @model_validator(mode="after")
    def merge_frontend_origin_into_cors(self):
        """Opcional en Railway: FRONTEND_ORIGIN=https://tu-frontend.up.railway.app sin tocar ALLOWED_ORIGINS."""
        if self.frontend_origin:
            normalized = self._normalize_origin(self.frontend_origin)
            if normalized and normalized not in self.allowed_origins:
                object.__setattr__(self, "allowed_origins", [*self.allowed_origins, normalized])
        return self

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
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
