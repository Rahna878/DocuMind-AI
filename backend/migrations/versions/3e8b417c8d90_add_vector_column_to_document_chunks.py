"""add_vector_column_to_document_chunks

Revision ID: 3e8b417c8d90
Revises: 1ca0cd751932
Create Date: 2026-11-04 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '3e8b417c8d90'
down_revision: Union[str, Sequence[str], None] = '1ca0cd751932'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension is enabled in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add the 768-dimensional embedding column to document_chunks
    op.add_column(
        'document_chunks',
        sa.Column('embedding', Vector(768), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('document_chunks', 'embedding')

