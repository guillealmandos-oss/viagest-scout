from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class UserFacingError(RuntimeError):
    message_key: str
    status_code: int
    params: dict[str, Any] = field(default_factory=dict)
