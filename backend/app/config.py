import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CONFLUENCE_URL: str = os.getenv("CONFLUENCE_URL")
    CONFLUENCE_EMAIL: str = os.getenv("CONFLUENCE_EMAIL")
    CONFLUENCE_API_TOKEN: str = os.getenv("CONFLUENCE_API_TOKEN")
    CONFLUENCE_SPACE: str = os.getenv("CONFLUENCE_SPACE")
    # OpenRouter configuration
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_EMBEDDING_MODEL: str = os.getenv(
        "OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"
    )
    CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_data")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

settings = Settings()