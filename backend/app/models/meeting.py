from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# Association table for many-to-many relationship
meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("meeting_id", Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
    Column("participant_id", Integer, ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
)


class Meeting(Base):
    """Meeting model."""

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    meeting_type = Column(String(50), nullable=False)  # 'brainstorm', 'review', 'planning', 'status_update'
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Team association
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    team = relationship("Team", back_populates="meetings")
    participants = relationship("Participant", secondary=meeting_participants, backref="meetings")
    role_assignments = relationship("RoleAssignment", back_populates="meeting", cascade="all, delete-orphan")
