"""Initial migration

Revision ID: 108779776143
Revises: 
Create Date: 2024-12-30 14:58:15.240366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.articles.utils.logging import setup_logging

# revision identifiers, used by Alembic.
revision: str = '108779776143'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


logger = setup_logging(__name__)


def upgrade() -> None:
    current_step = "Starting migration"
    try:
        # Log each step of the migration process
        # current_step = "Creating versioning schema"
        # op.execute("CREATE SCHEMA IF NOT EXISTS versioning")
        # logger.info("Created versioning schema")
        #
        # current_step = "Creating transaction sequence"
        # op.execute("""
        #             CREATE SEQUENCE IF NOT EXISTS versioning.transaction_id_seq
        #             START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1
        #         """)
        # logger.info("Created transaction sequence")
        #
        # current_step = "Creating transaction table"
        # op.create_table(
        #     'transaction',
        #     sa.Column('id', sa.BigInteger(),
        #               sa.Sequence('transaction_id_seq', schema='versioning'),
        #               server_default=sa.text("nextval('versioning.transaction_id_seq')"),
        #               nullable=False),
        #     sa.Column('issued_at', sa.DateTime(timezone=True),
        #               server_default=sa.text('CURRENT_TIMESTAMP'),
        #               nullable=True),
        #     sa.Column('user_id', sa.Integer(), nullable=True),
        #     sa.Column('remote_addr', sa.String(50), nullable=True),
        #     sa.PrimaryKeyConstraint('id'),
        #     schema='versioning'
        # )
        # logger.info("Created transaction table")


        # Create base tables
        current_step = "Creating user table"
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=255), nullable=False),
            sa.Column('password', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('username')
        )
        logger.info("Created user table")

        current_step = "Creating authors table"
        op.create_table(
            'authors',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

        current_step = "Creating tags table"
        op.create_table(
            'tags',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        logger.info("Created tags table")

        current_step = "Creating article table"
        op.create_table(
            'articles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('abstract', sa.Text(), nullable=False),
            sa.Column('publication_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('owner_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        logger.info("Created article table")

        current_step = "Creating article_authors table"
        op.create_table(
            'article_authors',
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('author_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('article_id', 'author_id')
        )
        logger.info("Created article_authors table")

        current_step = "Creating article_tags table"
        op.create_table(
            'article_tags',
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('tag_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('article_id', 'tag_id')
        )
        logger.info("Created article_tags table")

        current_step = "Creating comments table"
        op.create_table(
            'comments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        logger.info("Created comments table")
    except Exception as e:
        logger.error(f"Error in {current_step} during migration: {str(e)}")
        raise

def downgrade() -> None:
    try:
        # Drop tables in reverse order
        op.drop_table('comments')
        op.drop_table('article_tags')
        op.drop_table('article_authors')
        op.drop_table('articles')
        op.drop_table('tags')
        op.drop_table('authors')
        op.drop_table('users')
        op.drop_table('transaction', schema='versioning')
        op.execute("DROP SCHEMA IF EXISTS versioning")
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

