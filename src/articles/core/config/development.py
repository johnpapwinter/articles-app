from src.articles.core.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'

    DB_ECHO: bool = True
    JWT_SECRET_KEY: str = 'development_secret'
    ENV: str = 'development'

