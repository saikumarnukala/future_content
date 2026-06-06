"""
Configuration settings for the AI YouTube Shorts Factory.
Loads environment variables and sets up project defaults.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    # API Keys
    groq_api_key: SecretStr = Field(..., env="GROQ_API_KEY")
    deepgram_api_key: SecretStr = Field(..., env="DEEPGRAM_API_KEY")
    image_api_key: SecretStr = Field(..., env="IMAGE_API_KEY")
    
    # YouTube OAuth
    youtube_client_id: str = Field(..., env="YOUTUBE_CLIENT_ID")
    youtube_client_secret: SecretStr = Field(..., env="YOUTUBE_CLIENT_SECRET")
    youtube_refresh_token: SecretStr = Field(..., env="YOUTUBE_REFRESH_TOKEN")
    
    # Optional Webhooks
    slack_webhook_url: str | None = Field(default=None, env="SLACK_WEBHOOK_URL")

    # App Settings
    environment: str = Field(default="production", env="ENVIRONMENT")
    database_url: str = Field(default="sqlite:///./data/pipeline.db", env="DATABASE_URL")
    
    # Project paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    output_dir: Path = base_dir / "output"
    music_dir: Path = data_dir / "music"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.music_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.setup_directories()
