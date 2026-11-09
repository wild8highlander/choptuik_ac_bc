# Multi-platform Dockerfile for reproducible verification
# Usage: docker build -t choptyuk-verify . && docker run choptyuk-verify

FROM python:3.12-slim AS base

LABEL maintainer="Ishak Khamzatovich Isaev <aslan08_05@mail.ru>"
LABEL description="Choptyuk Spinor Corrections Verification Environment"
LABEL repository="https://github.com/wild8highlander/choptuik_ac_bc"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ gfortran \
    libopenblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY python/requirements.txt /app/python/
RUN pip install --no-cache-dir -r python/requirements.txt \
    python-docx reportlab markdown jinja2

# Copy Python source
COPY python/ /app/python/

# Default: run verification
CMD ["python", "/app/python/run.py", "--mode", "verify", "--non-interactive", "--output-dir", "/app/output"]
