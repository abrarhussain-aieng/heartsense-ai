#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:?}"
: "${ECR_REGISTRY:?}"
: "${IMAGE_TAG:?default to latest}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker pull "$ECR_REGISTRY/heartsense-api:$IMAGE_TAG"
docker pull "$ECR_REGISTRY/heartsense-mcp:$IMAGE_TAG"

docker compose down || true
docker compose up -d
sleep 10

curl -fsS http://localhost:8000/api/health || (docker compose logs; exit 1)