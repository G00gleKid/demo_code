"""Comprehensive seed script to populate ALL database tables with test data.

This script creates:
- 2 teams (Команда Альфа, Команда Бета)
- 3 users (team leads)
- 15 participants (10 for Team 1, 5 for Team 2)
- 22+ meetings with role assignments
"""

from datetime import datetime, timedelta, timezone
import random
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine, Base
from app.models.team import Team
from app.models.user import User
from app.models.participant import Participant
from app.models.meeting import Meeting
from app.services.assignment_engine import assign_roles


async def create_teams(db: AsyncSession) -> list[Team]:
    """Create test teams."""
    print("Creating test teams...")
    teams_data = [
        {"name": "Команда Альфа"},
        {"name": "Команда Бета"},
    ]

    teams = []
    for idx, data in enumerate(teams_data, 1):
        team = Team(**data)
        db.add(team)
        teams.append(team)
        print(f"  [{idx}/{len(teams_data)}] Added team: {data['name']}")

    print("  Committing teams to database...")
    await db.commit()

    print("  Refreshing team data...")
    for t in teams:
        await db.refresh(t)

    print(f"✓ Created {len(teams)} teams")
    return teams


async def create_users(db: AsyncSession, teams: list[Team]) -> list[User]:
    """Create test users (team leads)."""
    print("\nCreating test users...")
    users_data = [
        {
            "email": "anna.ivanova@team-alpha.ru",
            "password": "demo123",
            "full_name": "Анна Иванова",
            "team_id": teams[0].id,
            "is_active": True,
        },
        {
            "email": "boris.petrov@team-beta.ru",
            "password": "demo123",
            "full_name": "Борис Петров",
            "team_id": teams[1].id,
            "is_active": True,
        },
        {
            "email": "vera.sidorova@team-alpha.ru",
            "password": "demo123",
            "full_name": "Вера Сидорова",
            "team_id": teams[0].id,
            "is_active": True,
        },
    ]

    users = []
    for idx, data in enumerate(users_data, 1):
        user = User(**data)
        db.add(user)
        users.append(user)
        print(f"  [{idx}/{len(users_data)}] Added user: {data['full_name']} ({data['email']})")

    print("  Committing users to database...")
    await db.commit()

    print("  Refreshing user data...")
    for u in users:
        await db.refresh(u)

    print(f"✓ Created {len(users)} users")
    return users


