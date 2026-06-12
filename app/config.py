from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ==========================
    # Groq
    # ==========================
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # ==========================
    # MySQL
    # ==========================
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # ==========================
    # ChromaDB
    # ==========================
    CHROMA_DB_PATH: str = "chroma_db"

    # ==========================
    # Uploads
    # ==========================
    UPLOAD_DIR: str = "uploads"

    # ==========================
    # Embeddings
    # ==========================
    EMBEDDING_MODEL: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # ==========================
    # LangChain
    # ==========================
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # ==========================
    # JWT Authentication
    # ==========================
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================
    # Pydantic Settings
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()