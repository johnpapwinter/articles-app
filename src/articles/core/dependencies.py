import os
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

# from src.articles.core.config import Settings, settings
from src.articles.core.config.base import BaseConfig
from src.articles.core.config.factory import get_settings


@lru_cache()
def get_and_cache_settings() -> BaseConfig:
    return get_settings(os.getenv("ENVIRONMENT", "development"))
    # return Settings()


def get_elasticsearch_client(settings_: BaseConfig | None = None) -> AsyncElasticsearch:
    configured_settings = settings_ or get_and_cache_settings()

    return AsyncElasticsearch(
        hosts=[configured_settings.ELASTICSEARCH_HOST],
        verify_certs=configured_settings.ELASTICSEARCH_VERIFY_CERTS,
        basic_auth=(
            configured_settings.ELASTICSEARCH_USER,
            configured_settings.ELASTICSEARCH_PASSWORD
        ) if configured_settings.ELASTICSEARCH_USER else None
    )


def get_elasticsearch_client_dependency(settings_: BaseConfig = Depends(get_settings)) -> AsyncElasticsearch:
    return get_elasticsearch_client(settings_)

