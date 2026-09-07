from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from google import genai
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.adapters.base import (
    AnalysisInput,
    ProviderOutputError,
    ProviderUnavailableError,
)
from app.contracts import (
    CANONICAL_RULE_IDS,
    AnalysisResult,
    Barrier,
    EngineMode,
    Evidence,
    EvidenceMethod,
    ModelOutputSubset,
    Precursor,
    Provenance,
    ReferenceCitation,
    RulesAssessment,
    ScoreKind,
    SifLabel,
)
from app.validation import ModelOutputValidationError, verify_model_output


class InteractionClient(Protocol):
    async def create(self, **kwargs: Any) -> Any: ...


class ReferenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str
    title: str
    url: str | None
    accessed_at: str
    rights_status: str


class ReferencePassage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passage_id: str
    source_id: str
    kind: str
    text: str


class ReferenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bundle_version: str
    rubric_version: str
    status: str
    intended_use: str
    rights_note: str
    sources: list[ReferenceSource]
    passages: list[ReferencePassage]

    @field_validator("passages")
    @classmethod
    def unique_passages(cls, passages: list[ReferencePassage]) -> list[ReferencePassage]:
        ids = [passage.passage_id for passage in passages]
        if len(ids) != len(set(ids)):
            raise ValueError("reference passage IDs must be unique")
        return passages


class HostedManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    manifest_version: str
    engine_mode: str
    provider: str
    model_id: str
    model_revision: str
    schema_version: str
    prompt_version: str
    prompt_path: str
    prompt_sha256: str
    label_guide_version: str
    reference_bundle_version: str
    reference_bundle_path: str
    reference_bundle_sha256: str
    normalization_version: str
    taxonomy_order: list[str]
    response_schema: str
    provider_timeout_seconds: int = Field(gt=0, le=45)
    fallback_enabled: bool
    evaluation_status: str
    live_smoke_status: str
    created_at: str


@dataclass(frozen=True)
class LoadedHostedConfiguration:
    manifest: HostedManifest
    manifest_sha256: str
    system_prompt: str
    references: ReferenceBundle


