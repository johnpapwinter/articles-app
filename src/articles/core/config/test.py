from src.articles.core.config.base import BaseConfig

class TestConfig(BaseConfig):
    class Config:
        env_file = '.env.tests'

    POSTGRES_DB: str = 'articles_test_db'
    DB_ECHO: bool = True
    JWT_SECRET_KEY: str = 'test_secret'


