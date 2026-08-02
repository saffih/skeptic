from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class STTError(RuntimeError):
    code: str
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def require(condition: bool, code: str, message: str, **details: Any) -> None:
    if not condition:
        raise STTError(code, message, details or None)
