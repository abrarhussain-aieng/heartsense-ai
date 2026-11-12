from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ===== DagsHub & MLflow =====
    dagshub_repo_owner: str = ""
    dagshub_repo_name: str = "heartsense-heart-disease"
    dagshub_token: str = ""

    mlflow_tracking_uri: str = ""
    mlflow_tracking_username: str = ""
    mlflow_tracking_password: str = ""
    mlflow_experiment: str = "heartsense-heart-disease"

    # ===== LLM Fallback Chain =====
    cerebras_api_key: str = ""
    cerebras_model: str = "llama-3.3-70b"

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    # ===== MCP =====
    mcp_server_url: str = "http://127.0.0.1:8001/mcp"
    mcp_auth_token: str = ""

    # ===== LangSmith =====
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "heartsense-ai"
    
    # ===== Authentication =====
    jwt_secret: str = "fallback-secret-key"
    jwt_algorithm: str = "HS256"

settings = Settings()