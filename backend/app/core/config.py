from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    app_name: str = Field(default="Bangla AI Backend")
    api_version: str = Field(default="v0")
    
    # CORS
    cors_origins: str = Field(default='["http://localhost:5173"]')
    
    # Database
    database_url: str = Field(default="postgresql://bangla:bangla_dev_pass@localhost:5432/bangla_ai")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # JWT
    secret_key: str = Field(default="dev_secret_key_change_in_production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    
    # AI Services
    nlu_model_name: str = Field(default="sagorsarker/bangla-bert-base")
    whisper_model_size: str = Field(default="base")
    tts_provider: str = Field(default="google")  # google, azure, coqui
    
    # External API keys (optional)
    openai_api_key: str = Field(default="")
    google_cloud_api_key: str = Field(default="")
    azure_speech_key: str = Field(default="")
    
    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.cors_origins)
        except:
            return ["http://localhost:5173"]

    class Config:
        env_prefix = "BANG_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
