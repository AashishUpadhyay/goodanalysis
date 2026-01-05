# Docker Setup

This project is fully dockerized with separate containers for the frontend and backend.

## Quick Start

### Using Makefile (Recommended)

```bash
# Build and start all services
make build
make up

# View logs
make logs

# Stop services
make down

# Clean up
make clean
```

### Using Docker Compose Directly

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Services

### Frontend (UI)

- **Port**: 3000
- **URL**: http://localhost:3000
- **Build**: Multi-stage build with Node.js and Nginx
- **Environment**: `REACT_APP_API_URL` set to backend API

### Backend (API)

- **Port**: 5000
- **URL**: http://localhost:5000/api
- **Build**: Python 3.12 with uv package manager
- **Health Check**: http://localhost:5000/api/health

## Makefile Commands

- `make build` - Build all Docker images
- `make up` - Start all services in detached mode
- `make down` - Stop all services
- `make logs` - Follow logs from all services
- `make ps` - Show running containers
- `make restart` - Restart all services
- `make rebuild` - Clean, build, and start
- `make rebuild-backend` - Rebuild only backend
- `make rebuild-frontend` - Rebuild only frontend
- `make rebuild-backend-clean` - Rebuild backend without cache
- `make rebuild-frontend-clean` - Rebuild frontend without cache
- `make clean` - Remove local images
- `make clean-all` - Remove all images and volumes

## Volumes

Data is persisted in `.tmp/` directory:

- `.tmp/app/chroma_db` - Vector database
- `.tmp/app/logs` - Application logs

## Environment Variables

### Backend

- `ENV` - Environment (dev/prod)
- `VERSION` - Application version

### Frontend

- `REACT_APP_API_URL` - Backend API URL (set automatically in docker-compose)

## Development

For local development without Docker:

- Backend: `uv run python -m goodanalysis.main api`
- Frontend: `cd frontend && npm start`

## Troubleshooting

### Port conflicts

If ports 3000 or 5000 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - '3001:80' # Change frontend port
  - '5001:5000' # Change backend port
```

### Rebuild after dependency changes

```bash
make rebuild-backend-clean  # After Python dependency changes
make rebuild-frontend-clean  # After npm dependency changes
```

### View container logs

```bash
docker-compose logs goodanalysis-api
docker-compose logs ui
```

### Access container shell

```bash
docker-compose exec goodanalysis-api bash
docker-compose exec ui sh
```
