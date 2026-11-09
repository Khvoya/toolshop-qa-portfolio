FROM ghcr.io/astral-sh/uv:0.13.7 AS uv

FROM mcr.microsoft.com/playwright/python:v1.64.1-noble

COPY --from=uv /uv /uvx /bin/

WORKDIR /workspace
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

COPY tests ./tests

ENTRYPOINT ["uv", "run", "--no-sync", "pytest"]