class _SdkInteractionClient:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    async def create(self, **kwargs: Any) -> Any:
        return await self._client.aio.interactions.create(**kwargs)

    async def close(self) -> None:
        await self._client.aio.aclose()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _extract_json_payload(output_text: str) -> str:
    """Unwrap the conventional Markdown fence some Gemini responses include.

    The result is still parsed and validated against the strict response schema;
    this only removes presentation markup around an otherwise valid JSON object.
    """

    match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n?```\s*", output_text, re.DOTALL)
    return match.group(1) if match else output_text


def load_hosted_configuration(
    manifest_path: Path, *, repository_root: Path
) -> LoadedHostedConfiguration:
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = HostedManifest.model_validate_json(manifest_bytes)
        prompt_path = repository_root / manifest.prompt_path
        reference_path = repository_root / manifest.reference_bundle_path
        prompt_bytes = prompt_path.read_bytes()
        reference_bytes = reference_path.read_bytes()
        if _sha256_bytes(prompt_bytes) != manifest.prompt_sha256:
            raise ValueError("system prompt hash does not match the manifest")
        if _sha256_bytes(reference_bytes) != manifest.reference_bundle_sha256:
            raise ValueError("reference bundle hash does not match the manifest")
        references = ReferenceBundle.model_validate_json(reference_bytes)
    except (OSError, ValidationError, ValueError) as exc:
        raise ProviderUnavailableError("hosted model configuration is invalid") from exc

    if manifest.taxonomy_order != [rule.value for rule in CANONICAL_RULE_IDS]:
        raise ProviderUnavailableError("manifest taxonomy does not match the API contract")
    if manifest.response_schema != ModelOutputSubset.__name__:
        raise ProviderUnavailableError("manifest response schema is unsupported")
    if references.bundle_version != manifest.reference_bundle_version:
        raise ProviderUnavailableError("reference bundle version does not match the manifest")
    return LoadedHostedConfiguration(
        manifest=manifest,
        manifest_sha256=_sha256_bytes(manifest_bytes),
        system_prompt=prompt_bytes.decode("utf-8"),
        references=references,
    )


class GeminiAdapter:
    def __init__(
        self,
        configuration: LoadedHostedConfiguration,
        *,
        api_key: str | None = None,
        interaction_client: InteractionClient | None = None,
    ) -> None:
        if interaction_client is None and not api_key:
            raise ProviderUnavailableError("Gemini API key is not configured")
        self.configuration = configuration
        self._client = interaction_client or _SdkInteractionClient(api_key or "")

    async def health(self) -> bool:
        return bool(self.configuration.system_prompt and self.configuration.references.passages)

    async def analyze(self, value: AnalysisInput) -> AnalysisResult:
        manifest = self.configuration.manifest
        request_data = {
            "narrative": value.narrative,
            "activity": value.activity,
            "rubric_version": manifest.label_guide_version,
            "allowed_rule_ids": manifest.taxonomy_order,
            "reference_passages": [
                {
                    "passage_id": passage.passage_id,
                    "text": passage.text,
                }
                for passage in self.configuration.references.passages
            ],
        }
        request = {
            "model": manifest.model_id,
            "system_instruction": self.configuration.system_prompt,
            "input": json.dumps(request_data, ensure_ascii=False, separators=(",", ":")),
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": ModelOutputSubset.model_json_schema(mode="serialization"),
            },
            "store": False,
            "timeout": float(manifest.provider_timeout_seconds),
        }
        allowed_passage_ids = {
            passage.passage_id for passage in self.configuration.references.passages
        }
        last_error: Exception | None = None
        for _ in range(3):
            try:
                interaction = await self._client.create(**request)
            except Exception as exc:
                raise ProviderUnavailableError("Gemini inference request failed") from exc

            output_text = getattr(interaction, "output_text", None)
            if not isinstance(output_text, str) or not output_text:
                last_error = ProviderOutputError("Gemini returned no structured output")
                continue
            try:
                provider_output = ModelOutputSubset.model_validate_json(
                    _extract_json_payload(output_text)
                )
                verify_model_output(
                    provider_output,
                    narrative=value.narrative,
                    activity=value.activity,
                    allowed_passage_ids=allowed_passage_ids,
                )
            except (ValidationError, ModelOutputValidationError) as exc:
                last_error = exc
                continue
            return self._to_analysis_result(provider_output, value)

        raise ProviderOutputError("Gemini returned invalid or ungrounded output") from last_error

    def _to_analysis_result(
        self, output: ModelOutputSubset, value: AnalysisInput
    ) -> AnalysisResult:
        quotes = list(
            dict.fromkeys(
                [
                    *output.evidence_quotes,
                    *(item.evidence_quote for item in output.precursors),
                    *(item.evidence_quote for item in output.barriers),
                ]
            )
        )
        evidence: list[Evidence] = []
        quote_to_id: dict[str, str] = {}
        for index, quote in enumerate(quotes, start=1):
            evidence_id = f"e{index}"
            quote_to_id[quote] = evidence_id
            evidence.append(
                Evidence(
                    id=evidence_id,
                    field="narrative" if quote in value.narrative else "activity",
                    quote=quote,
                    method=EvidenceMethod.LLM_EXTRACTED,
                    occurrence=0,
                )
            )

        sif_label = output.sif_label
        abstain_reasons: list[str] = []
        if sif_label == SifLabel.UNKNOWN:
            abstain_reasons = [
                "missing_information" if output.missing_information else "model_abstention"
            ]
        elif not evidence:
            sif_label = SifLabel.UNKNOWN
            abstain_reasons = ["evidence_unavailable"]

        rules_assessment = output.rules_assessment
        relevant_rule_ids = output.relevant_rule_ids
        unassessed_rule_ids = output.unassessed_rule_ids
        if sif_label == SifLabel.UNKNOWN and abstain_reasons == ["evidence_unavailable"]:
            rules_assessment = RulesAssessment.UNKNOWN
            relevant_rule_ids = []
            unassessed_rule_ids = list(CANONICAL_RULE_IDS)

        passage_sources = {
            passage.passage_id: passage.source_id
            for passage in self.configuration.references.passages
        }
        manifest = self.configuration.manifest
        return AnalysisResult(
            schema_version="1.0",
            sif_label=sif_label,
            abstain_reasons=abstain_reasons,
            model_score=None,
            score_kind=ScoreKind.NONE,
            relevant_rule_ids=relevant_rule_ids,
            rules_assessment=rules_assessment,
            unassessed_rule_ids=unassessed_rule_ids,
            rule_scores=None,
            precursors=[
                Precursor(tag=item.tag, evidence_ids=[quote_to_id[item.evidence_quote]])
                for item in output.precursors
            ],
            barriers=[
                Barrier(
                    tag=item.tag,
                    state=item.state,
                    evidence_ids=[quote_to_id[item.evidence_quote]],
                )
                for item in output.barriers
            ],
            evidence=evidence,
            missing_information=output.missing_information,
            summary=output.summary,
            references=[
                ReferenceCitation(
                    source_id=passage_sources[passage_id], passage_id=passage_id
                )
                for passage_id in output.reference_passage_ids
            ],
            review_status="pending",
            provenance=Provenance(
                engine_mode=EngineMode.HOSTED_BASELINE,
                model_id=manifest.model_id,
                model_revision=manifest.model_revision,
                prompt_version="sif-analysis-v1",
                label_guide_version="sif-pilot-v1",
                auxiliary_models=[],
                inference_is_live=True,
            ),
        )

    async def close(self) -> None:
        close = getattr(self._client, "close", None)
        if close is not None:
            await close()
