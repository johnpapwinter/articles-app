from src.articles.core.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    class Config:
        env_file = '.env.production'
        env_file_encoding = 'utf-8'

    ENV: str = 'production'
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 200
    DB_ECHO: bool = False
    ELASTICSEARCH_VERIFY_CERTS: bool = True


