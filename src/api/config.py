from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/voice_agent"
    )
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/voice_agent"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    openai_api_key: str = ""
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_model_id: str = "eleven_turbo_v2_5"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    tts_provider: str = "deepgram"
    deepgram_tts_model: str = "aura-2-thalia-en"
    serper_api_key: str = ""

    chroma_host: str = "localhost"
    chroma_port: int = 8100

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
