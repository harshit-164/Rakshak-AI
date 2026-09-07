from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiProblem(Exception):
    status_code: int
    code: str
    message: str
    retryable: bool = False
