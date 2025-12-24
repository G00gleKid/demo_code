# Статус реализации системы авторизации

## ✅ Выполнено (Backend - 60%)

### Конфигурация и зависимости
- ✅ Добавлены зависимости: python-jose, passlib
- ✅ Обновлён [config.py](backend/app/config.py) - добавлены SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS

### Модели данных
- ✅ Создана модель [Team](backend/app/models/team.py)
- ✅ Создана модель [User](backend/app/models/user.py)
- ✅ Обновлена модель [Participant](backend/app/models/participant.py) - добавлен team_id
- ✅ Обновлена модель [Meeting](backend/app/models/meeting.py) - добавлен team_id

### Схемы (Pydantic)
- ✅ Создана [team.py](backend/app/schemas/team.py) - Team, TeamBase, TeamCreate
- ✅ Создана [user.py](backend/app/schemas/user.py) - User, UserWithTeam, UserLogin, TokenResponse

### Сервисы
- ✅ Создан [auth_service.py](backend/app/services/auth_service.py) - JWT создание/валидация
- ✅ Создан [user_service.py](backend/app/services/user_service.py) - аутентификация

### Зависимости и роутеры
- ✅ Создан [dependencies/auth.py](backend/app/dependencies/auth.py) - get_current_user, get_current_team_id
- ✅ Создан [routers/auth.py](backend/app/routers/auth.py) - /login, /me, /logout

### Миграции БД
- ✅ Создана [миграция](backend/alembic/versions/aaecafab3c0c_add_authentication.py) - teams, users, team_id в participants/meetings

---

## ⏳ Осталось сделать (Backend - 40%)

### 1. Обновить models/__init__.py
Добавить импорты Team и User:
```python
from app.models.team import Team
from app.models.user import User
```

### 2. Обновить schemas/__init__.py
Добавить импорты team и user.

### 3. Зарегистрировать роутер auth в [main.py](backend/app/main.py)
```python
from app.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
```

### 4. Обновить роутер participants.py
Добавить во все эндпоинты:
```python
from app.dependencies.auth import get_current_team_id
team_id: int = Depends(get_current_team_id)
```
Фильтровать запросы: `.where(Participant.team_id == team_id)`

### 5. Обновить роутер meetings.py
Аналогично participants.py - добавить фильтрацию по team_id

### 6. Обновить роутер assignments.py
Добавить проверку принадлежности к команде

### 7. Создать скрипт миграции данных
**Файл:** `backend/migrate_existing_data.py`
- Создать дефолтную команду
- Назначить всех participants в эту команду
- Назначить все meetings в эту команду

### 8. Создать скрипт тестовых данных
**Файл:** `backend/seed_auth_data.py` (см. ниже)

### 9. Выполнить миграцию БД
```bash
cd backend
uv run alembic upgrade head
uv run python migrate_existing_data.py
uv run python seed_auth_data.py
```

---

## ⏳ Осталось сделать (Frontend - 100%)

### 1. Создать модуль API авторизации
**Файл:** `frontend/src/api/auth.ts`
- Интерфейсы: LoginCredentials, User, LoginResponse
- authAPI.login(), getCurrentUser(), logout()

### 2. Обновить клиент Axios
**Файл:** `frontend/src/api/client.ts`
- Request interceptor: добавлять Authorization header
- Response interceptor: при 401 очищать localStorage и redirect на /login

### 3. Создать контекст авторизации
**Файл:** `frontend/src/contexts/AuthContext.tsx`
- State: user, isLoading, isAuthenticated
- Methods: login(), logout()
- useAuth() hook

### 4. Создать компонент ProtectedRoute
**Файл:** `frontend/src/components/ProtectedRoute.tsx`
- Проверка isAuthenticated
- Redirect на /login если не авторизован

### 5. Создать страницу входа
**Файлы:**
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.css`

### 6. Обновить App.tsx
- Обернуть в AuthProvider
- Добавить /login route
- Обернуть существующие роуты в ProtectedRoute
- Добавить навбар с user info и logout

---

## 📝 Готовые скрипты для копирования

### seed_auth_data.py

```python
"""Скрипт для создания тестовых данных авторизации."""

import asyncio
from sqlalchemy import select, update
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
```

### migrate_existing_data.py

```python
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
```

---

## 🚀 Порядок запуска

```bash
# 1. Установить зависимости
cd backend
uv sync

# 2. Выполнить миграцию БД
uv run alembic upgrade head

# 3. Мигрировать существующие данные
uv run python migrate_existing_data.py

# 4. Создать тестовые данные
uv run python seed_auth_data.py

# 5. Запустить сервер
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 Следующие шаги

1. Завершить обновление роутеров (participants, meetings, assignments)
2. Реализовать frontend (7 файлов)
3. Протестировать систему авторизации
4. Проверить изоляцию данных между командами
