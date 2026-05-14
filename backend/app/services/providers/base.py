from abc import ABC, abstractmethod

from app.core.config import get_settings
from app.schemas.common import SearchRequestInput


class BaseFlightProvider(ABC):
    provider_name: str

    def __init__(self) -> None:
        self.settings = get_settings()
        self._last_request_metadata: dict = {}

    @abstractmethod
    async def search_offers(self, search_input: SearchRequestInput) -> list[dict]:
        raise NotImplementedError

    def get_timeout_seconds(self) -> float:
        timeout = self.settings.provider_timeouts.get(self.provider_name)
        if timeout is None:
            return 20.0
        return float(timeout)

    def reset_last_request_metadata(self) -> None:
        self._last_request_metadata = {}

    def get_last_request_metadata(self) -> dict:
        return dict(self._last_request_metadata)

    def set_last_request_metadata(
        self,
        *,
        external_request_id: str | None = None,
        external_correlation_id: str | None = None,
    ) -> None:
        self._last_request_metadata = {
            "external_request_id": external_request_id,
            "external_correlation_id": external_correlation_id,
        }

    def capture_response_metadata(self, response) -> None:
        headers = response.headers
        self.set_last_request_metadata(
            external_request_id=headers.get("x-request-id") or headers.get("X-Request-ID"),
            external_correlation_id=headers.get("x-client-correlation-id")
            or headers.get("X-Client-Correlation-Id"),
        )
