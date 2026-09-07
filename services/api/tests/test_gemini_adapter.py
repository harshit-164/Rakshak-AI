import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.adapters.base import AnalysisInput, ProviderOutputError, ProviderUnavailableError
from app.adapters.gemini import GeminiAdapter, load_hosted_configuration

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPOSITORY_ROOT / "artifacts" / "manifests" / "hosted-baseline.v1.json"


def provider_result() -> dict[str, object]:
    quote = "A suspended load passed directly above a worker"
    return {
        "sif_label": "yes",
        "relevant_rule_ids": ["line_of_fire", "safe_mechanical_lifting"],
        "rules_assessment": "complete",
        "unassessed_rule_ids": [],
        "precursors": [{"tag": "overhead_load_exposure", "evidence_quote": quote}],
        "barriers": [
            {
                "tag": "separation_from_suspended_load",
                "state": "failed",
                "evidence_quote": quote,
            }
        ],
        "evidence_quotes": [quote],
        "missing_information": [],
        "summary": "A worker was exposed beneath a suspended load.",
        "reference_passage_ids": ["rule-line-of-fire-001", "rule-mechanical-lifting-001"],
    }


class FakeInteractionClient:
    def __init__(self, output: dict[str, object] | None = None, error: Exception | None = None):
        self.output = output
        self.error = error
        self.request: dict[str, Any] | None = None

    async def create(self, **kwargs: Any) -> Any:
        self.request = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(output_text=json.dumps(self.output))


@pytest.mark.asyncio
async def test_gemini_request_is_schema_constrained_and_result_is_grounded() -> None:
    configuration = load_hosted_configuration(MANIFEST_PATH, repository_root=REPOSITORY_ROOT)
    client = FakeInteractionClient(provider_result())
    adapter = GeminiAdapter(configuration, interaction_client=client)
    value = AnalysisInput(
        narrative="A suspended load passed directly above a worker during the lift.",
        activity="Mechanical lifting",
    )

    result = await adapter.analyze(value)

    assert client.request is not None
    assert client.request["model"] == "gemini-2.5-flash"
    assert client.request["store"] is False
    assert client.request["timeout"] == 45.0
    assert client.request["response_format"]["mime_type"] == "application/json"
    assert client.request["response_format"]["schema"]["title"] == "ModelOutputSubset"
    sent_input = json.loads(client.request["input"])
    assert sent_input["narrative"] == value.narrative
    assert "site" not in sent_input
    assert "report_date" not in sent_input
    assert len(sent_input["allowed_rule_ids"]) == 9

    assert result.sif_label.value == "yes"
    assert result.evidence[0].quote in value.narrative
    assert result.provenance.model_id == "gemini-2.5-flash"
    assert result.provenance.model_revision == "provider_revision_unavailable"
    assert [reference.passage_id for reference in result.references] == [
        "rule-line-of-fire-001",
        "rule-mechanical-lifting-001",
    ]


@pytest.mark.asyncio
async def test_fabricated_evidence_is_a_provider_output_failure_not_unknown() -> None:
    configuration = load_hosted_configuration(MANIFEST_PATH, repository_root=REPOSITORY_ROOT)
    invalid = provider_result() | {"evidence_quotes": ["This sentence was invented"]}
    client = FakeInteractionClient(invalid)
    adapter = GeminiAdapter(configuration, interaction_client=client)

    with pytest.raises(ProviderOutputError, match="invalid or ungrounded"):
        await adapter.analyze(
            AnalysisInput(
                narrative="A suspended load passed directly above a worker during the lift.",
                activity=None,
            )
        )


@pytest.mark.asyncio
async def test_provider_outage_is_failure_not_safety_unknown() -> None:
    configuration = load_hosted_configuration(MANIFEST_PATH, repository_root=REPOSITORY_ROOT)
    client = FakeInteractionClient(error=TimeoutError("provider timeout"))
    adapter = GeminiAdapter(configuration, interaction_client=client)

    with pytest.raises(ProviderUnavailableError, match="request failed"):
        await adapter.analyze(
            AnalysisInput(
                narrative="A suspended load passed directly above a worker during the lift.",
                activity=None,
            )
        )
