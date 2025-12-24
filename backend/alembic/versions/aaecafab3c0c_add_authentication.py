"""add_authentication

Revision ID: aaecafab3c0c
Revises: 001
Create Date: 2025-12-23 23:50:28.767592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaecafab3c0c'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_team_id'), 'users', ['team_id'], unique=False)

    # Add team_id to participants (nullable initially for migration)
    op.add_column('participants', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_participants_team_id', 'participants', 'teams', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_participants_team_id'), 'participants', ['team_id'], unique=False)

    # Add team_id to meetings (nullable initially for migration)
    op.add_column('meetings', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_meetings_team_id', 'meetings', 'teams', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_meetings_team_id'), 'meetings', ['team_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_meetings_team_id'), table_name='meetings')
    op.drop_constraint('fk_meetings_team_id', 'meetings', type_='foreignkey')
    op.drop_column('meetings', 'team_id')

    op.drop_index(op.f('ix_participants_team_id'), table_name='participants')
    op.drop_constraint('fk_participants_team_id', 'participants', type_='foreignkey')
    op.drop_column('participants', 'team_id')

    op.drop_index(op.f('ix_users_team_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
