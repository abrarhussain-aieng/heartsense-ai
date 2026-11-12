# --- STAGE 1: Builder ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
          build-essential \
          curl \
          && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a local folder
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- STAGE 2: Final Image ---
FROM python:3.12-slim

# Create a non-root user for security
RUN useradd -m -u 10001 appuser
WORKDIR /app

# --- BUG FIXES APPLIED HERE ---
# 1. Tell Python to look inside the 'src' folder for the 'heartsense' module
ENV PYTHONPATH=/app/src
# 2. Ensure logs are printed immediately to the console
ENV PYTHONUNBUFFERED=1
# 3. Ensure pip installed packages are in the PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy the installed dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy the application code
COPY . .

# Change ownership to the non-root user so it can write to artifacts/chroma
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose ports for FastAPI and MCP
EXPOSE 8000 8001

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]