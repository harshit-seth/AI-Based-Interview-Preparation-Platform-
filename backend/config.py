import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def setup_logging():
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s"
    level = logging.DEBUG if os.getenv("DEBUG", "").lower() == "true" else logging.INFO
    logging.basicConfig(level=level, format=fmt, stream=sys.stdout)
    return logging.getLogger(__name__)


logger = setup_logging()


class Settings:
    APP_NAME: str = "Interview Prep API"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    PORT: int = int(os.getenv("PORT", "8000"))

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "interview_prep")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "questions")

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")

    # Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    def validate(self):
        missing = []
        if not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not self.MONGO_URI:
            missing.append("MONGO_URI")
        if missing:
            logger.warning("Missing required env vars: %s", ", ".join(missing))
            logger.warning("The app will start but some features may not work.")
        else:
            logger.info("All required environment variables are set.")
        return self


settings = Settings().validate()
