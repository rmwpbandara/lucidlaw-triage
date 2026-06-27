# LucidLaw Triage API — production container image.
FROM python:3.12-slim AS base

# Avoid Python writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code.
COPY app ./app

# Run as a non-root user (security best practice).
RUN useradd --create-home --uid 1001 appuser
USER appuser

EXPOSE 8000

# Honour the platform-provided $PORT when present (Railway/Render), default 8000.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
