from __future__ import annotations

from typing import Annotated, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from app.auth import CurrentRequest
from app.contracts import (
    AnalysisJobCreate,
    AnalysisJobCreated,
    JobStatusResponse,
    ReportCreate,
    ReportCreated,
    ReportDetail,
)
from app.errors import ApiProblem
from app.persistence import (
    PersistenceConflictError,
    PersistenceNotFoundError,
    PersistenceQuotaError,
    PersistenceUnavailableError,
    ReportStore,
    get_report_store,
)

router = APIRouter(prefix="/v1")
IdempotencyKey = Annotated[
    str, Header(alias="Idempotency-Key", min_length=8, max_length=200)
]
Store = Annotated[ReportStore, Depends(get_report_store)]


def _raise_store_problem(exc: Exception) -> NoReturn:
    if isinstance(exc, PersistenceConflictError):
        raise ApiProblem(409, "idempotency_conflict", str(exc)) from exc
    if isinstance(exc, PersistenceNotFoundError):
        raise ApiProblem(
            404, "resource_not_found", "The requested resource is unavailable."
        ) from exc
    if isinstance(exc, PersistenceQuotaError):
        raise ApiProblem(429, "demo_limit_reached", str(exc), retryable=True) from exc
    raise ApiProblem(
        503,
        "database_unavailable",
        "Persistence is temporarily unavailable.",
        retryable=True,
    ) from exc


@router.post("/reports", response_model=ReportCreated, status_code=status.HTTP_201_CREATED)
async def create_report(
    value: ReportCreate,
    idempotency_key: IdempotencyKey,
    request: CurrentRequest,
    store: Store,
) -> ReportCreated:
    try:
        created = await store.create_report(
            value,
            idempotency_key=idempotency_key,
            access_token=request.access_token,
        )
    except PersistenceUnavailableError as exc:
        _raise_store_problem(exc)
    except (PersistenceConflictError, PersistenceNotFoundError, PersistenceQuotaError) as exc:
        _raise_store_problem(exc)
    return created


@router.post(
    "/reports/{report_id}/analyses",
    response_model=AnalysisJobCreated,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_analysis_job(
    report_id: UUID,
    value: AnalysisJobCreate,
    idempotency_key: IdempotencyKey,
    request: CurrentRequest,
    store: Store,
) -> AnalysisJobCreated:
    try:
        return await store.create_analysis_job(
            str(report_id),
            value,
            idempotency_key=idempotency_key,
            access_token=request.access_token,
        )
    except (
        PersistenceConflictError,
        PersistenceNotFoundError,
        PersistenceQuotaError,
        PersistenceUnavailableError,
    ) as exc:
        _raise_store_problem(exc)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: UUID, request: CurrentRequest, store: Store) -> JobStatusResponse:
    try:
        return await store.get_job(str(job_id), access_token=request.access_token)
    except (PersistenceNotFoundError, PersistenceUnavailableError) as exc:
        _raise_store_problem(exc)


@router.get("/reports/{report_id}", response_model=ReportDetail)
async def get_report(report_id: UUID, request: CurrentRequest, store: Store) -> ReportDetail:
    try:
        return await store.get_report(str(report_id), access_token=request.access_token)
    except (PersistenceNotFoundError, PersistenceUnavailableError) as exc:
        _raise_store_problem(exc)
