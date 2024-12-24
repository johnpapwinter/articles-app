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

    class Config:
        env_file = '.env'


settings = Settings()


