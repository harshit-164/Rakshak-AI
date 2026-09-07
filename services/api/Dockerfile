# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.12.9 AS uv
FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/workspace/services/api/.venv/bin:$PATH"

WORKDIR /workspace
COPY --from=uv /uv /uvx /bin/
COPY services/api/pyproject.toml services/api/uv.lock ./services/api/
RUN uv sync --project services/api --frozen --no-dev

COPY services/api/app ./services/api/app
COPY configs ./configs
COPY artifacts/manifests/hosted-baseline.v1.json ./artifacts/manifests/hosted-baseline.v1.json

RUN useradd --create-home --uid 10001 safeguard \
    && chown -R safeguard:safeguard /workspace
USER safeguard

EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --app-dir services/api --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
