from __future__ import annotations

import httpx
import pytest

from app.config import Settings
from app.contracts import ReportCreate
from app.persistence import PersistenceNotFoundError, SupabaseReportStore

NARRATIVE = "A worker stood near the suspended load while the lift crossed the access route."


@pytest.mark.asyncio
async def test_report_rpc_uses_caller_token_and_never_sends_owner_id() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://project.supabase.co/rest/v1/rpc/create_report_v1"
        assert request.headers["apikey"] == "public-anon-key"
        assert request.headers["authorization"] == "Bearer caller-token"
        payload = request.content.decode("utf-8")
        assert "owner_id" not in payload
        assert NARRATIVE in payload
        return httpx.Response(
            200,
            json=[
                {
                    "report_id": "4f7551cb-1b56-4d3a-bc87-b4c722840ca8",
                    "report_version": 1,
                    "replayed": False,
                }
            ],
        )

    settings = Settings(
        supabase_url="https://project.supabase.co",
        supabase_anon_key="public-anon-key",
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        store = SupabaseReportStore(settings, client)
        created = await store.create_report(
            ReportCreate(narrative=NARRATIVE),
            idempotency_key="report-key-1",
            access_token="caller-token",
        )

    assert created.version == 1
    assert created.replayed is False


@pytest.mark.asyncio
async def test_rls_filtered_report_is_returned_as_not_found() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer caller-token"
        return httpx.Response(200, json=[])

    settings = Settings(
        supabase_url="https://project.supabase.co",
        supabase_anon_key="public-anon-key",
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        store = SupabaseReportStore(settings, client)
        with pytest.raises(PersistenceNotFoundError):
            await store.get_report(
                "4f7551cb-1b56-4d3a-bc87-b4c722840ca8",
                access_token="caller-token",
            )
