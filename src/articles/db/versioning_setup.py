# # src/articles/db/versioning_setup.py
#
# from sqlalchemy_continuum import make_versioned, versioning_manager
# from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin
# from sqlalchemy import event, DDL, MetaData
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.schema import CreateSchema
#
#
# def setup_versioning(Base):
#     """
#     Configure SQLAlchemy Continuum versioning with async support.
#
#     This setup ensures proper versioning in an async context by:
#     1. Configuring the versioning manager with the correct schema settings
#     2. Setting up proper transaction handling for async sessions
#     3. Ensuring all database operations respect schema qualifications
#     """
#     # Create metadata for versioning schema
#     versioning_metadata = MetaData(schema='versioning')
#
#     # Configure versioning manager
#     versioning_manager.options.update({
#         'native_versioning': True,
#         'transaction_column_name': 'transaction_id',
#         'end_transaction_column_name': 'end_transaction_id',
#         'operation_type_column_name': 'operation_type',
#         'strategy': 'validity',
#         'use_module_name': False,
#         'schema_name': 'versioning',
#         'transaction_table_schema': 'versioning',
#         'metadata': versioning_metadata,
#         'version_table_schema': 'versioning',
#         # Ensure all table references include schema
#         'table_name': lambda obj: f"versioning.{obj.__tablename__}",
#         # Configure transaction class options
#         'transaction_cls': {
#             '__table_args__': {'schema': 'versioning'}
#         }
#     })
#
#     # Initialize versioning
#     make_versioned(user_cls=None, plugins=[PropertyModTrackerPlugin()])
#
#     # Set the declarative base
#     versioning_manager.declarative_base = Base
#
#     # Add schema creation event listener
#     @event.listens_for(Base.metadata, 'before_create')
#     def create_versioning_schema(target, connection, **kw):
#         """Ensure versioning schema exists before any tables are created"""
#         connection.execute(CreateSchema('versioning', if_not_exists=True))
#
#     return versioning_manager