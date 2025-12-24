# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Role Distribution System** for agile teams that dynamically assigns 7 situational roles (Moderator, Speaker, Time Manager, Critic, Ideologue, Mediator, Harmonizer) to meeting participants based on their biorhythms, emotional intelligence (EI), and social intelligence (SI).

The system uses a deterministic algorithm with two validators:
1. **Load Balance Validator** - prevents role repetition via history-based penalties
2. **Meeting Context Validator** - adapts role priorities based on meeting type

**Tech Stack:**
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Alembic (uv for dependency management)
- Frontend: React 18 + TypeScript + Vite + React Router + Axios

## Common Commands

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
uv run alembic upgrade head           # Apply migrations
uv run alembic downgrade base         # Reset database
uv run alembic revision --autogenerate -m "description"  # Create new migration

# Seed test data
uv run python seed_data.py

# Run tests (if available)
uv run python -m pytest
```

Backend runs at `http://localhost:8000` with API docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend runs at `http://localhost:5173`

### Database Setup

```bash
# Create PostgreSQL database
createdb role_distribution

# Or via psql
psql -U postgres
CREATE DATABASE role_distribution;
\q
```

Configure `backend/.env` with your DATABASE_URL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/role_distribution
CORS_ORIGINS=http://localhost:5173
```

### Docker Setup

Run the application using Docker Compose with an external PostgreSQL database:

```bash
# 1. Ensure PostgreSQL is running on your host machine
# The database must be accessible from Docker containers

# 2. Create .env file in project root (copy from .env.example)
cp .env.example .env

# 3. Edit .env and configure DATABASE_URL
# Use host.docker.internal to connect from containers to host:
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/role_distribution
CORS_ORIGINS=["http://localhost"]

# 4. Also create backend/.env (copy from backend/.env.example)
cp backend/.env.example backend/.env
# Edit backend/.env with the same DATABASE_URL

# 5. Build and start services
docker-compose up -d

# 6. View logs
docker-compose logs -f

# 7. Stop services
docker-compose down
```

After starting with Docker Compose:
- Frontend is available at `http://localhost` (port 80)
- Backend API is available at `http://localhost/api/`
- API docs are available at `http://localhost/docs`

**Important Notes:**
- Database must be running externally (not in Docker Compose)
- Use `host.docker.internal` in DATABASE_URL to access host machine from containers
- On Linux, you may need to use `host.gateway` or the host's IP address instead
- Frontend nginx proxies API requests to backend automatically

**Useful Docker Commands:**
```bash
# Rebuild containers after code changes
docker-compose up -d --build

# View container status
docker-compose ps

# Execute commands in backend container
docker-compose exec backend uv run alembic upgrade head
docker-compose exec backend uv run python seed_data.py

# Remove containers and volumes
docker-compose down -v
```

## Architecture Overview

### Core Algorithm Flow

The role assignment algorithm is implemented in `backend/app/services/` and follows this pipeline:

1. **Energy Calculation** ([energy_calculator.py](backend/app/services/energy_calculator.py)):
   - Calculates participant energy level at meeting time based on chronotype and peak hours
   - Determines if participant is in their active period

2. **Base Fitness Scoring** ([role_matcher.py](backend/app/services/role_matcher.py)):
   - Evaluates how well participant's EI, SI, and energy match each role's requirements
   - Each role has defined min/max ranges for these parameters (see [constants/roles.py](backend/app/constants/roles.py))

3. **Validator 1 - History Penalty** ([assignment_engine.py](backend/app/services/assignment_engine.py)):
   - Queries participant's recent role assignments
   - Applies penalties: 2 consecutive = -40%, 3 = -70%, 4+ = exclude
   - Prevents role burnout and promotes rotation

4. **Validator 2 - Meeting Context** ([constants/meeting_types.py](backend/app/constants/meeting_types.py)):
   - Applies multipliers (0.5-1.5x) based on meeting type
   - E.g., Brainstorm meetings boost Moderator (1.5x) and Ideologue (1.5x)

5. **Greedy Assignment** ([assignment_engine.py](backend/app/services/assignment_engine.py)):
   - Sorts all (participant, role) pairs by final fitness score
   - Iteratively assigns highest-scoring pairs
   - Ensures determinism via alphabetical tie-breaking by participant name
   - Each participant gets max 1 role, each role assigned once

### Database Schema

Three main tables (see [alembic/versions/001_initial_schema.py](backend/alembic/versions/001_initial_schema.py)):

- **participants**: Stores participant data (name, email, chronotype, peak_hours, ei_score, si_score)
- **meetings**: Meeting info (title, meeting_type, scheduled_time) with many-to-many relationship to participants
- **role_assignments**: Results of algorithm (participant_id, meeting_id, role, fitness_score, created_at)

The many-to-many relationship between meetings and participants uses `meeting_participants` association table.

### API Structure

Backend follows a layered architecture:

