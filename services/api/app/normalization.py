from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any

from app.contracts import NORMALIZATION_VERSION, AnalysisJobCreate, ReportCreate


def normalize_text(value: str) -> str:
    """Normalize inference text without stripping or deleting meaningful whitespace."""
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def report_storage_values(value: ReportCreate) -> dict[str, Any]:
    normalized = normalize_text(value.narrative)
    request_value = value.model_dump(mode="json")
    return {
        "request_sha256": canonical_sha256(request_value),
        "normalized_input": normalized,
        "normalization_version": NORMALIZATION_VERSION,
        "narrative_sha256": sha256_text(normalized),
    }


def analysis_request_sha256(report_id: str, value: AnalysisJobCreate) -> str:
    return canonical_sha256(
        {"report_id": report_id, "engine_mode": value.engine_mode.value}
    )