async def create_participants(db: AsyncSession, teams: list[Team]) -> list[Participant]:
    """Create diverse set of test participants for both teams."""
    print("\nCreating test participants...")

    # Team 1 participants (10) - Команда Альфа
    team1_participants_data = [
        {
            "name": "Алиса Жукова",
            "email": "alisa.zhukova@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "morning",
            "peak_hours_start": 7,
            "peak_hours_end": 11,
            "emotional_intelligence": 85,
            "social_intelligence": 90,
        },
        {
            "name": "Борис Смирнов",
            "email": "boris.smirnov@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "evening",
            "peak_hours_start": 14,
            "peak_hours_end": 18,
            "emotional_intelligence": 65,
            "social_intelligence": 70,
        },
        {
            "name": "Кира Давыдова",
            "email": "kira.davydova@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "intermediate",
            "peak_hours_start": 10,
            "peak_hours_end": 14,
            "emotional_intelligence": 92,
            "social_intelligence": 88,
        },
        {
            "name": "Дмитрий Чернов",
            "email": "dmitry.chernov@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "morning",
            "peak_hours_start": 6,
            "peak_hours_end": 10,
            "emotional_intelligence": 78,
            "social_intelligence": 82,
        },
        {
            "name": "Ева Мартынова",
            "email": "eva.martynova@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "evening",
            "peak_hours_start": 16,
            "peak_hours_end": 20,
            "emotional_intelligence": 58,
            "social_intelligence": 55,
        },
        {
            "name": "Филипп Волков",
            "email": "filipp.volkov@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "intermediate",
            "peak_hours_start": 9,
            "peak_hours_end": 13,
            "emotional_intelligence": 72,
            "social_intelligence": 78,
        },
        {
            "name": "Галина Лебедева",
            "email": "galina.lebedeva@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "morning",
            "peak_hours_start": 8,
            "peak_hours_end": 12,
            "emotional_intelligence": 88,
            "social_intelligence": 85,
        },
        {
            "name": "Григорий Брунов",
            "email": "grigory.brunov@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "evening",
            "peak_hours_start": 15,
            "peak_hours_end": 19,
            "emotional_intelligence": 62,
            "social_intelligence": 68,
        },
        {
            "name": "Ирина Тарасова",
            "email": "irina.tarasova@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "intermediate",
            "peak_hours_start": 11,
            "peak_hours_end": 15,
            "emotional_intelligence": 95,
            "social_intelligence": 92,
        },
        {
            "name": "Яков Андреев",
            "email": "yakov.andreev@team-alpha.ru",
            "team_id": teams[0].id,
            "chronotype": "morning",
            "peak_hours_start": 7,
            "peak_hours_end": 11,
            "emotional_intelligence": 75,
            "social_intelligence": 80,
        },
    ]

    # Team 2 participants (5) - Команда Бета
    team2_participants_data = [
        {
            "name": "Максим Козлов",
            "email": "maxim.kozlov@team-beta.ru",
            "team_id": teams[1].id,
            "chronotype": "morning",
            "peak_hours_start": 7,
            "peak_hours_end": 11,
            "emotional_intelligence": 70,
            "social_intelligence": 75,
        },
        {
            "name": "Наталья Орлова",
            "email": "natalia.orlova@team-beta.ru",
            "team_id": teams[1].id,
            "chronotype": "evening",
            "peak_hours_start": 16,
            "peak_hours_end": 20,
            "emotional_intelligence": 82,
            "social_intelligence": 78,
        },
        {
            "name": "Олег Попов",
            "email": "oleg.popov@team-beta.ru",
            "team_id": teams[1].id,
            "chronotype": "intermediate",
            "peak_hours_start": 10,
            "peak_hours_end": 14,
            "emotional_intelligence": 65,
            "social_intelligence": 88,
        },
        {
            "name": "Полина Морозова",
            "email": "polina.morozova@team-beta.ru",
            "team_id": teams[1].id,
            "chronotype": "morning",
            "peak_hours_start": 8,
            "peak_hours_end": 12,
            "emotional_intelligence": 90,
            "social_intelligence": 85,
        },
        {
            "name": "Роман Новиков",
            "email": "roman.novikov@team-beta.ru",
            "team_id": teams[1].id,
            "chronotype": "evening",
            "peak_hours_start": 15,
            "peak_hours_end": 19,
            "emotional_intelligence": 58,
            "social_intelligence": 62,
        },
    ]

    all_participants_data = team1_participants_data + team2_participants_data
    participants = []

    for idx, data in enumerate(all_participants_data, 1):
        participant = Participant(**data)
        db.add(participant)
        participants.append(participant)
        team_name = "Команда Альфа" if data["team_id"] == teams[0].id else "Команда Бета"
        print(f"  [{idx}/{len(all_participants_data)}] Added participant: {data['name']} ({team_name})")

    print("  Committing participants to database...")
    await db.commit()

    print("  Refreshing participant data...")
    for p in participants:
        await db.refresh(p)

    print(f"✓ Created {len(participants)} participants (Team 1: {len(team1_participants_data)}, Team 2: {len(team2_participants_data)})")
    return participants


# Meeting title templates by type
MEETING_TITLES = {
    "brainstorm": [
        "Идеи для нового функционала",
        "Мозговой штурм: улучшения UX",
        "Креативная сессия команды",
    ],
    "review": [
        "Ретроспектива спринта",
        "Разбор итогов недели",
        "Code Review сессия",
    ],
    "planning": [
        "Планирование спринта",
        "Дорожная карта проекта",
        "Распределение задач",
    ],
    "status_update": [
        "Статус по задачам",
        "Daily Standup",
        "Синхронизация команды",
    ],
}


