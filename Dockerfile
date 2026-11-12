# --- STAGE 1: Builder ---
FROM python:3.12-slim AS builder

# Install system dependencies required to compile packages like uvloop
RUN apt-get update && apt-get install -y --no-install-recommends \
          build-essential \
          libffi-dev \
          python3-dev \
          && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for faster, more reliable installs
RUN pip install --no-cache-dir uv

# Install Python dependencies using uv
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

# Expose the port and run the app
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]