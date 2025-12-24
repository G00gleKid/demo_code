"""Assignment engine service - orchestrates the role assignment algorithm."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.roles import ALL_ROLES
from app.constants.meeting_types import MEETING_MULTIPLIERS
from app.models.meeting import Meeting
from app.models.participant import Participant
from app.models.role_assignment import RoleAssignment
from app.services.energy_calculator import calculate_energy
from app.services.role_matcher import calculate_base_fitness


async def get_history_penalty(db: AsyncSession, participant_id: int, role: str) -> float | str:
    """
    Calculate penalty based on participant's recent role history (Validator 1).

    Checks if the participant has performed this role in recent meetings
    and applies penalties to avoid role repetition.

    Rules from tech_task.md lines 23-26:
    - Last 2 meetings: -40% weight
    - Last 3 meetings: -70% weight
    - Last 4+ meetings: exclude from candidates

    Args:
        db: Database session
        participant_id: Participant ID
        role: Role to check

    Returns:
        - Float (0.0-0.7): Penalty percentage
        - "EXCLUDE": Participant should be excluded from this role
    """
    # Query last assignments for this participant, ordered by date DESC
    stmt = (
        select(RoleAssignment)
        .where(RoleAssignment.participant_id == participant_id)
        .order_by(RoleAssignment.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    recent_assignments = result.scalars().all()

    # Count consecutive occurrences of this role
    consecutive_count = 0
    for assignment in recent_assignments:
        if assignment.role == role:
            consecutive_count += 1
        else:
            break  # Stop at first different role

    if consecutive_count >= 4:
        return "EXCLUDE"
    elif consecutive_count == 3:
        return 0.7
    elif consecutive_count == 2:
        return 0.4
    else:
        return 0.0


def get_meeting_multiplier(meeting_type: str, role: str) -> float:
    """
    Get context multiplier for role based on meeting type (Validator 2).

    Different meeting types prioritize different roles.
    Multipliers from tech_task.md lines 28-35.

    Args:
        meeting_type: Type of meeting ('brainstorm', 'review', etc.)
        role: Role name

    Returns:
        Multiplier (0.5 to 1.5)
    """
    return MEETING_MULTIPLIERS.get(meeting_type, {}).get(role, 1.0)


def greedy_assignment(fitness_matrix: dict, participants: list[Participant], roles: list[str]) -> list[dict]:
    """
    Greedy algorithm for role assignment.

    Strategy:
    1. Sort all (participant, role) pairs by fitness score (DESC)
    2. Iterate and assign greedily
    3. Skip if participant already assigned OR role already filled
    4. Stop when all 7 roles filled OR all participants assigned

    For determinism, break ties alphabetically by participant name.

    Args:
        fitness_matrix: Dict mapping (participant_id, role) -> score
        participants: List of participants
        roles: List of roles to assign

    Returns:
        List of assignment dicts with participant_id, role, score
    """
    # Convert fitness matrix to sorted list
    assignments_pool = [
        {
            "participant_id": p_id,
            "role": r,
            "score": score
        }
        for (p_id, r), score in fitness_matrix.items()
    ]

    # Create participant name map for tie-breaking
    participant_names = {p.id: p.name for p in participants}

    # Sort by score DESC, then by participant name (for determinism)
    assignments_pool.sort(
        key=lambda x: (-x["score"], participant_names.get(x["participant_id"], ""))
    )

    assigned_participants = set()
    assigned_roles = set()
    final_assignments = []

    for candidate in assignments_pool:
        p_id = candidate["participant_id"]
        role = candidate["role"]

        # Skip if already assigned
        if p_id in assigned_participants or role in assigned_roles:
            continue

        # Make assignment
        final_assignments.append(candidate)
        assigned_participants.add(p_id)
        assigned_roles.add(role)

        # Stop if all roles filled
        if len(assigned_roles) == len(roles):
            break

    return final_assignments


async def assign_roles(db: AsyncSession, meeting_id: int) -> list[RoleAssignment]:
    """
    Main function to assign roles for a meeting.

    Orchestrates the full algorithm:
    1. Load meeting and participants
    2. Calculate fitness scores for all (participant, role) combinations
    3. Apply Validator 1 (role history penalty)
    4. Apply Validator 2 (meeting context multiplier)
    5. Run greedy assignment algorithm
    6. Save results to database

    Args:
        db: Database session
        meeting_id: ID of the meeting

    Returns:
        List of RoleAssignment objects

    Raises:
        ValueError: If meeting not found or has no participants
    """
    # Load meeting with participants
    from sqlalchemy.orm import selectinload

    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise ValueError(f"Meeting {meeting_id} not found")

    participants = meeting.participants
    if not participants:
        raise ValueError(f"Meeting {meeting_id} has no participants")

    # Calculate fitness scores for all combinations
    fitness_matrix = {}

    for participant in participants:
        # Calculate energy level at meeting time
        energy = calculate_energy(participant, meeting.scheduled_time)

        for role in ALL_ROLES:
            # Calculate base fitness
            base_score = calculate_base_fitness(participant, role, energy)

            # Apply Validator 1: Role balance (history check)
            history_penalty = await get_history_penalty(db, participant.id, role)
            if history_penalty == "EXCLUDE":
                continue  # Skip this combination

            # Apply Validator 2: Meeting context multiplier
            context_multiplier = get_meeting_multiplier(meeting.meeting_type, role)

            # Calculate final score
            final_score = base_score * (1 - history_penalty) * context_multiplier

            fitness_matrix[(participant.id, role)] = final_score

    # Run greedy assignment algorithm
    assignments = greedy_assignment(fitness_matrix, participants, ALL_ROLES)

    # Delete existing assignments for this meeting (if re-running)
    delete_stmt = select(RoleAssignment).where(RoleAssignment.meeting_id == meeting_id)
    result = await db.execute(delete_stmt)
    existing_assignments = result.scalars().all()
    for assignment in existing_assignments:
        await db.delete(assignment)

    # Save to database
    db_assignments = []
    for assignment in assignments:
        db_assignment = RoleAssignment(
            meeting_id=meeting_id,
            participant_id=assignment["participant_id"],
            role=assignment["role"],
            fitness_score=assignment["score"]
        )
        db.add(db_assignment)
        db_assignments.append(db_assignment)

    await db.commit()

    # Refresh to get created_at timestamps
    for assignment in db_assignments:
        await db.refresh(assignment)

    return db_assignments