async def create_historical_meetings(
    db: AsyncSession,
    participants_team1: list[Participant],
    team1_id: int
) -> list[Meeting]:
    """Create past meetings with role assignments for Team 1."""
    print("\nCreating historical meetings with role assignments...")
    now = datetime.now(timezone.utc)

    # Configuration for 18 historical meetings (last 7 days)
    historical_config = [
        # 7 дней назад (2 встречи)
        {"days_ago": 7, "hour": 10, "type": "brainstorm", "participants_count": 7},
        {"days_ago": 7, "hour": 15, "type": "status_update", "participants_count": 5},

        # 6 дней назад (3 встречи)
        {"days_ago": 6, "hour": 9, "type": "planning", "participants_count": 8},
        {"days_ago": 6, "hour": 14, "type": "review", "participants_count": 6},
        {"days_ago": 6, "hour": 17, "type": "brainstorm", "participants_count": 7},

        # 5 дней назад (1 встреча)
        {"days_ago": 5, "hour": 11, "type": "status_update", "participants_count": 6},

        # 4 дня назад (3 встречи)
        {"days_ago": 4, "hour": 10, "type": "brainstorm", "participants_count": 8},
        {"days_ago": 4, "hour": 14, "type": "planning", "participants_count": 7},
        {"days_ago": 4, "hour": 16, "type": "review", "participants_count": 6},

        # 3 дня назад (2 встречи)
        {"days_ago": 3, "hour": 9, "type": "status_update", "participants_count": 5},
        {"days_ago": 3, "hour": 15, "type": "brainstorm", "participants_count": 7},

        # 2 дня назад (4 встречи)
        {"days_ago": 2, "hour": 10, "type": "planning", "participants_count": 8},
        {"days_ago": 2, "hour": 12, "type": "status_update", "participants_count": 6},
        {"days_ago": 2, "hour": 14, "type": "review", "participants_count": 7},
        {"days_ago": 2, "hour": 17, "type": "brainstorm", "participants_count": 7},

        # 1 день назад (3 встречи)
        {"days_ago": 1, "hour": 9, "type": "planning", "participants_count": 8},
        {"days_ago": 1, "hour": 14, "type": "brainstorm", "participants_count": 6},
        {"days_ago": 1, "hour": 16, "type": "status_update", "participants_count": 5},
    ]

    meetings = []
    total_meetings = len(historical_config)

    for idx, config in enumerate(historical_config, 1):
        # Calculate meeting time in the past
        meeting_time = now - timedelta(days=config["days_ago"], hours=(24 - config["hour"]))

        # Select random title for this meeting type
        title = random.choice(MEETING_TITLES[config["type"]])

        # Select random participants
        selected_participants = random.sample(
            participants_team1,
            min(config["participants_count"], len(participants_team1))
        )

        print(f"  [{idx}/{total_meetings}] Creating '{title}' ({config['type']}) - {config['days_ago']} days ago")
        print(f"      Participants: {len(selected_participants)}")

        # Create meeting
        meeting = Meeting(
            title=title,
            meeting_type=config["type"],
            scheduled_time=meeting_time,
            team_id=team1_id
        )
        meeting.participants = selected_participants
        db.add(meeting)

        print("      Flushing to get meeting ID...")
        await db.flush()  # Get meeting ID without committing

        # Assign roles using the algorithm
        try:
            print("      Calculating role assignments...")
            await assign_roles(db, meeting.id)
            print("      ✓ Roles assigned successfully")
        except Exception as e:
            print(f"      ✗ Failed to assign roles: {e}")

        meetings.append(meeting)

    print("  Committing all meetings to database...")
    await db.commit()

    print("  Refreshing meeting data...")
    for m in meetings:
        await db.refresh(m)

    print(f"✓ Created {len(meetings)} historical meetings with role assignments")
    return meetings


async def create_future_meetings(
    db: AsyncSession,
    participants_by_team: dict[int, list[Participant]],
    team_ids: list[int]
) -> list[Meeting]:
    """Create future meetings for both teams."""
    print("\nCreating future meetings...")
    now = datetime.now(timezone.utc)

    # Team 1 future meetings (3)
    team1_meetings_data = [
        {
            "title": "Weekly Brainstorm Session",
            "meeting_type": "brainstorm",
            "scheduled_time": now + timedelta(days=1, hours=10),
            "team_id": team_ids[0],
            "participant_ids": [p.id for p in participants_by_team[team_ids[0]][:8]],
        },
        {
            "title": "Sprint Retrospective",
            "meeting_type": "review",
            "scheduled_time": now + timedelta(days=2, hours=15),
            "team_id": team_ids[0],
            "participant_ids": [p.id for p in participants_by_team[team_ids[0]][2:10]],
        },
        {
            "title": "Sprint Planning",
            "meeting_type": "planning",
            "scheduled_time": now + timedelta(days=3, hours=9),
            "team_id": team_ids[0],
            "participant_ids": [p.id for p in participants_by_team[team_ids[0]]],
        },
    ]

    # Team 2 future meetings (2)
    team2_meetings_data = [
        {
            "title": "Планирование квартала",
            "meeting_type": "planning",
            "scheduled_time": now + timedelta(days=1, hours=14),
            "team_id": team_ids[1],
            "participant_ids": [p.id for p in participants_by_team[team_ids[1]]],
        },
        {
            "title": "Обзор продукта",
            "meeting_type": "review",
            "scheduled_time": now + timedelta(days=4, hours=11),
            "team_id": team_ids[1],
            "participant_ids": [p.id for p in participants_by_team[team_ids[1]][:4]],
        },
    ]

    all_meetings_data = team1_meetings_data + team2_meetings_data
    meetings = []

    for idx, data in enumerate(all_meetings_data, 1):
        participant_ids = data.pop("participant_ids")
        meeting = Meeting(**data)

        team_name = "Команда Альфа" if data["team_id"] == team_ids[0] else "Команда Бета"
        print(f"  [{idx}/{len(all_meetings_data)}] Creating future meeting: {data['title']} ({team_name})")

        # Add participants
        stmt = select(Participant).where(Participant.id.in_(participant_ids))
        result = await db.execute(stmt)
        meeting_participants = result.scalars().all()
        meeting.participants = list(meeting_participants)

        db.add(meeting)
        meetings.append(meeting)

    print("  Committing future meetings to database...")
    await db.commit()

    print("  Refreshing meeting data...")
    for m in meetings:
        await db.refresh(m)

    print(f"✓ Created {len(meetings)} future meetings (Team 1: {len(team1_meetings_data)}, Team 2: {len(team2_meetings_data)})")
    return meetings


