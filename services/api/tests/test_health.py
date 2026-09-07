from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_is_public_and_minimal() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_fails_closed_without_external_configuration() -> None:
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {
            "database": "unconfigured",
            "inference": "unconfigured",
            "worker": "unconfigured",
        },
    }


def test_capabilities_disclose_unconfigured_live_provider() -> None:
    response = client.get("/v1/capabilities")
    assert response.status_code == 200
    result = response.json()
    assert result["schema_version"] == "1.0"
    assert result["rubric_version"] == "sif-pilot-v1"
    assert result["engines"][0]["engine_mode"] == "hosted_baseline"
    assert result["engines"][0]["available"] is False
    assert result["engines"][0]["live_inference"] is True
    assert len(result["canonical_rule_ids"]) == 9
