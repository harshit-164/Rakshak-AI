from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic.json_schema import models_json_schema

from app.contracts import CONTRACT_MODELS


def build_openapi(app: FastAPI) -> dict[str, Any]:
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    _, definitions = models_json_schema(
        [(model, "validation") for model in CONTRACT_MODELS],
        ref_template="#/components/schemas/{model}",
        title="SIH26165 API contracts",
    )
    contract_schemas = definitions.get("$defs", {})
    schema.setdefault("components", {}).setdefault("schemas", {}).update(contract_schemas)
    return schema

