# HeartSense AI

HeartSense AI is an end-to-end cardiovascular risk prediction and assistant platform built on the UCI Heart Disease dataset. It combines a scikit-learn ML pipeline, DVC + DagsHub + MLflow experiment tracking, a FastAPI backend, a responsive dark dashboard, Gemini/Groq RAG, a LangGraph multi-agent system with an MCP Streamable HTTP server, LangSmith tracing, Ragas evaluation, NeMo Guardrails, Docker, GitHub Actions, and AWS EC2 + S3 deployment.

> **Medical disclaimer:** This project is for educational and research purposes only. It does not provide diagnosis, treatment, or medication advice. Always consult a licensed clinician.

---

## 1. Architecture

```
heart.csv
   │
   ▼
DVC (data versioning) ──► DagsHub (remote storage)
   │
   ▼
train.py ──► MLflow (DagsHub remote tracking) ──► artifacts/heart_disease_pipeline.joblib
   │
   ▼
FastAPI (api/main.py) ──► frontend/ (HTML + CSS + vanilla JS)
   │
   ├──► RAG (ChromaDB + Gemini embeddings)
   ├──► LangGraph Supervisor
   │       ├── Prediction Agent ──► MCP predict_heart_disease
   │       ├── Medical RAG Agent ──► MCP search_medical_knowledge
   │       └── Analytics Agent  ──► MCP get_prediction_analytics
   ├──► NeMo Guardrails (input/output rails)
   └──► LangSmith (tracing, optional)
```

---

## 2. Prerequisites

- Windows 10/11 with VS Code
- Conda (Miniconda or Anaconda)
- Python 3.12
- Git
- Docker Desktop (for local Docker testing)
- DagsHub account + repository
- Gemini API key (Google AI Studio)
- Groq API key
- AWS account (for Phase 7 only)

---

## 3. Environment Setup (Windows PowerShell)

```powershell
conda create -n ai-env python=3.12 -y
conda activate ai-env
python -m pip install --upgrade pip uv
uv pip install -r requirements.txt
```

**Why:** `uv pip` is used instead of plain `pip` for faster, lockfile-compatible installs inside the Conda environment.

Copy `.env.example` to `.env` and fill in credentials. **Never commit `.env`.**

---

## 4. Dataset

`data/raw/heart.csv` contains 918 rows and 12 columns. Target: `HeartDisease` (0/1).

| Column | Type | Notes |
|---|---|---|
| Age | numeric | |
| Sex | categorical | M/F |
| ChestPainType | categorical | ATA/NAP/ASY/TA |
| RestingBP | numeric | 0 treated as missing |
| Cholesterol | numeric | 0 treated as missing |
| FastingBS | binary | |
| RestingECG | categorical | Normal/ST/LVH |
| MaxHR | numeric | |
| ExerciseAngina | categorical | Y/N |
| Oldpeak | numeric | negative values kept |
| ST_Slope | categorical | Up/Flat/Down |
| HeartDisease | target | 0/1 |

Cleaning rules (in `src/heartsense/data.py`):
- `RestingBP == 0` → NaN → median imputation.
- `Cholesterol == 0` → NaN → median imputation.
- Negative `Oldpeak` is physiologically possible and is **not** clipped.

---

## 5. DVC + DagsHub

```powershell
git init
dvc init
dvc add data/raw/heart.csv
git add .
git commit -m "track data with dvc"

dvc remote add -d dagshub https://dagshub.com/'Abrar'/'MLFlow_test'.dvc
dvc remote modify dagshub user 'Abrar'
dvc remote modify dagshub auth basic
dvc remote modify dagshub password --local <dagshub_token>

dvc push
```

**Why each command:**
- `dvc add` creates a `.dvc` pointer file; the actual CSV goes to the DVC cache.
- `dvc remote` configures DagsHub as the default remote.
- `--local` keeps the token out of `.dvc/config`, so it is not committed.
- `dvc push` uploads data to DagsHub.

---

## 6. MLflow via DagsHub

Set in `.env`:

```env
MLFLOW_TRACKING_URI=https://dagshub.com/<owner>/<repo>.mlflow
MLFLOW_TRACKING_USERNAME=<dagshub_username>
MLFLOW_TRACKING_PASSWORD=<dagshub_token>
```

Run training:

```powershell
dvc repro
dvc metrics show
```

**Why:** DagsHub provides a free hosted MLflow server per repository; the tracking URI and basic-auth credentials are read from environment variables, so tokens are never hardcoded.

View experiments at `https://dagshub.com/<owner>/<repo>/experiments`.

---

## 7. FastAPI + Dashboard

```powershell
uvicorn api.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000`.

Endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/predict` | Heart disease prediction |
| GET | `/api/history` | Prediction history |
| GET | `/api/analytics` | Aggregated analytics |
| POST | `/api/report` | Report generation |
| POST | `/api/assistant` | Multi-agent assistant |
| GET | `/api/monitoring` | MLflow experiment info |

**Why:** Serving the frontend from FastAPI keeps the dashboard and API on the same origin, avoiding CORS issues in production.

---

## 8. Gemini + Groq Fallback

`src/heartsense/llm_client.py` builds a primary Gemini chat model and attaches Groq as a LangChain fallback:

```python
primary = ChatGoogleGenerativeAI(...)
fallback = ChatGroq(...)
llm = primary.with_fallbacks([fallback])
```

**Why:** Gemini free tier has rate limits; Groq provides a fast fallback when Gemini returns 429/503 or times out. `langchain-google-genai >= 4.0.0` uses the unified `google-genai` SDK.

---

## 9. RAG (ChromaDB + Gemini Embeddings)

```powershell
python -m heartsense.rag.ingest
```

This chunks curated cardiovascular educational documents, embeds them with Gemini embeddings, and persists them to ChromaDB. The retriever returns excerpts with source metadata (`source`, `title`, `url`). If no relevant chunk exceeds the relevance threshold, the API returns an "insufficient evidence" response instead of hallucinating.

**Why ChromaDB persistent mode:** It avoids an external vector database service, important on a 1 GB t3.micro.

---

## 10. LangGraph Multi-Agent System + MCP

Start the MCP server:

```powershell
python -m mcp_server.server
```

It listens on `http://127.0.0.1:8001/mcp` using Streamable HTTP.

