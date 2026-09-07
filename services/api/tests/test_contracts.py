import pytest
from pydantic import ValidationError

from app.contracts import CANONICAL_RULE_IDS, AnalysisResult, ModelOutputSubset, ReportCreate
from app.validation import ModelOutputValidationError, verify_model_output


def valid_model_output() -> dict[str, object]:
    return {
        "sif_label": "yes",
        "relevant_rule_ids": ["line_of_fire", "safe_mechanical_lifting"],
        "rules_assessment": "complete",
        "unassessed_rule_ids": [],
        "precursors": [
            {
                "tag": "overhead_load_exposure",
                "evidence_quote": "A suspended load passed directly above a worker",
            }
        ],
        "barriers": [
            {
                "tag": "separation_from_suspended_load",
                "state": "failed",
                "evidence_quote": "A suspended load passed directly above a worker",
            }
        ],
        "evidence_quotes": ["A suspended load passed directly above a worker"],
        "missing_information": [],
        "summary": "A worker was exposed beneath a suspended load.",
        "reference_passage_ids": ["curated-lifting-001"],
    }


def valid_analysis_result() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "sif_label": "yes",
        "abstain_reasons": [],
        "model_score": None,
        "score_kind": "none",
        "relevant_rule_ids": ["line_of_fire", "safe_mechanical_lifting"],
        "rules_assessment": "complete",
        "unassessed_rule_ids": [],
        "rule_scores": None,
        "precursors": [{"tag": "overhead_load_exposure", "evidence_ids": ["e1"]}],
        "barriers": [
            {
                "tag": "separation_from_suspended_load",
                "state": "failed",
                "evidence_ids": ["e1"],
            }
        ],
        "evidence": [
            {
                "id": "e1",
                "field": "narrative",
                "quote": "A suspended load passed directly above a worker",
                "method": "llm_extracted",
                "occurrence": 0,
            }
        ],
        "missing_information": [],
        "summary": "Potential serious harm requires reviewer attention.",
        "references": [{"source_id": "S25", "passage_id": "curated-lifting-001"}],
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


def test_report_input_preserves_narrative_and_rejects_unknown_fields() -> None:
    narrative = "  No injury occurred, but the suspended load crossed the access route.  "
    parsed = ReportCreate.model_validate({"narrative": narrative, "site": None})
    assert parsed.narrative == narrative
    assert parsed.site is None

    with pytest.raises(ValidationError, match="owner_id"):
        ReportCreate.model_validate({"narrative": narrative, "owner_id": "client-controlled"})


def test_full_result_parses_and_rejects_invalid_provenance() -> None:
    parsed = AnalysisResult.model_validate(valid_analysis_result())
    assert parsed.provenance.model_id == "gemini-2.5-flash"
    assert parsed.evidence[0].quote.startswith("A suspended load")

    invalid = valid_analysis_result()
    assert isinstance(invalid["provenance"], dict)
    invalid["provenance"]["model_id"] = "CONFIGURED_AT_RUNTIME"
    with pytest.raises(ValidationError, match="placeholders"):
        AnalysisResult.model_validate(invalid)


@pytest.mark.parametrize("narrative", ["", "   ", "too short"])
def test_report_input_rejects_blank_or_short_narratives(narrative: str) -> None:
    with pytest.raises(ValidationError):
        ReportCreate.model_validate({"narrative": narrative})


def test_multiple_rules_and_complete_empty_rules_are_distinct() -> None:
    multiple = ModelOutputSubset.model_validate(valid_model_output())
    assert [rule.value for rule in multiple.relevant_rule_ids] == [
        "line_of_fire",
        "safe_mechanical_lifting",
    ]

    no_rules = valid_model_output() | {"relevant_rule_ids": []}
    parsed_no_rules = ModelOutputSubset.model_validate(no_rules)
    assert parsed_no_rules.relevant_rule_ids == []
    assert parsed_no_rules.rules_assessment.value == "complete"


def test_unknown_rule_assessment_requires_all_rules_unassessed() -> None:
    unknown = valid_model_output() | {
        "sif_label": "unknown",
        "relevant_rule_ids": [],
        "rules_assessment": "unknown",
        "unassessed_rule_ids": [rule.value for rule in CANONICAL_RULE_IDS],
    }
    parsed = ModelOutputSubset.model_validate(unknown)
    assert tuple(parsed.unassessed_rule_ids) == CANONICAL_RULE_IDS

    unknown["unassessed_rule_ids"] = ["driving"]
    with pytest.raises(ValidationError, match="full taxonomy"):
        ModelOutputSubset.model_validate(unknown)


def test_duplicate_or_invalid_rule_ids_fail() -> None:
    duplicate = valid_model_output() | {
        "relevant_rule_ids": ["line_of_fire", "line_of_fire"]
    }
    with pytest.raises(ValidationError, match="duplicates"):
        ModelOutputSubset.model_validate(duplicate)

    invalid = valid_model_output() | {"relevant_rule_ids": ["made_up_rule"]}
    with pytest.raises(ValidationError):
        ModelOutputSubset.model_validate(invalid)


def test_evidence_and_references_are_verified_against_supplied_data() -> None:
    narrative = "A suspended load passed directly above a worker during the lift."
    parsed = ModelOutputSubset.model_validate(valid_model_output())
    verified = verify_model_output(
        parsed,
        narrative=narrative,
        activity="Mechanical lifting",
        allowed_passage_ids={"curated-lifting-001"},
    )
    assert verified.quote_occurrences == {
        "A suspended load passed directly above a worker": 1
    }

    fabricated_quote = ModelOutputSubset.model_validate(
        valid_model_output() | {"evidence_quotes": ["A fabricated sentence"]}
    )
    with pytest.raises(ModelOutputValidationError, match="unsupported evidence"):
        verify_model_output(
            fabricated_quote,
            narrative=narrative,
            activity=None,
            allowed_passage_ids={"curated-lifting-001"},
        )

    unsupported_reference = ModelOutputSubset.model_validate(
        valid_model_output() | {"reference_passage_ids": ["invented-passage"]}
    )
    with pytest.raises(ModelOutputValidationError, match="unsupported reference"):
        verify_model_output(
            unsupported_reference,
            narrative=narrative,
            activity=None,
            allowed_passage_ids={"curated-lifting-001"},
        )
