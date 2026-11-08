from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    dagshub_repo_owner: str = ""
    dagshub_repo_name: str = "heartsense-ai"
    dagshub_token: str = ""

    mlflow_tracking_uri: str = ""
    mlflow_tracking_username: str = ""
    mlflow_tracking_password: str = ""
    mlflow_experiment: str = "heartsense-heart-disease"

    gemini_api_key: str = ""
    groq_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    groq_model: str = "llama-3.1-8b-instant"

    mcp_server_url: str = "http://127.0.0.1:8001/mcp"
    mcp_auth_token: str = ""

    langsmith_api_key: str = ""
    langsmith_project: str = "heartsense-ai"
    langsmith_tracing: bool = False

settings = Settings()