from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RoleAssignment(Base):
    """Role assignment model storing results of the algorithm."""

    __tablename__ = "role_assignments"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    fitness_score = Column(Float, nullable=False)  # For transparency
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    meeting = relationship("Meeting", back_populates="role_assignments")
    participant = relationship("Participant", backref="role_assignments")

    __table_args__ = (
        UniqueConstraint("meeting_id", "participant_id", name="unique_meeting_participant"),
    )
