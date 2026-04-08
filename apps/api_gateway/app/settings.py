from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "local-commerce-ai"
    database_url: str = "sqlite+pysqlite:///./local.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "commerce_knowledge"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    shopify_store: str = "stub.myshopify.com"


settings = Settings()
