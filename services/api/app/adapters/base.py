from dataclasses import dataclass
from typing import Protocol

from app.contracts import AnalysisResult


@dataclass(frozen=True)
class AnalysisInput:
    narrative: str
    activity: str | None


class ModelAdapter(Protocol):
    async def health(self) -> bool: ...

    async def analyze(self, value: AnalysisInput) -> AnalysisResult: ...

    async def close(self) -> None: ...


class ProviderUnavailableError(RuntimeError):
    """External inference did not return a usable response."""


class ProviderOutputError(RuntimeError):
    """External inference returned invalid or ungrounded output."""
