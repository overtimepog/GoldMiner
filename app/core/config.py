from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "GoldMiner"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./goldminer.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Perplexity
    perplexity_api_key: Optional[str] = None
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    scraping_delay_seconds: int = 2
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "goldminer.log"
    
    # Streamlit
    streamlit_port: int = 8501
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()