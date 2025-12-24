"""Скрипт для создания тестовых данных авторизации."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.team import Team
from app.models.user import User
from app.models.participant import Participant
from app.models.meeting import Meeting

# Create async engine
engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_test_teams(db: AsyncSession):
    """Создать тестовые команды."""
    print("Создание тестовых команд...")
    teams_data = [
        {"name": "Frontend Team"},
        {"name": "Backend Team"},
        {"name": "DevOps Team"},
    ]

    teams = []
    for data in teams_data:
        team = Team(**data)
        db.add(team)
        teams.append(team)

    await db.flush()
    print(f"✓ Создано {len(teams)} команд")
    return teams


async def create_test_users(db: AsyncSession, teams):
    """Создать тестовых тимлидов."""
    print("Создание тестовых тимлидов...")
    users_data = [
        {
            "email": "frontend@team.com",
            "password": "password123",
            "full_name": "Алиса (Frontend Lead)",
            "team_id": teams[0].id,
        },
        {
            "email": "backend@team.com",
            "password": "password123",
            "full_name": "Борис (Backend Lead)",
            "team_id": teams[1].id,
        },
        {
            "email": "devops@team.com",
            "password": "password123",
            "full_name": "Виктор (DevOps Lead)",
            "team_id": teams[2].id,
        },
    ]

    users = []
    for data in users_data:
        user = User(**data)
        db.add(user)
        users.append(user)

    await db.flush()
    print(f"✓ Создано {len(users)} тимлидов")
    return users, users_data


async def assign_participants_to_teams(db: AsyncSession, teams):
    """Распределить существующих участников по командам."""
    print("Распределение участников по командам...")

    # Получить всех участников
    result = await db.execute(select(Participant))
    participants = result.scalars().all()

    if not participants:
        print("⚠️ Нет участников для распределения")
        return

    # Распределить равномерно
    team_idx = 0
    for participant in participants:
        participant.team_id = teams[team_idx % len(teams)].id
        team_idx += 1

    print(f"✓ Распределено {len(participants)} участников по {len(teams)} командам")


async def assign_meetings_to_teams(db: AsyncSession, teams):
    """Назначить существующие встречи командам."""
    print("Назначение встреч командам...")

    # Получить все встречи
    result = await db.execute(select(Meeting))
    meetings = result.scalars().all()

    if not meetings:
        print("⚠️ Нет встреч для назначения")
        return

    # Распределить равномерно
    team_idx = 0
    for meeting in meetings:
        meeting.team_id = teams[team_idx % len(teams)].id
        team_idx += 1

    print(f"✓ Назначено {len(meetings)} встреч командам")


async def main():
    """Главная функция."""
    async with AsyncSessionLocal() as db:
        try:
            teams = await create_test_teams(db)
            users, users_data = await create_test_users(db, teams)
            await assign_participants_to_teams(db, teams)
            await assign_meetings_to_teams(db, teams)

            await db.commit()

            print("\n" + "=" * 50)
            print("✅ Тестовые данные успешно созданы!")
            print("=" * 50)
            print("\n📧 Учётные данные для входа:\n")
            for user_data in users_data:
                print(f"  Email: {user_data['email']}")
                print(f"  Password: {user_data['password']}")
                print()

        except Exception as e:
            await db.rollback()
            print(f"❌ Ошибка: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
