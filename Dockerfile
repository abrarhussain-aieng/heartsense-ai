# --- STAGE 1: Builder ---
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
          build-essential \
          libffi-dev \
          python3-dev \
          && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

# 1. Install CPU-only PyTorch first to avoid ~2.5GB+ of CUDA/NVIDIA packages
RUN uv pip install --system --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install remaining dependencies (sentence-transformers will reuse CPU torch)
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# --- STAGE 2: Final Image ---
FROM python:3.12-slim

WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Tell Python to look inside the /app/src directory for modules
ENV PYTHONPATH=/app/src

# Expose the port and run the app
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]