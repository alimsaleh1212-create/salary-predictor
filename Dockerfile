FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev extras)
RUN uv sync --no-dev --frozen

# Copy application code
COPY api/ ./api/
COPY src/ ./src/
COPY models/ ./models/

# Expose port (Railway overrides with $PORT at runtime)
EXPOSE 8000

# Use venv directly — avoids uv run overhead and PATH issues on Railway
CMD ["/bin/sh", "-c", "/app/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
