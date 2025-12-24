"""Миграция существующих данных в дефолтную команду."""

import asyncio
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.team import Team
from app.models.participant import Participant
from app.models.meeting import Meeting

# Create async engine
engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def migrate_data():
    async with AsyncSessionLocal() as db:
        # Создать дефолтную команду
        default_team = Team(name="Default Team")
        db.add(default_team)
        await db.flush()

        # Обновить всех участников
        await db.execute(
            update(Participant).values(team_id=default_team.id)
        )

        # Обновить все встречи
        await db.execute(
            update(Meeting).values(team_id=default_team.id)
        )

        await db.commit()
        print(f"✓ Данные мигрированы в команду: {default_team.name} (ID: {default_team.id})")


if __name__ == "__main__":
    asyncio.run(migrate_data())
