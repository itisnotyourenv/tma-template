FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /bin/
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --no-dev --native-tls

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-packages --no-dev --native-tls

FROM base AS prod

ARG GIT_COMMIT=unknown
ARG GIT_BRANCH=unknown
ARG SENTRY_ENVIRONMENT=unknown
ARG SENTRY_RELEASE=unknown

RUN echo "GIT_COMMIT=$GIT_COMMIT" >> /app/.gitinfo && \
    echo "GIT_BRANCH=$GIT_BRANCH" >> /app/.gitinfo && \
    echo "export GIT_COMMIT=$GIT_COMMIT" >> /etc/profile.d/gitinfo.sh && \
    echo "export GIT_BRANCH=$GIT_BRANCH" >> /etc/profile.d/gitinfo.sh

ENV GIT_COMMIT=${GIT_COMMIT} \
    GIT_BRANCH=${GIT_BRANCH} \
    SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT} \
    SENTRY_RELEASE=${SENTRY_RELEASE}

WORKDIR /app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY locales/ ./locales/
COPY --chmod=755 docker/entrypoint-*.sh ./
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
