FROM python:3.12-slim

# Install curl for healthchecks/debug and pipx
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Install uv via official installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY app ./app

# Port configuration
ENV API_PORT=8000

# Use shell form so ${API_PORT} expands correctly at runtime
CMD sh -lc "uv run uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT}"