- **[routers/](backend/app/routers/)**: FastAPI route handlers (participants.py, meetings.py, assignments.py)
- **[schemas/](backend/app/schemas/)**: Pydantic models for request/response validation
- **[models/](backend/app/models/)**: SQLAlchemy ORM models
- **[services/](backend/app/services/)**: Business logic and algorithm implementation
- **[constants/](backend/app/constants/)**: Role requirements and meeting type multipliers (derived from tech spec)

Key endpoint: `POST /api/meetings/{id}/assign-roles` triggers the algorithm

### Frontend Architecture

- **[api/](frontend/src/api/)**: Axios client and API layer
  - [client.ts](frontend/src/api/client.ts): Axios instance
  - [types.ts](frontend/src/api/types.ts): TypeScript interfaces
  - [participants.ts](frontend/src/api/participants.ts), [meetings.ts](frontend/src/api/meetings.ts): API methods

- **[pages/](frontend/src/pages/)**: React pages
  - [ParticipantsPage.tsx](frontend/src/pages/ParticipantsPage.tsx): CRUD for participants
  - [MeetingsPage.tsx](frontend/src/pages/MeetingsPage.tsx): List meetings
  - [CreateMeetingPage.tsx](frontend/src/pages/CreateMeetingPage.tsx): Create meeting form
  - [MeetingDetailPage.tsx](frontend/src/pages/MeetingDetailPage.tsx): View meeting, trigger role assignment, display results

- [vite.config.ts](frontend/vite.config.ts): Proxies `/api/*` to `http://localhost:8000`

### Role Requirements Reference

All 7 roles are defined in [constants/roles.py](backend/app/constants/roles.py) with EI/SI/energy ranges:

- **moderator**: High EI (75-100), high SI (75-100), high energy (70-100)
- **speaker**: Moderate EI (60-85), high SI (75-100), very high energy (80-100)
- **time_manager**: Moderate EI (50-75), low SI (30-60), moderate energy (60-90)
- **critic**: Moderate EI (60-85), moderate SI (50-75), low energy (40-70)
- **ideologue**: Moderate EI (50-75), moderate-high SI (60-85), high energy (75-100)
- **mediator**: Very high EI (80-100), high SI (70-95), moderate-high energy (65-90)
- **harmonizer**: High EI (70-95), high SI (75-100), moderate energy (60-85)

### Meeting Types

Four meeting types in [constants/meeting_types.py](backend/app/constants/meeting_types.py):
- **brainstorm**: Boosts moderator, ideologue
- **review**: Boosts critic, harmonizer
- **planning**: Boosts time_manager, ideologue
- **status_update**: Boosts speaker, time_manager

## Development Notes

### When Working on the Algorithm

The core algorithm logic is in [services/assignment_engine.py](backend/app/services/assignment_engine.py). Key considerations:

- Algorithm must remain **deterministic** - same inputs always produce same outputs
- Tie-breaking uses alphabetical sorting by participant name
- If modifying fitness calculation, ensure it respects the two-validator architecture
- Test with `seed_data.py` which creates 10 participants with diverse profiles and 3 meetings

### When Modifying Database Schema

1. Update SQLAlchemy models in [models/](backend/app/models/)
2. Create migration: `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Apply: `uv run alembic upgrade head`
5. Update Pydantic schemas in [schemas/](backend/app/schemas/) if needed

### When Adding New API Endpoints

Follow existing pattern:
1. Add route handler in [routers/](backend/app/routers/)
2. Create request/response schemas in [schemas/](backend/app/schemas/)
3. Implement business logic in [services/](backend/app/services/) if complex
4. Register router in [main.py](backend/app/main.py)
5. Add corresponding API call in frontend [api/](frontend/src/api/)

### Working with uv (Python Package Manager)

- `uv sync`: Install dependencies from `pyproject.toml` and create/update virtual environment
- `uv add <package>`: Add new dependency
- `uv run <command>`: Run command in virtual environment
- Virtual environment is in `backend/.venv/`

### Environment Configuration

Backend uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for config management:
- Settings defined in [config.py](backend/app/config.py)
- Environment variables loaded from `.env`
- Required vars: `DATABASE_URL`, `CORS_ORIGINS`

## Testing the System

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open `http://localhost:5173`
4. Navigate to Participants page to view seeded data
5. Go to Meetings, open any meeting
6. Click "Assign Roles" to run algorithm
7. View fitness scores and role assignments

The algorithm can be re-run multiple times - it will delete previous assignments and recalculate (with history penalty increasing if same roles are repeated).

## References

- [README.md](README.md): Full project overview
- [QUICKSTART.md](QUICKSTART.md): Step-by-step setup guide
- [tech_task.md](tech_task.md): Original technical specification (in Russian)
- [backend/README.md](backend/README.md): Backend API documentation
- [frontend/README.md](frontend/README.md): Frontend documentation
