from src.articles.core.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    class Config:
        env_file = '.env.development'

    DB_ECHO: bool = True
    JWT_SECRET_KEY: str = 'development_secret'


