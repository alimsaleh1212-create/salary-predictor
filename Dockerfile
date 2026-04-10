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

# Expose port
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
