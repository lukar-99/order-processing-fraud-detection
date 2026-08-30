# =========================================================
# Stage 1: Builder (Install dependencies via Poetry)
# =========================================================
FROM python:3.14-slim AS builder
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1


ENV PATH="$POETRY_HOME/bin:$PATH"

# Install curl & Poetry
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY pyproject.toml poetry.lock* ./

# Install production dependencies only into /app/.venv
RUN poetry install --no-root --only main


# =========================================================
# Stage 2: Runtime (Minimal slim production container)
# =========================================================
FROM python:3.14-slim AS runner

WORKDIR /app

# Ensure Python outputs logs directly to stdout (crucial for K8s)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy pre-built virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY ./app /app/app

# Expose port for FastAPI
EXPOSE 8000

# Start Uvicorn web server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]