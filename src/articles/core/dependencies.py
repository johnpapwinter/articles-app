from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.articles.core.config import Settings, settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_elasticsearch_client(settings_: Settings | None = None) -> AsyncElasticsearch:
    configured_settings = settings_ or settings

    return AsyncElasticsearch(
        hosts=[configured_settings.ELASTICSEARCH_HOST],
        verify_certs=configured_settings.ELASTICSEARCH_VERIFY_CERTS,
        basic_auth=(
            configured_settings.ELASTICSEARCH_USER,
            configured_settings.ELASTICSEARCH_PASSWORD
        ) if configured_settings.ELASTICSEARCH_USER else None
    )


def get_elasticsearch_client_dependency(settings_: Settings = Depends(get_settings)) -> AsyncElasticsearch:
    return get_elasticsearch_client(settings_)

