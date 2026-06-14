from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PGAGI Candidate Screening System"
    DATABASE_URL: str = "sqlite:///./candidate_screening.db"
    CHROMA_DIR: str = "./chroma_db"
    KNOWLEDGE_BASE_DIR: str = "./data/knowledge_base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    OPENAI_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
