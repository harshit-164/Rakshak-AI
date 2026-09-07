from __future__ import annotations

import math
from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "1.0"
LABEL_GUIDE_VERSION = "sif-pilot-v1"
PROMPT_VERSION = "sif-analysis-v1"
NORMALIZATION_VERSION = "input-normalization-v1"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RuleId(StrEnum):
    BYPASSING_SAFETY_CONTROLS = "bypassing_safety_controls"
    CONFINED_SPACE = "confined_space"
    DRIVING = "driving"
    ENERGY_ISOLATION = "energy_isolation"
    HOT_WORK = "hot_work"
    LINE_OF_FIRE = "line_of_fire"
    SAFE_MECHANICAL_LIFTING = "safe_mechanical_lifting"
    WORK_AUTHORISATION = "work_authorisation"
    WORKING_AT_HEIGHT = "working_at_height"


CANONICAL_RULE_IDS = tuple(RuleId)


class SifLabel(StrEnum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class RulesAssessment(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class BarrierState(StrEnum):
    FAILED = "failed"
    MISSING = "missing"
    PRESENT = "present"
    UNKNOWN = "unknown"


class EvidenceMethod(StrEnum):
    LLM_EXTRACTED = "llm_extracted"
    RULE_MATCHED = "rule_matched"
    REVIEWER = "reviewer"


class ScoreKind(StrEnum):
    NONE = "none"
    UNCALIBRATED = "uncalibrated_model_score"
    CALIBRATED = "calibrated_score"


class EngineMode(StrEnum):
    HOSTED_BASELINE = "hosted_baseline"
    ENCODER = "encoder"
    QWEN_ADAPTER = "qwen_adapter"
    RECORDED_SAMPLE = "recorded_sample"


class AnalysisJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def _unique_rule_ids(values: list[RuleId]) -> list[RuleId]:
    if len(values) != len(set(values)):
        raise ValueError("rule IDs must not contain duplicates")
    return sorted(values, key=CANONICAL_RULE_IDS.index)


class RulesPartitionMixin(BaseModel):
    relevant_rule_ids: list[RuleId]
    rules_assessment: RulesAssessment
    unassessed_rule_ids: list[RuleId]

    @field_validator("relevant_rule_ids", "unassessed_rule_ids")
    @classmethod
    def validate_rule_list(cls, values: list[RuleId]) -> list[RuleId]:
        return _unique_rule_ids(values)

    @model_validator(mode="after")
    def validate_rule_partition(self) -> Self:
        relevant = set(self.relevant_rule_ids)
        unassessed = set(self.unassessed_rule_ids)
        if relevant & unassessed:
            raise ValueError("a relevant rule cannot also be unassessed")
        if self.rules_assessment == RulesAssessment.COMPLETE and unassessed:
            raise ValueError("complete assessment cannot contain unassessed rule IDs")
        if self.rules_assessment == RulesAssessment.PARTIAL and not unassessed:
            raise ValueError("partial assessment must list every unassessed rule ID")
        if self.rules_assessment == RulesAssessment.UNKNOWN:
            if relevant:
                raise ValueError("unknown rule assessment cannot assert relevant rules")
            if tuple(self.unassessed_rule_ids) != CANONICAL_RULE_IDS:
                raise ValueError("unknown rule assessment must mark the full taxonomy unassessed")
        return self


class ModelPrecursor(StrictModel):
    tag: Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")]
    evidence_quote: Annotated[str, Field(min_length=1, max_length=8000)]


class ModelBarrier(StrictModel):
    tag: Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")]
    state: BarrierState
    evidence_quote: Annotated[str, Field(min_length=1, max_length=8000)]


class ModelOutputSubset(StrictModel, RulesPartitionMixin):
    sif_label: SifLabel
    precursors: list[ModelPrecursor] = Field(max_length=30)
    barriers: list[ModelBarrier] = Field(max_length=30)
    evidence_quotes: list[Annotated[str, Field(min_length=1, max_length=8000)]] = Field(
        max_length=50
    )
    missing_information: list[Annotated[str, Field(min_length=1, max_length=240)]] = Field(
        max_length=30
    )
    summary: Annotated[str, Field(min_length=1, max_length=800)]
    reference_passage_ids: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        max_length=30
    )

    @field_validator("evidence_quotes", "reference_passage_ids")
    @classmethod
    def validate_unique_strings(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("values must not contain duplicates")
        return values


class Evidence(StrictModel):
    id: Annotated[str, Field(pattern=r"^e[1-9][0-9]*$")]
    field: Literal["narrative", "activity"]
    quote: Annotated[str, Field(min_length=1, max_length=8000)]
    method: EvidenceMethod
    occurrence: Annotated[int, Field(ge=0)] = 0


class Precursor(StrictModel):
    tag: Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")]
    evidence_ids: list[str] = Field(min_length=1, max_length=20)


class Barrier(StrictModel):
    tag: Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")]
    state: BarrierState
    evidence_ids: list[str] = Field(min_length=1, max_length=20)


class ReferenceCitation(StrictModel):
    source_id: Annotated[str, Field(min_length=1, max_length=40)]
    passage_id: Annotated[str, Field(min_length=1, max_length=120)]


class AuxiliaryModel(StrictModel):
    purpose: Annotated[str, Field(min_length=1, max_length=80)]
    provider: Annotated[str, Field(min_length=1, max_length=80)]
    model_id: Annotated[str, Field(min_length=1, max_length=160)]
    revision: Annotated[str, Field(min_length=1, max_length=160)]


class Provenance(StrictModel):
    engine_mode: EngineMode
    model_id: Annotated[str, Field(min_length=1, max_length=160)]
    model_revision: Annotated[str, Field(min_length=1, max_length=160)]
    prompt_version: Literal["sif-analysis-v1"]
    label_guide_version: Literal["sif-pilot-v1"]
    auxiliary_models: list[AuxiliaryModel] = Field(max_length=5)
    inference_is_live: bool

    @field_validator("model_id", "model_revision")
    @classmethod
    def reject_documentation_placeholders(cls, value: str) -> str:
        if value in {"CONFIGURED_AT_RUNTIME", "RECORDED_AT_RUNTIME"}:
            raise ValueError("documentation placeholders are not valid runtime provenance")
        return value


class AnalysisResult(StrictModel, RulesPartitionMixin):
    schema_version: Literal["1.0"]
    sif_label: SifLabel
    abstain_reasons: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        max_length=20
    )
    model_score: Annotated[float, Field(ge=0, le=1)] | None
    score_kind: ScoreKind
    rule_scores: dict[RuleId, Annotated[float, Field(ge=0, le=1)] | None] | None
    precursors: list[Precursor] = Field(max_length=30)
    barriers: list[Barrier] = Field(max_length=30)
    evidence: list[Evidence] = Field(max_length=50)
    missing_information: list[Annotated[str, Field(min_length=1, max_length=240)]] = Field(
        max_length=30
    )
    summary: Annotated[str, Field(min_length=1, max_length=800)]
    references: list[ReferenceCitation] = Field(max_length=30)
    review_status: Literal["pending", "reviewed"]
    provenance: Provenance

    @field_validator("model_score")
    @classmethod
    def validate_finite_score(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("model score must be finite")
        return value

    @model_validator(mode="after")
    def validate_result_relationships(self) -> Self:
        if self.score_kind == ScoreKind.NONE and self.model_score is not None:
            raise ValueError("score_kind none requires a null model_score")
        if self.score_kind != ScoreKind.NONE and self.model_score is None:
            raise ValueError("a non-none score_kind requires model_score")
        if self.sif_label == SifLabel.UNKNOWN and not self.abstain_reasons:
            raise ValueError("unknown SIF label requires at least one abstain reason")
        if self.sif_label != SifLabel.UNKNOWN and self.abstain_reasons:
            raise ValueError("definitive SIF label cannot contain abstain reasons")

        evidence_ids = [item.id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence IDs must be unique")
        known_evidence_ids = set(evidence_ids)
        for precursor in self.precursors:
            if not set(precursor.evidence_ids) <= known_evidence_ids:
                raise ValueError("precursor refers to missing evidence")
        for barrier in self.barriers:
            if not set(barrier.evidence_ids) <= known_evidence_ids:
                raise ValueError("barrier refers to missing evidence")
        if self.rule_scores is not None and set(self.rule_scores) != set(CANONICAL_RULE_IDS):
            raise ValueError("rule_scores must contain the complete canonical taxonomy")
        return self


class ReportCreate(StrictModel):
    narrative: Annotated[str, Field(min_length=20, max_length=8000)]
    activity: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    site: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    report_date: date | None = None
    is_synthetic: bool = False

    @field_validator("narrative")
    @classmethod
    def reject_blank_narrative(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("narrative cannot be blank")
        return value

    @field_validator("activity", "site")
    @classmethod
    def reject_blank_optional_text(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("optional text must be null or contain non-whitespace characters")
        return value


class ReportCreated(StrictModel):
    report_id: str
    version: Annotated[int, Field(gt=0)]
    replayed: bool


class AnalysisJobCreate(StrictModel):
    engine_mode: EngineMode = EngineMode.HOSTED_BASELINE

    @field_validator("engine_mode")
    @classmethod
    def reject_recorded_sample(cls, value: EngineMode) -> EngineMode:
        if value == EngineMode.RECORDED_SAMPLE:
            raise ValueError("recorded samples cannot analyze newly submitted reports")
        return value


class AnalysisJobCreated(StrictModel):
    job_id: str
    status: AnalysisJobStatus
    replayed: bool


class JobStatusResponse(StrictModel):
    job_id: str
    report_id: str
    status: AnalysisJobStatus
    attempt_count: Annotated[int, Field(ge=0, le=2)]
    error_code: str | None
    analysis_id: str | None
    updated_at: datetime


class ReportRecord(StrictModel):
    id: str
    report_group_id: str
    version: Annotated[int, Field(gt=0)]
    narrative: str
    activity: str | None
    site: str | None
    report_date: date | None
    is_synthetic: bool
    created_at: datetime


class StoredAnalysis(StrictModel):
    id: str
    job_id: str
    result: AnalysisResult
    duration_ms: Annotated[int, Field(ge=0)]
    created_at: datetime


class ReportDetail(StrictModel):
    report: ReportRecord
    analyses: list[StoredAnalysis]


class CapabilitiesLimits(StrictModel):
    narrative_min_codepoints: int
    narrative_max_codepoints: int
    max_api_body_bytes: int
    max_active_jobs: int


class EngineCapability(StrictModel):
    engine_mode: EngineMode
    display_name: str
    available: bool
    live_inference: bool


class CapabilitiesResponse(StrictModel):
    schema_version: Literal["1.0"]
    rubric_version: Literal["sif-pilot-v1"]
    current_model_display_name: str
    engines: list[EngineCapability]
    limits: CapabilitiesLimits
    canonical_rule_ids: list[RuleId]


CONTRACT_MODELS: tuple[type[BaseModel], ...] = (
    AnalysisResult,
    AnalysisJobCreate,
    AnalysisJobCreated,
    CapabilitiesResponse,
    JobStatusResponse,
    ModelOutputSubset,
    ReportCreate,
    ReportCreated,
    ReportDetail,
)
