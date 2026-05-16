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

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOOL_ROUNDS: int = 5
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024
    LLM_HISTORY_WINDOW_MINUTES: int = 30
    LLM_MAX_HISTORY_CHARS: int = 8000

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