MCP tools:
1. `predict_heart_disease` — validates inputs and calls the saved scikit-learn pipeline.
2. `search_medical_knowledge` — returns ChromaDB excerpts with source metadata.
3. `get_prediction_analytics` — returns authorized prediction history summaries.

**Authentication:** The MCP endpoint expects `Authorization: Bearer <MCP_AUTH_TOKEN>`. Do not expose it publicly without TLS and access control.

LangGraph connects via `langchain-mcp-adapters` and `mcp.client.streamable_http`.

---

## 11. LangSmith, Ragas, NeMo Guardrails

**LangSmith:** set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to trace agent runs. Raw patient inputs are redacted before tracing.

**Ragas:** run:

```powershell
python evaluation/run_ragas.py
```

Reports faithfulness, answer relevancy, context precision, and context recall. Thresholds are configurable in the script.

**NeMo Guardrails:** input rails block diagnosis/medication requests; output rails block unsafe clinical advice. Prompt-injection patterns are also blocked. Configuration lives in `src/heartsense/guardrails/rails.py`.

---

## 12. Docker (Local)

```powershell
docker compose build
docker compose up -d
curl http://localhost:8000/api/health
curl http://localhost:8001/mcp
```

**Why:** The API and MCP server run as separate services with internal networking. Both run as non-root users and include health checks.

---

## 13. GitHub Actions CI/CD

- **CI:** lint, unit tests, API tests, MCP tool tests, RAG and guardrail tests.
- **Build:** build and push Docker images to Amazon ECR.
- **Deploy:** SSH into EC2, pull images, restart services, verify health endpoint.

Required GitHub secrets:
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `ECR_REPOSITORY`.

Prefer GitHub OIDC over static AWS keys where practical.

---

## 14. AWS EC2 t3.micro Deployment

### 14.1 Critical memory step

t3.micro has only 1 GB RAM. Add 2 GB swap before running Docker:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Why:** Without swap, `docker build` and ChromaDB initialization will be OOM-killed.

### 14.2 Do not build on EC2

Build images in GitHub Actions, push to ECR, and run on EC2:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker pull <account>.dkr.ecr.<region>.amazonaws.com/heartsense-api:latest
docker compose up -d
```

### 14.3 S3

Use S3 only for:
- application logs and backups,
- deployment scripts,
- optional model artifact backups.

Keep DVC data and MLflow experiments on DagsHub to avoid duplicate storage. Bucket policy: private, SSE-S3 or SSE-KMS, versioning enabled, lifecycle rule to expire old backups.

### 14.4 HTTPS

Put Nginx or Caddy in front of the API on EC2 and terminate TLS with Let's Encrypt. Only expose 80/443 and 22 (restricted to your IP) in the security group.

### 14.5 Rollback

```bash
docker compose down
docker pull <account>.dkr.ecr.<region>.amazonaws.com/heartsense-api:<previous_tag>
docker compose up -d
```

### 14.6 Cleanup / cost control

- Stop or terminate the EC2 instance when not in use.
- Delete unused ECR images.
- Set S3 lifecycle rules.
- AWS Free Tier for t3.micro is limited to 750 hours/month for 12 months; after that, charges apply.

---

## 15. Troubleshooting

| Symptom | Fix |
|---|---|
| `Model artifact not found` | Run `dvc repro` first |
| `No LLM API key configured` | Set `GEMINI_API_KEY` or `GROQ_API_KEY` in `.env` |
| MCP connection refused | Ensure `python -m mcp_server.server` is running on port 8001 |
| DVC push 403 | Check DagsHub token and `dvc remote modify dagshub password --local` |
| EC2 OOM during build | Do not build on EC2; build in CI, use ECR, add swap |
| ChromaDB slow on t3.micro | Reduce chunk size / collection size; run ingestion locally and copy `chroma/` to EC2 |

---

## 16. Privacy & Medical Limitations

- Do not log raw patient inputs by default.
- LangSmith tracing redacts sensitive fields.
- The assistant refuses diagnosis, treatment, and medication requests.
- Predictions are statistical estimates, not clinical diagnoses.

---

## 17. Verified vs. Requires Credentials

**Verified locally without cloud credentials:**
- Data loading, cleaning, and schema validation.
- Preprocessing pipeline and model training.
- FastAPI routes and frontend static serving.
- MCP tool schemas and local Streamable HTTP server.

**Requires credentials / cloud setup:**
- DVC push to DagsHub.
- MLflow logging to DagsHub remote.
- Gemini / Groq API calls.
- LangSmith tracing.
- AWS ECR / EC2 / S3 deployment.

No test results or deployment success are claimed here; run the commands in your environment to verify.