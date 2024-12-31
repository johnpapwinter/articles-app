import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context
# from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin

from src.articles.core.config.factory import get_settings
from src.articles.db.base import Base
# from src.articles.core.config import settings
# from sqlalchemy_continuum import make_versioned, versioning_manager

# make_versioned(user_cls=None, plugins=[PropertyModTrackerPlugin()])

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
settings = get_settings(ENVIRONMENT)

# # Initialize versioning
# make_versioned(user_cls=None)
#
# # Configure versioning manager
# versioning_manager.options.update({
#     'native_versioning': True,
#     'transaction_column_name': 'transaction_id',
#     'end_transaction_column_name': 'end_transaction_id',
#     'operation_type_column_name': 'operation_type',
#     'strategy': 'validity',
#     'use_module_name': False,
#     'schema_name': 'versioning',
#     'transaction_table_schema': 'versioning',
# })


from src.articles.models.article import Article
from src.articles.models.user import User
from src.articles.models.author import Author
from src.articles.models.comment import Comment
from src.articles.models.tag import Tag

# versioning_manager.declarative_base = Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    return settings.POSTGRES_URI

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(obj, name, type_, reflected, compare_to):
    """Handle versioning tables inclusion"""
    if type_ == "table":
        # Skip version_table operations during initial migration
        if name == "version_table":
            return False
    return True

    # """Handle versioning tables exclusion"""
    # if name is None:
    #     return True
    # if type_ == "table":
    #     return not (name.endswith('_version') or
    #                name == 'transaction' or
    #                name.endswith('_version_id') or
    #                name.endswith('_temp'))
    # return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create versioning schema if it doesn't exist
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS versioning"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            # version_table_schema="versioning",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
