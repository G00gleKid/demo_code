from sqlalchemy import Column, Integer, String, CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Participant(Base):
    """Participant model representing team members."""

    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Team association
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # Biorhythm data
    chronotype = Column(String(20), nullable=False)  # 'morning', 'evening', 'intermediate'
    peak_hours_start = Column(Integer, nullable=False)  # 0-23
    peak_hours_end = Column(Integer, nullable=False)  # 0-23

    # Intelligence scores (0-100)
    emotional_intelligence = Column(Integer, nullable=False)
    social_intelligence = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    team = relationship("Team", back_populates="participants")

    __table_args__ = (
        CheckConstraint("emotional_intelligence >= 0 AND emotional_intelligence <= 100", name="check_ei_range"),
        CheckConstraint("social_intelligence >= 0 AND social_intelligence <= 100", name="check_si_range"),
        CheckConstraint("peak_hours_start >= 0 AND peak_hours_start <= 23", name="check_peak_start"),
        CheckConstraint("peak_hours_end >= 0 AND peak_hours_end <= 23", name="check_peak_end"),
        CheckConstraint("chronotype IN ('morning', 'evening', 'intermediate')", name="check_chronotype"),
    )
