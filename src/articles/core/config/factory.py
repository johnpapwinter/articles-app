from functools import lru_cache
from typing import Type

from src.articles.core.config.base import BaseConfig
from src.articles.core.config.development import DevelopmentConfig
from src.articles.core.config.production import ProductionConfig
from src.articles.core.config.test import TestConfig


class EnvironmentNotFound(Exception):
    pass


@lru_cache
def get_settings(environment: str = None) -> BaseConfig:
    if environment is None:
        environment = "development"

    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig,
    }

    config_class = configs.get(environment.lower())

    if not config_class:
        raise EnvironmentNotFound(
            f"Environment {environment} not found. "
            f"Available environments: {', '.join(configs.keys())}"
        )

    return config_class()


