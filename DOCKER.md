# Docker Setup Guide

This guide explains how to run the Role Distribution System using Docker Compose with an external PostgreSQL database.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database running on host machine or accessible network
- Database `role_distribution` created

## Quick Start

1. **Configure environment variables:**

```bash
# Create .env file in project root
cp .env.example .env

# Edit .env with your database credentials
# Use host.docker.internal to connect from Docker to host machine
nano .env
```

Example `.env`:
```
DATABASE_URL=postgresql://user:password@host.docker.internal:5432/role_distribution
CORS_ORIGINS=["http://localhost"]
```

2. **Configure backend environment:**

```bash
# Create backend/.env file
cp backend/.env.example backend/.env

# Edit with same DATABASE_URL
nano backend/.env
```

3. **Start services:**

```bash
docker-compose up -d
```

4. **Access the application:**

- Frontend: http://localhost
- Backend API: http://localhost/api/
- API Documentation: http://localhost/docs

## Architecture

The Docker setup consists of two services:

- **backend**: FastAPI application (port 8000, internal)
- **frontend**: React application served by nginx (port 80)

The frontend nginx acts as a reverse proxy, routing `/api/*` requests to the backend container.

## Database Connection

The database is **external** (not managed by Docker Compose). Containers connect to it using:

- **macOS/Windows**: `host.docker.internal:5432`
- **Linux**: Use host's IP address or configure `host.gateway`

Example connection strings:

```bash
# macOS/Windows
DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/role_distribution

# Linux (option 1: use host IP)
DATABASE_URL=postgresql://postgres:password@192.168.1.100:5432/role_distribution

# Linux (option 2: use docker host gateway)
# Add to docker-compose.yml under backend service:
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Common Commands

### Starting and Stopping

```bash
# Start in detached mode
docker-compose up -d

# Start with logs visible
docker-compose up

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuilding

```bash
# Rebuild after code changes
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

### Running Commands in Containers

```bash
# Run migrations
docker-compose exec backend uv run alembic upgrade head

# Seed test data
docker-compose exec backend uv run python seed_data.py

# Open backend shell
docker-compose exec backend sh

# Check backend health
docker-compose exec backend curl http://localhost:8000/docs
```

### Checking Status

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# Inspect container
docker-compose exec backend env
```

## Troubleshooting

### Database Connection Issues

**Problem**: Backend can't connect to PostgreSQL

**Solutions**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check PostgreSQL accepts connections from Docker:
   - Edit `postgresql.conf`: `listen_addresses = '*'`
   - Edit `pg_hba.conf`: add line `host all all 172.16.0.0/12 md5`
   - Restart PostgreSQL: `sudo systemctl restart postgresql`
3. Test connection from container:
   ```bash
   docker-compose exec backend sh
   apk add postgresql-client
   psql postgresql://user:password@host.docker.internal:5432/role_distribution
   ```

### Port Already in Use

**Problem**: Port 80 or 8000 already in use

**Solution**: Edit `docker-compose.yml` to use different ports:
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change host port to 8080
```

### Frontend Can't Reach Backend

**Problem**: API requests fail with 502 Bad Gateway

**Solutions**:
1. Check backend is running: `docker-compose logs backend`
2. Verify backend health: `curl http://localhost:8000/docs`
3. Check nginx config: `docker-compose exec frontend cat /etc/nginx/conf.d/default.conf`

### Migrations Not Running

**Problem**: Database schema not created

**Solution**: Run migrations manually:
```bash
docker-compose exec backend uv run alembic upgrade head
```

## Development Workflow

1. Make code changes in your editor
2. Rebuild affected service:
   ```bash
   docker-compose up -d --build backend
   # or
   docker-compose up -d --build frontend
   ```
3. Check logs for errors:
   ```bash
   docker-compose logs -f backend
   ```

## Production Considerations

For production deployment:

1. **Use environment-specific .env files**
2. **Enable HTTPS**: Add SSL certificates and configure nginx
3. **Set resource limits** in docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 512M
   ```
4. **Use secrets management**: Don't commit .env files
5. **Configure logging**: Use external log aggregation
6. **Set up monitoring**: Add health checks and metrics
7. **Use external database**: Managed PostgreSQL service recommended

## Cleanup

Remove all containers, networks, and images:

```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```
