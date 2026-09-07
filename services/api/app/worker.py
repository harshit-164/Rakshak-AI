from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, ConfigDict

from app.adapters.base import (
    AnalysisInput,
    ModelAdapter,
    ProviderOutputError,
    ProviderUnavailableError,
)
from app.adapters.gemini import GeminiAdapter, load_hosted_configuration
from app.config import Settings
from app.normalization import canonical_sha256, normalize_text

logger = logging.getLogger(__name__)


class WorkerPersistenceError(RuntimeError):
    """A queue operation failed; retain the lease so Postgres can reclaim it safely."""


class WorkerJob(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    report_id: str
    engine_mode: str
    lease_token: str


class WorkerReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    normalized_input: str
    activity: str | None


class WorkerStore(Protocol):
    async def claim(self) -> WorkerJob | None: ...

    async def get_report(self, report_id: str) -> WorkerReport: ...

    async def heartbeat(self, job_id: str, lease_token: str) -> bool: ...

    async def finalize(
        self,
        job_id: str,
        lease_token: str,
        *,
        result: dict[str, Any],
        model_manifest_sha256: str,
        input_sha256: str,
        duration_ms: int,
    ) -> str: ...

    async def fail(self, job_id: str, lease_token: str, error_code: str) -> bool: ...

    async def close(self) -> None: ...


class SupabaseWorkerStore:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError("worker database credentials are not configured")
        self._url = settings.supabase_url.rstrip("/")
        self._service_key = settings.supabase_service_role_key
        self._client = client or httpx.AsyncClient(timeout=10.0)

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self._service_key,
            "Authorization": f"Bearer {self._service_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method,
                f"{self._url}{path}",
                headers=self._headers,
                json=json,
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise WorkerPersistenceError("worker database operation failed") from exc

    async def claim(self) -> WorkerJob | None:
        rows = await self._request("POST", "/rest/v1/rpc/claim_analysis_job_v1", json={})
        if not rows:
            return None
        try:
            return WorkerJob.model_validate(rows[0])
        except (TypeError, ValueError) as exc:
            raise WorkerPersistenceError("claimed job is invalid") from exc

    async def get_report(self, report_id: str) -> WorkerReport:
        rows = await self._request(
            "GET",
            "/rest/v1/reports",
            params={
                "id": f"eq.{report_id}",
                "select": "normalized_input,activity",
                "limit": "1",
            },
        )
        if not rows:
            raise WorkerPersistenceError("claimed job report is unavailable")
        try:
            return WorkerReport.model_validate(rows[0])
        except (TypeError, ValueError) as exc:
            raise WorkerPersistenceError("claimed job report is invalid") from exc

    async def heartbeat(self, job_id: str, lease_token: str) -> bool:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/heartbeat_analysis_job_v1",
            json={"p_job_id": job_id, "p_lease_token": lease_token},
        )
        return bool(result)

    async def finalize(
        self,
        job_id: str,
        lease_token: str,
        *,
        result: dict[str, Any],
        model_manifest_sha256: str,
        input_sha256: str,
        duration_ms: int,
    ) -> str:
        analysis_id = await self._request(
            "POST",
            "/rest/v1/rpc/finalize_analysis_job_v1",
            json={
                "p_job_id": job_id,
                "p_lease_token": lease_token,
                "p_result": result,
                "p_model_manifest_sha256": model_manifest_sha256,
                "p_input_sha256": input_sha256,
                "p_duration_ms": duration_ms,
            },
        )
        if not isinstance(analysis_id, str):
            raise WorkerPersistenceError("database returned no analysis ID")
        return analysis_id

    async def fail(self, job_id: str, lease_token: str, error_code: str) -> bool:
        result = await self._request(
            "POST",
            "/rest/v1/rpc/fail_analysis_job_v1",
            json={
                "p_job_id": job_id,
                "p_lease_token": lease_token,
                "p_error_code": error_code,
            },
        )
        return bool(result)

    async def close(self) -> None:
        await self._client.aclose()


@dataclass
class AnalysisWorker:
    store: WorkerStore
    adapter: ModelAdapter
    manifest_sha256: str
    poll_seconds: float = 2.0

    async def process_once(self) -> bool:
        job = await self.store.claim()
        if job is None:
            return False
        if job.engine_mode != "hosted_baseline":
            await self.store.fail(job.id, job.lease_token, "unsupported_engine_mode")
            return True

        heartbeat = asyncio.create_task(self._heartbeat(job))
        started = time.perf_counter()
        try:
            report = await self.store.get_report(job.report_id)
            normalized_activity = (
                normalize_text(report.activity) if report.activity is not None else None
            )
            result = await self.adapter.analyze(
                AnalysisInput(
                    narrative=report.normalized_input,
                    activity=normalized_activity,
                )
            )
            duration_ms = max(0, round((time.perf_counter() - started) * 1000))
            input_sha256 = canonical_sha256(
                {"narrative": report.normalized_input, "activity": normalized_activity}
            )
            await self.store.finalize(
                job.id,
                job.lease_token,
                result=result.model_dump(mode="json"),
                model_manifest_sha256=self.manifest_sha256,
                input_sha256=input_sha256,
                duration_ms=duration_ms,
            )
        except ProviderOutputError:
            await self.store.fail(job.id, job.lease_token, "invalid_provider_output")
        except ProviderUnavailableError:
            await self.store.fail(job.id, job.lease_token, "provider_unavailable")
        except WorkerPersistenceError:
            logger.warning(
                "worker persistence interrupted; lease left for safe reclaim",
                extra={"job_id": job.id},
            )
        except Exception:
            logger.exception("analysis job failed", extra={"job_id": job.id})
            with contextlib.suppress(Exception):
                await self.store.fail(job.id, job.lease_token, "worker_error")
        finally:
            heartbeat.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await heartbeat
        return True

    async def _heartbeat(self, job: WorkerJob) -> None:
        while True:
            await asyncio.sleep(30)
            if not await self.store.heartbeat(job.id, job.lease_token):
                raise RuntimeError("analysis lease expired")

    async def run(self, stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                processed = await self.process_once()
            except WorkerPersistenceError:
                logger.exception("worker poll failed")
                processed = False
            if not processed:
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(stop.wait(), timeout=self.poll_seconds)

    async def close(self) -> None:
        await self.adapter.close()
        await self.store.close()


def build_worker(settings: Settings) -> AnalysisWorker:
    if not settings.gemini_api_key:
        raise RuntimeError("Gemini API key is not configured")
    repository_root = Path(__file__).resolve().parents[3]
    configuration = load_hosted_configuration(
        repository_root / "artifacts/manifests/hosted-baseline.v1.json",
        repository_root=repository_root,
    )
    adapter = GeminiAdapter(configuration, api_key=settings.gemini_api_key)
    return AnalysisWorker(
        store=SupabaseWorkerStore(settings),
        adapter=adapter,
        manifest_sha256=configuration.manifest_sha256,
    )
