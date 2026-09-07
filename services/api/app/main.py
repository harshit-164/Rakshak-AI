import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth import get_auth_runtime
from app.config import get_settings
from app.contracts import (
    CANONICAL_RULE_IDS,
    CapabilitiesLimits,
    CapabilitiesResponse,
    EngineCapability,
    EngineMode,
)
from app.errors import ApiProblem
from app.openapi import build_openapi
from app.persistence import (
    PersistenceUnavailableError,
    get_persistence_runtime,
)
from app.routes import router as v1_router
from app.worker import build_worker


class LiveStatus(BaseModel):
    status: str


class ReadyStatus(BaseModel):
    status: str
    dependencies: dict[str, str]


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    worker = None
    worker_task: asyncio.Task[None] | None = None
    stop = asyncio.Event()
    if settings.worker_configured:
        worker = build_worker(settings)
        worker_task = asyncio.create_task(worker.run(stop), name="analysis-worker")
    try:
        yield
    finally:
        if worker_task is not None:
            stop.set()
            try:
                await asyncio.wait_for(worker_task, timeout=5)
            except TimeoutError:
                worker_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await worker_task
        if worker is not None:
            await worker.close()
        if get_auth_runtime.cache_info().currsize:
            await get_auth_runtime().verifier.close()
            get_auth_runtime.cache_clear()
        if get_persistence_runtime.cache_info().currsize:
            await get_persistence_runtime().store.close()
            get_persistence_runtime.cache_clear()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
)
app.include_router(v1_router)


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    retryable: bool = False,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id},
    )


@app.middleware("http")
async def request_boundary(request: Request, call_next: Any) -> Response:
    request.state.request_id = request.headers.get("X-Request-ID") or str(uuid4())
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 524_288:
                return _error_response(
                    request,
                    status_code=413,
                    code="request_too_large",
                    message="Request body exceeds the 512 KiB limit.",
                )
        except ValueError:
            return _error_response(
                request,
                status_code=400,
                code="invalid_content_length",
                message="Content-Length is invalid.",
            )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(ApiProblem)
async def handle_api_problem(request: Request, exc: ApiProblem) -> JSONResponse:
    return _error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        retryable=exc.retryable,
    )


@app.exception_handler(PersistenceUnavailableError)
async def handle_unconfigured_database(
    request: Request, _: PersistenceUnavailableError
) -> JSONResponse:
    return _error_response(
        request,
        status_code=503,
        code="database_unavailable",
        message="Persistence is temporarily unavailable.",
        retryable=True,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, _: RequestValidationError
) -> JSONResponse:
    return _error_response(
        request,
        status_code=422,
        code="validation_error",
        message="The request did not match the API contract.",
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    code = "invalid_session" if exc.status_code == 401 else "request_failed"
    return _error_response(
        request,
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail),
    )


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = build_openapi(app)
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/health/live", response_model=LiveStatus)
async def live() -> LiveStatus:
    return LiveStatus(status="ok")


@app.get("/health/ready", response_model=ReadyStatus)
async def ready(response: Response) -> ReadyStatus:
    dependencies = {
        "database": "ready" if settings.database_configured else "unconfigured",
        "inference": "ready" if settings.provider_configured else "unconfigured",
        "worker": "ready" if settings.worker_configured else "unconfigured",
    }
    is_ready = all(value == "ready" for value in dependencies.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyStatus(status="ready" if is_ready else "not_ready", dependencies=dependencies)


@app.get("/v1/capabilities", response_model=CapabilitiesResponse)
async def capabilities() -> CapabilitiesResponse:
    provider_available = settings.provider_configured
    return CapabilitiesResponse(
        schema_version="1.0",
        rubric_version="sif-pilot-v1",
        current_model_display_name=(
            settings.gemini_model_id if provider_available else "Gemini baseline — unconfigured"
        ),
        engines=[
            EngineCapability(
                engine_mode=EngineMode.HOSTED_BASELINE,
                display_name=settings.gemini_model_id,
                available=provider_available,
                live_inference=True,
            )
        ],
        limits=CapabilitiesLimits(
            narrative_min_codepoints=20,
            narrative_max_codepoints=8000,
            max_api_body_bytes=524_288,
            max_active_jobs=2,
        ),
        canonical_rule_ids=list(CANONICAL_RULE_IDS),
    )
