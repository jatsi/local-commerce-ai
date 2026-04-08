from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "commerce_ai"
    postgres_user: str = "localai"
    postgres_password: str = "localai"

    redis_host: str = "redis"
    redis_port: int = 6379

    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    ollama_host: str = "http://ollama:11434"

    shopify_store_domain: str = "your-store.myshopify.com"
    shopify_access_token: str = "replace_me"
    shopify_api_version: str = "2026-01"

    etsy_api_key: str = "replace_me"
    etsy_access_token: str = "replace_me"
    etsy_refresh_token: str = "replace_me"

    google_ads_developer_token: str = "replace_me"
    meta_ads_access_token: str = "replace_me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
