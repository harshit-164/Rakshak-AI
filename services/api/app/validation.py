from dataclasses import dataclass

from app.contracts import ModelOutputSubset


@dataclass(frozen=True)
class VerifiedModelOutput:
    output: ModelOutputSubset
    quote_occurrences: dict[str, int]


class ModelOutputValidationError(ValueError):
    """Raised when syntactically valid provider output is not grounded in supplied input."""


def verify_model_output(
    output: ModelOutputSubset,
    *,
    narrative: str,
    activity: str | None,
    allowed_passage_ids: set[str],
) -> VerifiedModelOutput:
    searchable_fields = (narrative, activity or "")
    quote_occurrences: dict[str, int] = {}

    for quote in output.evidence_quotes:
        occurrences = sum(field.count(quote) for field in searchable_fields)
        if occurrences == 0:
            raise ModelOutputValidationError(f"unsupported evidence quote: {quote!r}")
        quote_occurrences[quote] = occurrences

    for precursor in output.precursors:
        if not any(precursor.evidence_quote in field for field in searchable_fields):
            raise ModelOutputValidationError(
                "unsupported evidence quote for "
                f"{precursor.tag!r}: {precursor.evidence_quote!r}"
            )
    for barrier in output.barriers:
        if not any(barrier.evidence_quote in field for field in searchable_fields):
            raise ModelOutputValidationError(
                f"unsupported evidence quote for {barrier.tag!r}: {barrier.evidence_quote!r}"
            )

    unsupported_passages = set(output.reference_passage_ids) - allowed_passage_ids
    if unsupported_passages:
        rendered = ", ".join(sorted(unsupported_passages))
        raise ModelOutputValidationError(f"unsupported reference passage IDs: {rendered}")

    return VerifiedModelOutput(output=output, quote_occurrences=quote_occurrences)
