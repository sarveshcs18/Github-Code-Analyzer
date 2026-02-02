from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GitHub Repo Analyzer"
    
    # Environment
    ENV: str = "dev"
    
    # Paths (Default to dummy for dev, will be overridden by env vars in prod)
    CERT_PATH: Optional[str] = None
    KEY_PATH: Optional[str] = None
    SSH_KEY_PATH: Optional[str] = None
    
    # Vertex AI
    VERTEX_PROJECT_ID: Optional[str] = None
    VERTEX_LOCATION: str = "us-central1"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
