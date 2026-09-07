from __future__ import annotations

from typing import Any

import pytest

from app.adapters.base import AnalysisInput, ProviderUnavailableError
from app.contracts import AnalysisResult
from app.worker import AnalysisWorker, WorkerJob, WorkerPersistenceError, WorkerReport


def _result() -> AnalysisResult:
    return AnalysisResult.model_validate(
        {
            "schema_version": "1.0",
            "sif_label": "no",
            "abstain_reasons": [],
            "model_score": None,
            "score_kind": "none",
            "relevant_rule_ids": [],
            "rules_assessment": "complete",
            "unassessed_rule_ids": [],
            "rule_scores": None,
            "precursors": [],
            "barriers": [],
            "evidence": [
                {
                    "id": "e1",
                    "field": "narrative",
                    "quote": "The barrier remained in place",
                    "method": "llm_extracted",
                }
            ],
            "missing_information": [],
            "summary": "No credible serious-injury exposure is described in the submitted text.",
            "references": [],
            "review_status": "pending",
            "provenance": {
                "engine_mode": "hosted_baseline",
                "model_id": "gemini-2.5-flash",
                "model_revision": "provider_revision_unavailable",
                "prompt_version": "sif-analysis-v1",
                "label_guide_version": "sif-pilot-v1",
                "auxiliary_models": [],
                "inference_is_live": True,
            },
        }
    )


class FakeWorkerStore:
    def __init__(self, *, finalize_unavailable: bool = False) -> None:
        self.next_job: WorkerJob | None = WorkerJob(
            id="job-1",
            report_id="report-1",
            engine_mode="hosted_baseline",
            lease_token="lease-1",
        )
        self.finalized: dict[str, Any] | None = None
        self.failed_code: str | None = None
        self.finalize_unavailable = finalize_unavailable

    async def claim(self) -> WorkerJob | None:
        job, self.next_job = self.next_job, None
        return job

    async def get_report(self, report_id: str) -> WorkerReport:
        assert report_id == "report-1"
        return WorkerReport(
            normalized_input="The barrier remained in place during the completed task.",
            activity="Inspection",
        )

    async def heartbeat(self, job_id: str, lease_token: str) -> bool:
        return True

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
        if self.finalize_unavailable:
            raise WorkerPersistenceError("response lost")
        self.finalized = {
            "job_id": job_id,
            "lease_token": lease_token,
            "result": result,
            "manifest": model_manifest_sha256,
            "input_sha256": input_sha256,
            "duration_ms": duration_ms,
        }
        return "analysis-1"

    async def fail(self, job_id: str, lease_token: str, error_code: str) -> bool:
        self.failed_code = error_code
        return True

    async def close(self) -> None:
        return None


class FakeAdapter:
    def __init__(self, *, unavailable: bool = False) -> None:
        self.unavailable = unavailable
        self.received: AnalysisInput | None = None

    async def health(self) -> bool:
        return True

    async def analyze(self, value: AnalysisInput) -> AnalysisResult:
        self.received = value
        if self.unavailable:
            raise ProviderUnavailableError("provider failed")
        return _result()

    async def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_worker_claims_runs_and_finalizes_a_versioned_result() -> None:
    store = FakeWorkerStore()
    adapter = FakeAdapter()
    worker = AnalysisWorker(store, adapter, "a" * 64)

    assert await worker.process_once() is True

    assert adapter.received == AnalysisInput(
        narrative="The barrier remained in place during the completed task.",
        activity="Inspection",
    )
    assert store.finalized is not None
    assert store.finalized["manifest"] == "a" * 64
    assert len(store.finalized["input_sha256"]) == 64
    assert store.finalized["result"]["provenance"]["inference_is_live"] is True
    assert store.failed_code is None


@pytest.mark.asyncio
async def test_provider_failure_becomes_failed_job_not_unknown() -> None:
    store = FakeWorkerStore()
    worker = AnalysisWorker(store, FakeAdapter(unavailable=True), "a" * 64)

    assert await worker.process_once() is True

    assert store.failed_code == "provider_unavailable"
    assert store.finalized is None


@pytest.mark.asyncio
async def test_lost_finalize_response_leaves_lease_for_safe_reclaim() -> None:
    store = FakeWorkerStore(finalize_unavailable=True)
    worker = AnalysisWorker(store, FakeAdapter(), "a" * 64)

    assert await worker.process_once() is True

    assert store.failed_code is None
    assert store.finalized is None
