from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth import AuthenticatedRequest, AuthenticatedUser, get_authenticated_request
from app.contracts import (
    AnalysisJobCreate,
    AnalysisJobCreated,
    AnalysisJobStatus,
    JobStatusResponse,
    ReportCreate,
    ReportCreated,
    ReportDetail,
)
from app.main import app
from app.normalization import canonical_sha256
from app.persistence import (
    PersistenceConflictError,
    PersistenceNotFoundError,
    get_report_store,
)

NARRATIVE = "A suspended load crossed the marked access route while a worker stood nearby."
USER_A = uuid4()
USER_B = uuid4()


class FakeStore:
    def __init__(self) -> None:
        self.reports: dict[tuple[str, str], tuple[str, str]] = {}
        self.report_owner: dict[str, str] = {}

    async def create_report(
        self, value: ReportCreate, *, idempotency_key: str, access_token: str
    ) -> ReportCreated:
        key = (access_token, idempotency_key)
        request_hash = canonical_sha256(value.model_dump(mode="json"))
        existing = self.reports.get(key)
        if existing:
            if existing[1] != request_hash:
                raise PersistenceConflictError("idempotency key was reused with different input")
            return ReportCreated(report_id=existing[0], version=1, replayed=True)
        report_id = str(uuid4())
        self.reports[key] = (report_id, request_hash)
        self.report_owner[report_id] = access_token
        return ReportCreated(report_id=report_id, version=1, replayed=False)

    async def create_analysis_job(
        self,
        report_id: str,
        value: AnalysisJobCreate,
        *,
        idempotency_key: str,
        access_token: str,
    ) -> AnalysisJobCreated:
        if self.report_owner.get(report_id) != access_token:
            raise PersistenceNotFoundError("resource is unavailable")
        return AnalysisJobCreated(
            job_id=str(uuid4()), status=AnalysisJobStatus.QUEUED, replayed=False
        )

    async def get_job(self, job_id: str, *, access_token: str) -> JobStatusResponse:
        return JobStatusResponse(
            job_id=job_id,
            report_id=str(uuid4()),
            status=AnalysisJobStatus.QUEUED,
            attempt_count=0,
            error_code=None,
            analysis_id=None,
            updated_at=datetime.now(UTC),
        )

    async def get_report(self, report_id: str, *, access_token: str) -> ReportDetail:
        raise PersistenceNotFoundError("resource is unavailable")


@pytest.fixture
def client_and_store() -> Generator[tuple[TestClient, FakeStore]]:
    store = FakeStore()
    request = AuthenticatedRequest(
        user=AuthenticatedUser(id=USER_A, role="authenticated", is_anonymous=True),
        access_token="user-a-token",
    )
    app.dependency_overrides[get_authenticated_request] = lambda: request
    app.dependency_overrides[get_report_store] = lambda: store
    with TestClient(app) as client:
        yield client, store
    app.dependency_overrides.clear()


def test_report_creation_preserves_input_and_is_idempotent(
    client_and_store: tuple[TestClient, FakeStore],
) -> None:
    client, _ = client_and_store
    headers = {"Idempotency-Key": "report-key-0001"}
    body = {"narrative": NARRATIVE, "site": None, "report_date": None}

    created = client.post("/v1/reports", headers=headers, json=body)
    replayed = client.post("/v1/reports", headers=headers, json=body)
    conflict = client.post(
        "/v1/reports",
        headers=headers,
        json={"narrative": f"{NARRATIVE} Changed."},
    )

    assert created.status_code == 201
    assert replayed.status_code == 201
    assert replayed.json()["report_id"] == created.json()["report_id"]
    assert replayed.json()["replayed"] is True
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"


def test_another_users_report_is_indistinguishable_from_missing(
    client_and_store: tuple[TestClient, FakeStore],
) -> None:
    client, store = client_and_store
    report_id = str(uuid4())
    store.report_owner[report_id] = "user-b-token"

    response = client.get(f"/v1/reports/{report_id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_not_found"


def test_user_owned_report_can_queue_an_analysis(
    client_and_store: tuple[TestClient, FakeStore],
) -> None:
    client, _ = client_and_store
    created = client.post(
        "/v1/reports",
        headers={"Idempotency-Key": "report-key-0002"},
        json={"narrative": NARRATIVE},
    )
    report_id = created.json()["report_id"]

    queued = client.post(
        f"/v1/reports/{report_id}/analyses",
        headers={"Idempotency-Key": "analysis-key-0001"},
        json={"engine_mode": "hosted_baseline"},
    )

    assert queued.status_code == 202
    assert queued.json()["status"] == "queued"


def test_error_envelope_hides_validation_details(
    client_and_store: tuple[TestClient, FakeStore],
) -> None:
    client, _ = client_and_store
    response = client.post(
        "/v1/reports",
        headers={"Idempotency-Key": "valid-key"},
        json={"narrative": "short", "owner_id": str(UUID(int=0))},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "owner_id" not in response.text
    assert response.headers["x-request-id"]


def test_user_route_rejects_missing_bearer_token() -> None:
    with TestClient(app) as client:
        response = client.get(f"/v1/reports/{uuid4()}")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_session"


def test_oversized_request_fails_before_authentication_or_parsing() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/reports",
            content=b"x" * 524_289,
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"
