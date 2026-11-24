# HeartSense AI — End-to-End Agentic Cardiovascular Risk & Clinical Guidance Platform

HeartSense AI is a production-grade Machine Learning and Agentic AI platform for cardiovascular disease (CVD) risk assessment, evidence-backed clinical guidance, and longitudinal patient risk analytics. It unifies reproducible tabular ML pipelines (**DVC + MLflow/DagsHub**), multi-agent orchestration (**LangGraph**), grounded medical retrieval (**ChromaDB RAG**), standardized tool execution (**Model Context Protocol**), clinical safety enforcement (**NeMo Guardrails**), automated RAG quality gates (**Ragas**), and containerized cloud delivery (**Docker + GitHub Actions + AWS ECR/ECS/EC2**).

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Repository Structure](#repository-structure)
3. [Environment Setup (`uv`)](#environment-setup-uv)
4. [Configuration & Secrets (`.env`)](#configuration--secrets-env)
5. [Data Versioning & Reproducible ML Pipeline (`DVC` + `MLflow`)](#data-versioning--reproducible-ml-pipeline-dvc--mlflow)
6. [RAG Knowledge Base Ingestion & Ragas Evaluation](#rag-knowledge-base-ingestion--ragas-evaluation)
7. [Running the Application Locally (MCP, FastAPI & Frontend)](#running-the-application-locally-mcp-fastapi--frontend)
8. [Automated Testing (`pytest`)](#automated-testing-pytest)
9. [Containerization (`Docker` & `Docker Compose`)](#containerization-docker--docker-compose)
10. [CI/CD & Cloud Deployment (`GitHub Actions` -> `AWS ECR / ECS / EC2`)](#cicd--cloud-deployment-github-actions---aws-ecr--ecs--ec2)
11. [Clinical Disclaimer](#clinical-disclaimer)

---

## System Architecture

```text
+-----------------------------------------------------------------------------------+
|                        Frontend Dashboard (frontend/)                             |
|         Vanilla JS (app.js, api.js) • Chart.js (charts.js) • Responsive UI        |
+-----------------------------------------+-----------------------------------------+
                                          | REST / JWT Bearer Auth
                                          v
+-----------------------------------------------------------------------------------+
|                         FastAPI Gateway (api/main.py)                             |
|  Routers: /auth • /health • /predict • /assistant • /history • /analytics         |
|           /report • /monitoring                                                   |
+-------------------+-----------------------------------+---------------------------+
                    |                                   |
                    v                                   v
+-----------------------------------+   +-------------------------------------------+
|   Tabular ML Inference Engine     |   |     NeMo Guardrails (guardrails/rails.py) |
|   src/heartsense/predict.py       |   |     Input/Output Clinical Safety Rails    |
|   artifacts/heart_disease_        |   +---------------------+---------------------+
|   pipeline.joblib + SQLite DB     |                         |
+-----------------------------------+                         v
                                        +-------------------------------------------+
                                        |     LangGraph Multi-Agent Orchestrator    |
                                        |     src/heartsense/agents/graph.py        |
                                        +-----------+-------------------+-----------+
                                                    |                   |
                                    +---------------+                   +---------------+
                                    v                                                   v
                  +-----------------------------------+               +-----------------------------------+
                  |   ChromaDB Clinical RAG Engine    |               |   MCP Client -> MCP Server        |
                  |   src/heartsense/rag/retriever.py |               |   mcp_server/server.py + auth.py  |
                  |   WHO / AHA / NHLBI Guidelines    |               |   Clinical Calculators & Tools    |
                  +-----------------------------------+               +-----------------------------------+
```

---

## Repository Structure

```text
heartsense-ai/
├── .github/workflows/           # GitHub Actions CI/CD pipelines (test, build, AWS deploy)
├── api/                         # FastAPI application layer
│   ├── routers/                 # Modular API endpoints
│   │   ├── analytics.py         # Aggregated cohort & risk distribution analytics
│   │   ├── assistant.py         # LangGraph clinical assistant endpoint
│   │   ├── auth.py              # JWT token issuance & authentication
│   │   ├── health.py            # Liveness & readiness probes for Docker/ECS ALB
│   │   ├── history.py           # Patient prediction history queries (SQLite)
│   │   ├── monitoring.py        # Model & drift telemetry endpoints
│   │   ├── predict.py           # Tabular CVD risk inference endpoint
│   │   └── report.py            # Structured clinical summary report generation
│   ├── deps.py                  # Dependency injection (DB sessions, JWT auth, singletons)
│   ├── main.py                  # FastAPI app initialization, CORS & static frontend mount
│   └── schemas.py               # Pydantic v2 request/response contracts
├── artifacts/                   # DVC-tracked model binaries, metrics & local SQLite DB
│   ├── heart_disease_pipeline.joblib
│   ├── history.db
│   └── metrics.json
├── chroma/                      # Persisted ChromaDB vector store (chroma.sqlite3 + HNSW)
├── data/
│   ├── processed/               # Train/test splits produced by DVC stages
│   ├── rag_pdfs/                # WHO, AHA, and NHLBI clinical PDF corpus
│   └── raw/                     # DVC-tracked raw dataset (heart.csv + heart.csv.dvc)
├── evaluation/                  # Automated RAG evaluation suite
│   ├── rag_eval_dataset.json    # Ground-truth Q&A evaluation pairs
│   ├── ragas_result.json        # Faithfulness, relevancy & context precision scores
│   └── run_ragas.py             # Ragas evaluation runner
├── frontend/                    # Web dashboard UI
│   ├── css/styles.css
│   ├── js/                      # api.js, app.js, charts.js, chart.umd.min.js
│   └── index.html
├── mcp_server/                  # Standalone Model Context Protocol (MCP) tool server
│   ├── auth.py                  # Token/API-key verification for MCP tool calls
│   └── server.py                # Registered clinical & risk calculation tools
├── scripts/
│   └── setup_env.ps1            # Windows PowerShell environment bootstrap script
├── src/heartsense/              # Core installable Python package (pyproject.toml)
│   ├── agents/
│   │   ├── graph.py             # LangGraph state machine & agent nodes
│   │   └── mcp_client.py        # Client bridge connecting LangGraph to mcp_server
│   ├── guardrails/
│   │   └── rails.py             # NeMo Guardrails input/output topical & safety checks
│   ├── monitoring/
│   │   └── mlflow_utils.py      # MLflow & DagsHub experiment logging helpers
│   ├── rag/
│   │   ├── ingest.py            # PDF chunking, embedding & ChromaDB persistence
│   │   ├── retriever.py         # Semantic similarity retriever
│   │   └── sources.json         # Clinical metadata & citation registry
│   ├── config.py                # Centralized Pydantic/env settings
│   ├── data.py                  # Data ingestion, validation & splitting
│   ├── evaluate.py              # Classification metrics & artifact reporting
│   ├── features.py              # Scikit-learn preprocessing & feature engineering
│   ├── llm_client.py            # Unified LLM provider wrapper
│   ├── predict.py               # Inference pipeline loader & probability scorer
│   └── train.py                 # Model training & MLflow logging
├── tests/                       # Pytest unit & integration test suite
│   ├── test_api.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_guardrails.py
│   ├── test_mcp_tools.py
│   ├── test_rag.py
│   └── test_train.py
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # Local multi-service development stack
├── docker-compose.prod.yml      # Production container orchestration
├── dvc.yaml                     # Reproducible ML pipeline DAG definition
├── dvc.lock                     # Locked data & pipeline hashes
├── params.yaml                  # Hyperparameters & feature split configuration
├── pyproject.toml               # Package metadata & build configuration
├── requirements.in              # Direct top-level dependencies
└── requirements.txt             # Pinned lockfile generated via uv
```

---

## Environment Setup (`uv`)

HeartSense AI uses **`uv`** for deterministic, ultra-fast dependency resolution and editable package installation.

### 1. Clone Repository & Create Virtual Environment

**Windows (PowerShell):**
```powershell
git clone [https://github.com/](https://github.com/)<your-org>/heartsense-ai.git
cd heartsense-ai

# Option A: Run the bundled PowerShell bootstrap script
.\scripts\setup_env.ps1

# Option B: Manual virtual environment setup with uv
uv venv .venv --python 3.12
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS (Bash):**
```bash
git clone [https://github.com/](https://github.com/)<your-org>/heartsense-ai.git
cd heartsense-ai

uv venv .venv --python 3.12
source .venv/bin/activate
```

### 2. Compile & Install Dependencies (`uv`)

```bash
# Optional: Re-compile pinned requirements.txt from requirements.in
uv pip compile requirements.in -o requirements.txt

# Install locked dependencies and install src/heartsense in editable mode
uv pip install -r requirements.txt
uv pip install -e .
```

---

## Configuration & Secrets (`.env`)

Copy `.env.example` to `.env` and populate your API keys and secrets before running pipelines or servers:

```bash
cp .env.example .env
```

```env
# --- LLM & Embedding Providers ---
MISTRAL_API_KEY=your_mistral_api_key
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# --- Security & JWT Authentication ---
JWT_SECRET_KEY=replace_with_strong_random_256bit_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MCP_API_KEY=replace_with_internal_mcp_secret

# --- MLflow & DagsHub Tracking ---
MLFLOW_TRACKING_URI=[https://dagshub.com/](https://dagshub.com/)<username>/heartsense-ai.mlflow
MLFLOW_TRACKING_USERNAME=<dagshub_username>
MLFLOW_TRACKING_PASSWORD=<dagshub_token>

# --- Storage & Vector Store ---
CHROMA_PERSIST_DIR=./chroma
SQLITE_DB_PATH=./artifacts/history.db
MCP_SERVER_URL=http://localhost:8001
```

---

## Data Versioning & Reproducible ML Pipeline (`DVC` + `MLflow`)

All dataset versions (`data/raw/heart.csv.dvc`), pipeline stages (`dvc.yaml`), hyperparameters (`params.yaml`), and trained artifacts (`artifacts/heart_disease_pipeline.joblib`, `artifacts/metrics.json`) are managed by **DVC** and logged to **MLflow / DagsHub**.

### 1. Configure DVC Remote Storage (DagsHub or AWS S3)

**Option A — DagsHub Remote:**
```bash
dvc remote add -d origin [https://dagshub.com/](https://dagshub.com/)<username>/heartsense-ai.dvc
dvc remote modify origin --local auth basic
dvc remote modify origin --local user <dagshub_username>
dvc remote modify origin --local password <dagshub_token>
```

**Option B — Amazon S3 Remote:**
```bash
dvc remote add -d s3remote s3://heartsense-ai-dvc-artifacts/dvc-store
dvc remote modify s3remote region us-east-1
```

### 2. Pull Data, Reproduce Pipeline & Push Artifacts

```bash
# Pull tracked dataset & artifacts from remote storage
dvc pull

# Inspect the pipeline DAG defined in dvc.yaml
dvc dag

# Execute end-to-end ML pipeline (data prep -> feature engineering -> train -> evaluate)
dvc repro

# Force full pipeline re-execution ignoring cache
dvc repro --force

# Inspect model evaluation metrics (Accuracy, ROC-AUC, F1, Precision, Recall)
dvc metrics show
cat artifacts/metrics.json

# Push updated data hashes and trained model artifacts to remote storage
dvc push
git add dvc.lock artifacts/metrics.json
git commit -m "chore(ml): reproduce pipeline and update model metrics"
```

---

## RAG Knowledge Base Ingestion & Ragas Evaluation

HeartSense AI grounds clinical guidance in authoritative guidelines (`AHA_Dietary_Guidance`, `NHLBI_Healthy_Heart`, `WHO_CVD_FactSheet`) located in `data/rag_pdfs/`.

### 1. Ingest Clinical PDFs into ChromaDB

```bash
# Parse PDFs, chunk documents, attach citations from sources.json, and persist to ./chroma
python -m src.heartsense.rag.ingest
```

### 2. Run Ragas Automated Quality Evaluation

```bash
# Evaluate Faithfulness, Answer Relevancy, Context Precision & Context Recall
python evaluation/run_ragas.py

# Review evaluation scores
cat evaluation/ragas_result.json
```

---

## Running the Application Locally (MCP, FastAPI & Frontend)

Run the MCP tool server and the FastAPI backend in separate terminals (or run both together via Docker Compose).

### Terminal 1 — Start the MCP Tool Server
```bash
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2 — Start the FastAPI Backend & Web Dashboard
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verify Endpoints
- **Interactive Web Dashboard**: `http://localhost:8000` (served from `frontend/index.html`)
- **Swagger / OpenAPI Docs**: `http://localhost:8000/docs`
- **Health Check**: `curl http://localhost:8000/health`

### Quick API Smoke Test (`curl`)
```bash
# 1. Authenticate and retrieve JWT token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "clinician", "password": "password123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Run Cardiovascular Risk Prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 54, "sex": 1, "cp": 2, "trestbps": 140,
    "chol": 239, "fbs": 0, "restecg": 1, "thalach": 160,
    "exang": 0, "oldpeak": 1.2, "slope": 2, "ca": 0, "thal": 2
  }'

# 3. Query the Guardrailed LangGraph + RAG + MCP Assistant
curl -X POST "http://localhost:8000/assistant/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What dietary adjustments does the AHA recommend to lower LDL cholesterol?"}'
```

---

## Automated Testing (`pytest`)

Execute the full test suite covering data validation, feature transformations, model training, RAG retrieval, MCP tools, guardrails, and FastAPI endpoints:

```bash
# Run all tests with verbose output
pytest -v

# Run with coverage report across src/heartsense and api
pytest -v --cov=src/heartsense --cov=api --cov-report=term-missing
```

---

## Containerization (`Docker` & `Docker Compose`)

### Local Development Stack (`docker-compose.yml`)
```bash
docker compose up --build
```

### Production Stack (`docker-compose.prod.yml`)
```bash
# Build and launch detached production containers
docker compose -f docker-compose.prod.yml up -d --build

# Check container health and logs
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f

# Tear down containers
docker compose -f docker-compose.prod.yml down
```

### Standalone Docker Image Build & Run
```bash
docker build -t heartsense-ai:latest .
docker run -d --name heartsense-api -p 8000:8000 --env-file .env heartsense-ai:latest
```

---

## CI/CD & Cloud Deployment (`GitHub Actions` -> `AWS ECR / ECS / EC2`)

### Step 1: Provision AWS Infrastructure (ECR + ECS Fargate + IAM OIDC)

1. **Create an Amazon ECR Repository**:
   ```bash
   aws ecr create-repository \
     --repository-name heartsense-ai \
     --image-scanning-configuration scanOnPush=true \
     --region us-east-1
   ```

2. **Create an Amazon ECS Cluster & CloudWatch Log Group**:
   ```bash
   aws ecs create-cluster --cluster-name heartsense-cluster --region us-east-1
   aws logs create-log-group --log-group-name /ecs/heartsense-ai --region us-east-1
   ```

3. **Configure Passwordless GitHub Actions Authentication via AWS IAM OIDC**:
   ```bash
   # Register GitHub OIDC Identity Provider (one-time per AWS account)
   aws iam create-open-id-connect-provider \
     --url [https://token.actions.githubusercontent.com](https://token.actions.githubusercontent.com) \
     --client-id-list sts.amazonaws.com
   ```
   Create an IAM Role (`github-actions-heartsense-deploy`) with a trust policy scoped to your GitHub repository (`repo:<your-org>/heartsense-ai:ref:refs/heads/main`) and attach `AmazonEC2ContainerRegistryPowerUser` + `AmazonECS_FullAccess`.

4. **Register ECS Task Definition & Launch Fargate Service**:
   Create an ECS Fargate task definition (`heartsense-task`) pointing to `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/heartsense-ai:latest` on port `8000` (injecting `.env` variables via **AWS Secrets Manager**), then deploy your service:
   ```bash
   aws ecs create-service \
     --cluster heartsense-cluster \
     --service-name heartsense-service \
     --task-definition heartsense-task \
     --desired-count 1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}" \
     --region us-east-1
   ```

### Step 2: Configure GitHub Repository Secrets & Variables

Navigate to **GitHub Repository -> Settings -> Secrets and variables -> Actions**:

| Type | Name | Value |
| :--- | :--- | :--- |
| **Secret** | `AWS_ROLE_ARN` | `arn:aws:iam::<AWS_ACCOUNT_ID>:role/github-actions-heartsense-deploy` |
| **Secret** | `DAGSHUB_USERNAME` | Your DagsHub username (for `dvc pull` in CI) |
| **Secret** | `DAGSHUB_TOKEN` | Your DagsHub access token |
| **Variable** | `AWS_REGION` | `us-east-1` |
| **Variable** | `ECR_REPOSITORY` | `heartsense-ai` |
| **Variable** | `ECS_CLUSTER` | `heartsense-cluster` |
| **Variable** | `ECS_SERVICE` | `heartsense-service` |
| **Variable** | `CONTAINER_NAME` | `heartsense-api` |

### Step 3: GitHub Actions CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

Create `.github/workflows/ci-cd.yml` to automate DVC artifact retrieval, `pytest` validation, Docker image builds, Amazon ECR pushes, and zero-downtime ECS Fargate deployments on every push to `main`:

```yaml
name: HeartSense AI — CI/CD to AWS ECS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write   # Required for AWS OIDC federation
  contents: read

env:
  AWS_REGION: ${{ vars.AWS_REGION }}
  ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
  ECS_CLUSTER: ${{ vars.ECS_CLUSTER }}
  ECS_SERVICE: ${{ vars.ECS_SERVICE }}
  CONTAINER_NAME: ${{ vars.CONTAINER_NAME }}

jobs:
  ci-test-and-validate:
    name: Pull DVC Artifacts & Run Pytest Suite
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python 3.12 & install dependencies
        run: |
          uv venv .venv --python 3.12
          source .venv/bin/activate
          uv pip install -r requirements.txt
          uv pip install -e .

      - name: Pull DVC-tracked data & model pipeline
        env:
          DVC_REMOTE_USER: ${{ secrets.DAGSHUB_USERNAME }}
          DVC_REMOTE_PASSWORD: ${{ secrets.DAGSHUB_TOKEN }}
        run: |
          source .venv/bin/activate
          dvc remote modify origin --local user "$DVC_REMOTE_USER"
          dvc remote modify origin --local password "$DVC_REMOTE_PASSWORD"
          dvc pull

      - name: Run automated test suite (pytest)
        env:
          JWT_SECRET_KEY: "ci-test-secret-key-not-for-prod"
          MCP_API_KEY: "ci-test-mcp-key"
        run: |
          source .venv/bin/activate
          pytest -v

  cd-build-and-deploy-aws:
    name: Build Docker Image & Deploy to AWS ECS
    needs: ci-test-and-validate
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Install uv & pull DVC artifacts for container build
        env:
          DVC_REMOTE_USER: ${{ secrets.DAGSHUB_USERNAME }}
          DVC_REMOTE_PASSWORD: ${{ secrets.DAGSHUB_TOKEN }}
        run: |
          pip install uv dvc dvc-s3
          dvc remote modify origin --local user "$DVC_REMOTE_USER"
          dvc remote modify origin --local password "$DVC_REMOTE_PASSWORD"
          dvc pull

      - name: Build, tag, and push Docker image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Download current ECS Task Definition
        run: |
          aws ecs describe-task-definition \
            --task-definition heartsense-task \
            --query taskDefinition > task-def.json

      - name: Render new image URI into ECS Task Definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-def.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build-image.outputs.image }}

      - name: Deploy updated Task Definition to Amazon ECS Fargate
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```

### Alternative: Single-Instance AWS EC2 Deployment (`docker-compose.prod.yml`)

If deploying directly onto an Ubuntu EC2 instance (`t3.medium` or larger) instead of ECS Fargate:

```bash
# 1. SSH into your EC2 instance
ssh -i "heartsense-key.pem" ubuntu@<EC2_PUBLIC_IP>

# 2. Install Docker & Docker Compose plugin
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker

# 3. Authenticate to Amazon ECR & launch production compose stack
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

git clone [https://github.com/](https://github.com/)<your-org>/heartsense-ai.git && cd heartsense-ai
cp .env.example .env  # Populate production secrets
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## Clinical Disclaimer

HeartSense AI is an engineering and clinical decision-support system. Model probability scores and RAG-generated recommendations do not constitute a medical diagnosis and must be reviewed by a qualified healthcare professional.
