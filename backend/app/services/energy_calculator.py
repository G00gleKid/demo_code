"""Energy calculator service for computing participant energy levels at meeting time."""

from datetime import datetime

from app.models.participant import Participant


def calculate_energy(participant: Participant, meeting_time: datetime) -> int:
    """
    Calculate participant's energy level (0-100) at meeting time.

    Based on participant's biorhythm data (chronotype and peak hours),
    calculates how much energy the participant will have at the meeting time.

    Algorithm:
    1. Extract hour of meeting (0-23)
    2. Calculate distance from participant's peak hours center
    3. Map distance to energy percentage (0-100)

    Handles edge cases:
    - Peak hours wrapping around midnight (e.g., 22:00-02:00)
    - Circular distance calculation through midnight

    Args:
        participant: Participant model with peak_hours_start/end
        meeting_time: Scheduled meeting datetime

    Returns:
        Energy level (0-100)
    """
    meeting_hour = meeting_time.hour
    peak_start = participant.peak_hours_start
    peak_end = participant.peak_hours_end

    # Calculate peak center, handling wrap-around
    if peak_start <= peak_end:
        # Normal case: peak within same day (e.g., 9-12)
        peak_center = (peak_start + peak_end) / 2
    else:
        # Wrap-around case: peak crosses midnight (e.g., 22-2)
        peak_center = ((peak_start + peak_end + 24) / 2) % 24

    # Calculate circular distance from peak center
    direct_distance = abs(meeting_hour - peak_center)
    wrap_distance = 24 - direct_distance
    distance = min(direct_distance, wrap_distance)

    # Map distance to energy level
    # Close to peak (0-2 hours): 80-100%
    # Medium distance (2-4 hours): 55-70%
    # Far from peak (4-6 hours): 35-45%
    # Very far (6+ hours): 0-30%

    if distance <= 2:
        return int(100 - (distance * 10))  # 100, 90, 80
    elif distance <= 4:
        return int(80 - ((distance - 2) * 15))  # 70, 55
    elif distance <= 6:
        return int(55 - ((distance - 4) * 10))  # 45, 35
    else:
        return max(0, int(35 - ((distance - 6) * 5)))  # 30, 25, 20, ...
