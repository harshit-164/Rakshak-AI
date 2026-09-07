from app.adapters.gemini import _extract_json_payload


def test_extract_json_payload_accepts_raw_json() -> None:
    assert _extract_json_payload('{"sif_decision":"no"}') == '{"sif_decision":"no"}'


def test_extract_json_payload_unwraps_a_json_code_fence() -> None:
    assert _extract_json_payload('```json\n{"sif_decision":"no"}\n```') == '{"sif_decision":"no"}'
