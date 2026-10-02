from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://clauseiq:clauseiq@localhost:5432/clauseiq"
    upload_dir: str = "uploads"
    max_file_size_mb: int = 20

    # Gemini is still used temporarily for embeddings.
    GEMINI_API_KEY: str

    # Local Ollama configuration.
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    OLLAMA_TIMEOUT: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()