async def seed_database():
    """Main seeding function - populates ALL database tables."""
    print("=" * 60)
    print("Starting comprehensive database seeding...")
    print("=" * 60)

    # Create tables
    print("\nInitializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created")

    # Create session
    async with AsyncSessionLocal() as db:
        try:
            # Check if data already exists
            print("\nChecking existing data...")
            stmt = select(Team)
            result = await db.execute(stmt)
            existing = result.scalars().all()
            existing_count = len(existing)

            if existing_count > 0:
                print(f"\n⚠ Database already contains {existing_count} teams.")
                response = input("Clear and reseed? (y/n): ")
                if response.lower() != 'y':
                    print("Seeding cancelled.")
                    return

            # STEP 1: Create Teams
            print("\n" + "=" * 60)
            print("STEP 1: Creating Teams")
            print("=" * 60)
            teams = await create_teams(db)

            # STEP 2: Create Users
            print("\n" + "=" * 60)
            print("STEP 2: Creating Users (Team Leads)")
            print("=" * 60)
            users = await create_users(db, teams)

            # STEP 3: Create Participants
            print("\n" + "=" * 60)
            print("STEP 3: Creating Participants")
            print("=" * 60)
            all_participants = await create_participants(db, teams)

            # Separate participants by team
            participants_team1 = [p for p in all_participants if p.team_id == teams[0].id]
            participants_team2 = [p for p in all_participants if p.team_id == teams[1].id]
            participants_by_team = {
                teams[0].id: participants_team1,
                teams[1].id: participants_team2,
            }

            # STEP 4: Create Historical Meetings (Team 1 only)
            print("\n" + "=" * 60)
            print("STEP 4: Creating Historical Meetings (Team 1)")
            print("=" * 60)
            print("Note: Role assignment calculations may take 10-20 seconds per meeting")
            historical_meetings = await create_historical_meetings(
                db,
                participants_team1,
                teams[0].id
            )

            # STEP 5: Create Future Meetings (Both teams)
            print("\n" + "=" * 60)
            print("STEP 5: Creating Future Meetings")
            print("=" * 60)
            future_meetings = await create_future_meetings(
                db,
                participants_by_team,
                [teams[0].id, teams[1].id]
            )

            # Print summary
            print("\n" + "=" * 60)
            print("✓ DATABASE SEEDED SUCCESSFULLY!")
            print("=" * 60)
            print(f"  Teams:")
            print(f"    - {len(teams)} teams created")
            for team in teams:
                print(f"      • {team.name} (ID: {team.id})")

            print(f"\n  Users:")
            print(f"    - {len(users)} users created")
            for user in users:
                print(f"      • {user.full_name} ({user.email})")

            print(f"\n  Participants:")
            print(f"    - {len(all_participants)} total participants")
            print(f"      • Команда Альфа: {len(participants_team1)} participants")
            print(f"      • Команда Бета: {len(participants_team2)} participants")

            print(f"\n  Meetings:")
            print(f"    - {len(historical_meetings)} historical meetings (with role assignments)")
            print(f"    - {len(future_meetings)} future meetings (ready for assignment)")
            print(f"    - Total: {len(historical_meetings) + len(future_meetings)} meetings")

            print("\n💡 You can now:")
            print("   - View participant statistics in the frontend")
            print("   - Assign roles to future meetings")
            print("   - Test multi-tenant isolation")
            print("=" * 60)

        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ ERROR SEEDING DATABASE")
            print("=" * 60)
            print(f"Error details: {e}")
            print("=" * 60)
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
