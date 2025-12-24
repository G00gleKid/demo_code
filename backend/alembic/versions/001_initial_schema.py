"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create participants table
    op.create_table(
        'participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('chronotype', sa.String(length=20), nullable=False),
        sa.Column('peak_hours_start', sa.Integer(), nullable=False),
        sa.Column('peak_hours_end', sa.Integer(), nullable=False),
        sa.Column('emotional_intelligence', sa.Integer(), nullable=False),
        sa.Column('social_intelligence', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('emotional_intelligence >= 0 AND emotional_intelligence <= 100', name='check_ei_range'),
        sa.CheckConstraint('social_intelligence >= 0 AND social_intelligence <= 100', name='check_si_range'),
        sa.CheckConstraint('peak_hours_start >= 0 AND peak_hours_start <= 23', name='check_peak_start'),
        sa.CheckConstraint('peak_hours_end >= 0 AND peak_hours_end <= 23', name='check_peak_end'),
        sa.CheckConstraint("chronotype IN ('morning', 'evening', 'intermediate')", name='check_chronotype'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_participants_id'), 'participants', ['id'], unique=False)
    op.create_index(op.f('ix_participants_email'), 'participants', ['email'], unique=True)

    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('meeting_type', sa.String(length=50), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)
    op.create_index(op.f('ix_meetings_scheduled_time'), 'meetings', ['scheduled_time'], unique=False)

    # Create meeting_participants association table
    op.create_table(
        'meeting_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create role_assignments table
    op.create_table(
        'role_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('fitness_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('meeting_id', 'participant_id', name='unique_meeting_participant')
    )
    op.create_index(op.f('ix_role_assignments_id'), 'role_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_role_assignments_meeting_id'), 'role_assignments', ['meeting_id'], unique=False)
    op.create_index(op.f('ix_role_assignments_participant_id'), 'role_assignments', ['participant_id'], unique=False)
    op.create_index(op.f('ix_role_assignments_created_at'), 'role_assignments', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_role_assignments_created_at'), table_name='role_assignments')
    op.drop_index(op.f('ix_role_assignments_participant_id'), table_name='role_assignments')
    op.drop_index(op.f('ix_role_assignments_meeting_id'), table_name='role_assignments')
    op.drop_index(op.f('ix_role_assignments_id'), table_name='role_assignments')
    op.drop_table('role_assignments')
    op.drop_table('meeting_participants')
    op.drop_index(op.f('ix_meetings_scheduled_time'), table_name='meetings')
    op.drop_index(op.f('ix_meetings_id'), table_name='meetings')
    op.drop_table('meetings')
    op.drop_index(op.f('ix_participants_email'), table_name='participants')
    op.drop_index(op.f('ix_participants_id'), table_name='participants')
    op.drop_table('participants')
