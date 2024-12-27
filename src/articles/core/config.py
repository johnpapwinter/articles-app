from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = 'Articles'

    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'password'
    POSTGRES_DB: str = 'articles_db'
    POSTGRES_URI: str = f'postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'

    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 100

    JWT_ISSUER: str = 'ArticlesApp'
    JWT_SECRET_KEY: str = 'secret'
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 60

    ELASTICSEARCH_HOST: str = 'http://localhost:9200'
    ELASTICSEARCH_USER: str | None = None
    ELASTICSEARCH_PASSWORD: str | None = None
    ELASTICSEARCH_VERIFY_CERTS: bool = False

    class Config:
        env_file = '.env'


settings = Settings()


