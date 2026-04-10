FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY api/ ./api/
COPY src/ ./src/
COPY models/ ./models/

EXPOSE 8000

CMD ["/bin/sh", "-c", "/app/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
