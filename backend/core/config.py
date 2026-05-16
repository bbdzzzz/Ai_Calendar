from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/ai_calendar"
    SECRET_KEY: str = "ai-calendar-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    ASR_MODEL: str = "paraformer-zh-streaming"
    TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
