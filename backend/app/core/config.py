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
    tts_provider: str = Field(default="openai")  # openai, google, azure, coqui
    openai_tts_voice: str = Field(default="alloy", description="OpenAI TTS voice")
    openai_tts_model: str = Field(default="tts-1", description="OpenAI TTS model")

    # External API keys
    openai_api_key: str = Field(default="", description="OpenAI API key for GPT models and TTS")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=1000, description="Max tokens for OpenAI responses")

    # Social Media API Keys
    facebook_app_id: str = Field(default="", description="Facebook App ID")
    facebook_app_secret: str = Field(default="", description="Facebook App Secret")
    facebook_page_access_token: str = Field(default="", description="Facebook Page Access Token")
    facebook_verify_token: str = Field(default="", description="Facebook Webhook Verify Token")

    instagram_business_id: str = Field(default="", description="Instagram Business Account ID")
    instagram_access_token: str = Field(default="", description="Instagram Access Token")

    whatsapp_business_id: str = Field(default="", description="WhatsApp Business Account ID")
    whatsapp_access_token: str = Field(default="", description="WhatsApp Access Token")
    whatsapp_verify_token: str = Field(default="", description="WhatsApp Webhook Verify Token")
    whatsapp_phone_number_id: str = Field(default="", description="WhatsApp Phone Number ID")

    # Other API keys
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
