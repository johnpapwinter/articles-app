from sqlalchemy.orm import DeclarativeBase, declared_attr
# from sqlalchemy_continuum import versioning_manager, make_versioned
# from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin

# from src.articles.db.versioning_setup import setup_versioning


# from .versioning import make_versioned


class Base(DeclarativeBase):
    """Base class for all database models"""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

        # Configure versioning for all models
    # __versioned__ = {
    #         'transaction_column_name': 'transaction_id',
    #         'end_transaction_column_name': 'end_transaction_id',
    #         'operation_type_column_name': 'operation_type',
    #         'strategy': 'validity',
    #         'schema_name': 'versioning',
    #         'transaction_table_schema': 'versioning',
    # }


    def to_dict(self) -> dict:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns.values()
        }


# versioning_manager = setup_versioning(Base)
# # Then configure versioning manager
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
#
# # Initialize versioning with the plugin and base class
# make_versioned(user_cls=None, plugins=[PropertyModTrackerPlugin()])
# versioning_manager.declarative_base = Base

# This is important - declare these at the end
# from src.articles.models.article import Article  # noqa
# from src.articles.models.user import User  # noqa
# from src.articles.models.author import Author  # noqa
# from src.articles.models.comment import Comment  # noqa
# from src.articles.models.tag import Tag  # noqa
