# Role Distribution Backend

Backend API для системы динамического распределения ролей в agile-командах.

## Технологический стек

- **FastAPI** - современный веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Alembic** - инструмент для миграций БД
- **Pydantic** - валидация данных и настройки
- **uv** - менеджер зависимостей Python

## Установка и запуск

### 1. Установка зависимостей

```bash
cd backend
uv sync
```

### 2. Настройка базы данных

Создайте PostgreSQL базу данных:

```bash
createdb role_distribution
```

Скопируйте `.env.example` в `.env` и настройте подключение к БД:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/role_distribution
CORS_ORIGINS=http://localhost:5173
```

### 3. Применение миграций

```bash
uv run alembic upgrade head
```

### 4. Заполнение тестовыми данными

```bash
uv run python seed_data.py
```

Это создаст 10 тестовых участников и 3 встречи.

### 5. Запуск сервера

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: `http://localhost:8000`

Документация API (Swagger): `http://localhost:8000/docs`

## Структура проекта

```
backend/
├── app/
│   ├── constants/          # Константы из ТЗ (роли, типы встреч)
│   ├── models/             # SQLAlchemy модели
│   ├── schemas/            # Pydantic схемы
│   ├── routers/            # API endpoints
│   ├── services/           # Бизнес-логика алгоритма
│   ├── config.py           # Настройки приложения
│   ├── database.py         # Подключение к БД
│   └── main.py             # Точка входа FastAPI
├── alembic/                # Миграции БД
├── tests/                  # Тесты
├── seed_data.py            # Скрипт для заполнения тестовыми данными
└── pyproject.toml          # Зависимости проекта
```

## API Endpoints

### Participants (Участники)

- `GET /api/participants` - Список всех участников
- `POST /api/participants` - Создать участника
- `GET /api/participants/{id}` - Получить участника
- `PUT /api/participants/{id}` - Обновить участника
- `DELETE /api/participants/{id}` - Удалить участника

### Meetings (Встречи)

- `GET /api/meetings` - Список встреч
- `POST /api/meetings` - Создать встречу
- `GET /api/meetings/{id}` - Получить встречу
- `PUT /api/meetings/{id}` - Обновить встречу
- `DELETE /api/meetings/{id}` - Удалить встречу
- `POST /api/meetings/{id}/participants` - Добавить участников
- `DELETE /api/meetings/{id}/participants/{participant_id}` - Удалить участника

### Role Assignment (Распределение ролей)

- `POST /api/meetings/{id}/assign-roles` - **Запустить алгоритм распределения**
- `GET /api/meetings/{id}/assignments` - Получить результаты

### Assignments (История назначений)

- `GET /api/assignments/participant/{id}/history` - История ролей участника

## Алгоритм распределения ролей

Алгоритм реализован в `app/services/assignment_engine.py` и состоит из:

1. **Расчет энергии** (`energy_calculator.py`) - на основе биоритмов и времени встречи
2. **Базовый fitness** (`role_matcher.py`) - соответствие параметров участника требованиям роли
3. **Валидатор 1** - штраф за повторение ролей
4. **Валидатор 2** - множители по типу встречи
5. **Жадный алгоритм** - назначение ролей с максимальными score

## Тестирование

Пример запроса для назначения ролей:

```bash
curl -X POST http://localhost:8000/api/meetings/1/assign-roles
```

Результат:

```json
{
  "meeting_id": 1,
  "total_assigned": 7,
  "assignments": [
    {
      "participant_name": "Alice Johnson",
      "role": "moderator",
      "fitness_score": 95.5
    },
    ...
  ]
}
```
