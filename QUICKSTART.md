# Quick Start Guide

Быстрое руководство по запуску проекта Role Distribution System.

## Шаг 1: Подготовка окружения

### Установите необходимые инструменты:

```bash
# Python 3.11+
python --version

# uv (менеджер зависимостей Python)
pip install uv

# Node.js 18+
node --version
npm --version

# PostgreSQL 15+
postgres --version
```

## Шаг 2: Настройка базы данных

```bash
# Создайте базу данных PostgreSQL
createdb role_distribution

# Или через psql:
psql -U postgres
CREATE DATABASE role_distribution;
\q
```

## Шаг 3: Backend

```bash
cd backend

# Установка зависимостей
uv sync

# Настройка .env
cp .env.example .env

# Откройте .env и укажите правильный DATABASE_URL:
# DATABASE_URL=postgresql://your_user:your_password@localhost:5432/role_distribution

# Примените миграции
uv run alembic upgrade head

# Заполните тестовыми данными
uv run python seed_data.py

# Запустите сервер
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend запущен на `http://localhost:8000`
API документация: `http://localhost:8000/docs`

## Шаг 4: Frontend

Откройте новый терминал:

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

Frontend запущен на `http://localhost:5173`

## Шаг 5: Тестирование

1. Откройте браузер: `http://localhost:5173`

2. **Просмотр участников**:
   - Перейдите в "Participants"
   - Увидите 10 тестовых участников

3. **Создание встречи** (опционально):
   - Нажмите "New Meeting"
   - Заполните форму
   - Выберите участников
   - Создайте встречу

4. **Назначение ролей**:
   - Перейдите в "Meetings"
   - Откройте любую встречу
   - Нажмите "Assign Roles"
   - Просмотрите результаты!

## Возможные проблемы

### Backend не запускается

```bash
# Проверьте подключение к БД
psql -d role_distribution -U your_user

# Проверьте DATABASE_URL в .env
cat backend/.env
```

### Frontend не подключается к API

```bash
# Убедитесь, что backend запущен на порту 8000
curl http://localhost:8000/

# Проверьте vite.config.ts proxy настройки
```

### Ошибка миграций

```bash
# Пересоздайте БД
dropdb role_distribution
createdb role_distribution
cd backend
uv run alembic upgrade head
```

## Полезные команды

### Backend

```bash
# Проверка кода
uv run python -m pytest  # (если есть тесты)

# Пересоздание БД
uv run alembic downgrade base
uv run alembic upgrade head
uv run python seed_data.py
```

### Frontend

```bash
# Build для production
npm run build

# Preview production build
npm run preview
```

## Структура тестовых данных

После `seed_data.py` в БД будет:

- **10 участников** с разными профилями:
  - Alice, Carol, Grace, Jack - утренний хронотип (высокий EI/SI)
  - Bob, Eva, Henry - вечерний хронотип (средний/низкий EI/SI)
  - David, Frank, Iris - промежуточный хронотип (разные EI/SI)

- **3 встречи**:
  - Weekly Brainstorm (завтра в 10:00, 8 участников)
  - Sprint Retrospective (послезавтра в 15:00, 8 участников)
  - Sprint Planning (через 3 дня в 9:00, все 10 участников)

## Следующие шаги

Прочитайте подробную документацию:
- [README.md](README.md) - обзор проекта
- [backend/README.md](backend/README.md) - backend API
- [frontend/README.md](frontend/README.md) - frontend UI
- [tech_task.md](tech_task.md) - техническое задание

Готово! Проект запущен и работает 🎉
