from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "AI Engine"

    OPENAI_API_KEY: str = ""

    GOOGLE_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    LLM_PROVIDER: str = "groq"

    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

    API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()