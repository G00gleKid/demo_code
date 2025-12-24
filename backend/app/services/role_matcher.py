"""Role matcher service for calculating participant-role fitness scores."""

from app.constants.roles import ROLE_REQUIREMENTS
from app.models.participant import Participant


def calculate_parameter_fit(value: int, min_threshold: int, max_threshold: int) -> float:
    """
    Calculate how well a value fits within the desired range.

    Returns a fit score from 0.0 to 1.0:
    - 1.0: Perfect fit (exactly in the center of range)
    - 0.8-1.0: Good fit (within range but not centered)
    - <0.8: Below minimum or above maximum (penalized)

    Args:
        value: Actual parameter value (EI, SI, or energy)
        min_threshold: Minimum required value for the role
        max_threshold: Maximum required value for the role

    Returns:
        Fit score (0.0 to 1.0)
    """
    if min_threshold <= value <= max_threshold:
        # Value is within the desired range
        range_center = (min_threshold + max_threshold) / 2
        range_width = max_threshold - min_threshold

        if range_width == 0:
            # Edge case: min == max (exact value required)
            return 1.0

        distance_from_center = abs(value - range_center)
        # Closer to center = higher score (1.0 at center, 0.8 at edges)
        fit = 1.0 - (distance_from_center / (range_width / 2)) * 0.2
        return max(0.8, fit)

    elif value < min_threshold:
        # Below minimum: penalty based on deficit
        deficit = min_threshold - value
        # Penalty: -0.05 per point below minimum
        return max(0.0, 1.0 - (deficit * 0.05))

    else:  # value > max_threshold
        # Above maximum: smaller penalty (excess is less critical than deficit)
        excess = value - max_threshold
        # Penalty: -0.033 per point above maximum
        return max(0.0, 1.0 - (excess * 0.033))


def calculate_base_fitness(participant: Participant, role: str, energy: int) -> float:
    """
    Calculate base fitness score for participant-role combination.

    Evaluates how well the participant's attributes (EI, SI, energy)
    match the requirements for the given role.

    Algorithm:
    1. Get role requirements from ROLE_REQUIREMENTS
    2. Calculate fit for each parameter (EI, SI, energy)
    3. Average the three fit scores
    4. Convert to 0-100 scale

    Args:
        participant: Participant model with EI and SI scores
        role: Role name (e.g., 'moderator', 'critic')
        energy: Calculated energy level at meeting time (0-100)

    Returns:
        Base fitness score (0-100)
    """
    if role not in ROLE_REQUIREMENTS:
        raise ValueError(f"Unknown role: {role}")

    requirements = ROLE_REQUIREMENTS[role]

    # Calculate fit for each parameter
    ei_fit = calculate_parameter_fit(
        participant.emotional_intelligence,
        requirements["ei_min"],
        requirements["ei_max"]
    )

    si_fit = calculate_parameter_fit(
        participant.social_intelligence,
        requirements["si_min"],
        requirements["si_max"]
    )

    energy_fit = calculate_parameter_fit(
        energy,
        requirements["energy_min"],
        requirements["energy_max"]
    )

    # Average the three dimensions and convert to 0-100 scale
    base_score = (ei_fit + si_fit + energy_fit) / 3 * 100

    return base_score
