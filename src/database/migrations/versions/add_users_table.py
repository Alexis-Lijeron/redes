"""Add users table and user_id to posts

Revision ID: add_users_table
Revises: 3f23dd39f8d6
Create Date: 2024-11-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_users_table'
down_revision = '3f23dd39f8d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla de usuarios
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índice único para email
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Agregar columna user_id a posts (nullable para posts existentes)
    op.add_column('posts', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Crear foreign key
    op.create_foreign_key(
        'fk_posts_user_id',
        'posts', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Eliminar foreign key
    op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
    
    # Eliminar columna user_id de posts
    op.drop_column('posts', 'user_id')
    
    # Eliminar índice
    op.drop_index('ix_users_email', 'users')
    
    # Eliminar tabla de usuarios
    op.drop_table('users')
