from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    APP_NAME: str = 'Articles'
    ENV : str = 'base'

    # Database
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: str = '5433'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'password'
    POSTGRES_DB: str = 'articles_db'

    @property
    def POSTGRES_URI(self) -> str:
        return f'postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}'

    # Database Pool
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 100

    # JWT
    JWT_ISSUER: str = 'ArticlesApp'
    JWT_SECRET_KEY: str = 'secret'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 60

    # Elasticsearch
    ELASTICSEARCH_HOST: str = 'http://localhost:9200'
    ELASTICSEARCH_USER: str | None = None
    ELASTICSEARCH_PASSWORD: str | None = None
    ELASTICSEARCH_VERIFY_CERTS: bool = False

    class Config:
        env_file = '.env'