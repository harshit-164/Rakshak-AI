from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

import httpx

from app.config import Settings, get_settings
from app.contracts import (
    AnalysisJobCreate,
    AnalysisJobCreated,
    JobStatusResponse,
    ReportCreate,
    ReportCreated,
    ReportDetail,
    ReportRecord,
    StoredAnalysis,
)
from app.normalization import analysis_request_sha256, report_storage_values


class PersistenceError(RuntimeError):
    """Base error for safe persistence failures."""


class PersistenceUnavailableError(PersistenceError):
    pass


class PersistenceConflictError(PersistenceError):
    pass


class PersistenceNotFoundError(PersistenceError):
    pass


class PersistenceQuotaError(PersistenceError):
    pass


class ReportStore(Protocol):
    async def create_report(
        self, value: ReportCreate, *, idempotency_key: str, access_token: str
    ) -> ReportCreated: ...

    async def create_analysis_job(
        self,
        report_id: str,
        value: AnalysisJobCreate,
        *,
        idempotency_key: str,
        access_token: str,
    ) -> AnalysisJobCreated: ...

    async def get_job(self, job_id: str, *, access_token: str) -> JobStatusResponse: ...

    async def get_report(self, report_id: str, *, access_token: str) -> ReportDetail: ...


class SupabaseReportStore:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise PersistenceUnavailableError("database is not configured")
        self._url = settings.supabase_url.rstrip("/")
        self._anon_key = settings.supabase_anon_key
        self._client = client or httpx.AsyncClient(timeout=10.0)

    def _headers(self, access_token: str) -> dict[str, str]:
        return {
            "apikey": self._anon_key,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        access_token: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method,
                f"{self._url}{path}",
                headers=self._headers(access_token),
                json=json,
                params=params,
            )
        except httpx.HTTPError as exc:
            raise PersistenceUnavailableError("database request failed") from exc

        if response.is_success:
            try:
                return response.json()
            except ValueError as exc:
                raise PersistenceUnavailableError("database returned an invalid response") from exc

        try:
            error_document = response.json()
            database_message = str(error_document.get("message", ""))
        except ValueError:
            database_message = ""
        if "idempotency_payload_conflict" in database_message or response.status_code == 409:
            raise PersistenceConflictError("idempotency key was reused with different input")
        if "report_not_found" in database_message or response.status_code == 404:
            raise PersistenceNotFoundError("resource is unavailable")
        if "quota_" in database_message or "active_job_limit" in database_message:
            raise PersistenceQuotaError("demo usage limit reached")
        raise PersistenceUnavailableError("database operation is unavailable")

    async def create_report(
        self, value: ReportCreate, *, idempotency_key: str, access_token: str
    ) -> ReportCreated:
        storage = report_storage_values(value)
        rows = await self._request(
            "POST",
            "/rest/v1/rpc/create_report_v1",
            access_token=access_token,
            json={
                "p_idempotency_key": idempotency_key,
                "p_request_sha256": storage["request_sha256"],
                "p_narrative": value.narrative,
                "p_normalized_input": storage["normalized_input"],
                "p_normalization_version": storage["normalization_version"],
                "p_narrative_sha256": storage["narrative_sha256"],
                "p_activity": value.activity,
                "p_site": value.site,
                "p_report_date": value.report_date.isoformat() if value.report_date else None,
                "p_is_synthetic": value.is_synthetic,
            },
        )
        if not isinstance(rows, list) or len(rows) != 1:
            raise PersistenceUnavailableError("database returned no report")
        return ReportCreated(
            report_id=rows[0]["report_id"],
            version=rows[0]["report_version"],
            replayed=rows[0]["replayed"],
        )

    async def create_analysis_job(
        self,
        report_id: str,
        value: AnalysisJobCreate,
        *,
        idempotency_key: str,
        access_token: str,
    ) -> AnalysisJobCreated:
        rows = await self._request(
            "POST",
            "/rest/v1/rpc/create_analysis_job_v1",
            access_token=access_token,
            json={
                "p_report_id": report_id,
                "p_engine_mode": value.engine_mode.value,
                "p_idempotency_key": idempotency_key,
                "p_request_sha256": analysis_request_sha256(report_id, value),
            },
        )
        if not isinstance(rows, list) or len(rows) != 1:
            raise PersistenceUnavailableError("database returned no analysis job")
        return AnalysisJobCreated(
            job_id=rows[0]["job_id"],
            status=rows[0]["job_status"],
            replayed=rows[0]["replayed"],
        )

    async def get_job(self, job_id: str, *, access_token: str) -> JobStatusResponse:
        rows = await self._request(
            "GET",
            "/rest/v1/analysis_jobs",
            access_token=access_token,
            params={
                "id": f"eq.{job_id}",
                "select": "id,report_id,status,attempt_count,error_code,updated_at",
                "limit": "1",
            },
        )
        if not isinstance(rows, list) or not rows:
            raise PersistenceNotFoundError("resource is unavailable")
        analysis_rows = await self._request(
            "GET",
            "/rest/v1/analyses",
            access_token=access_token,
            params={"job_id": f"eq.{job_id}", "select": "id", "limit": "1"},
        )
        analysis_id = analysis_rows[0]["id"] if analysis_rows else None
        row = rows[0]
        return JobStatusResponse(
            job_id=row["id"],
            report_id=row["report_id"],
            status=row["status"],
            attempt_count=row["attempt_count"],
            error_code=row["error_code"],
            analysis_id=analysis_id,
            updated_at=row["updated_at"],
        )

    async def get_report(self, report_id: str, *, access_token: str) -> ReportDetail:
        rows = await self._request(
            "GET",
            "/rest/v1/reports",
            access_token=access_token,
            params={
                "id": f"eq.{report_id}",
                "select": (
                    "id,report_group_id,version,narrative,activity,site,report_date,"
                    "is_synthetic,created_at"
                ),
                "limit": "1",
            },
        )
        if not isinstance(rows, list) or not rows:
            raise PersistenceNotFoundError("resource is unavailable")
        analysis_rows = await self._request(
            "GET",
            "/rest/v1/analyses",
            access_token=access_token,
            params={
                "report_id": f"eq.{report_id}",
                "select": "id,job_id,result,duration_ms,created_at",
                "order": "created_at.desc",
            },
        )
        return ReportDetail(
            report=ReportRecord.model_validate(rows[0]),
            analyses=[StoredAnalysis.model_validate(row) for row in analysis_rows],
        )

    async def close(self) -> None:
        await self._client.aclose()


@dataclass(frozen=True)
class PersistenceRuntime:
    store: SupabaseReportStore


@lru_cache
def get_persistence_runtime() -> PersistenceRuntime:
    return PersistenceRuntime(store=SupabaseReportStore(get_settings()))


def get_report_store() -> ReportStore:
    try:
        return get_persistence_runtime().store
    except PersistenceUnavailableError:
        raise
