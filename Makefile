.PHONY: build up down clean clean-all logs ps restart rebuild rebuild-backend rebuild-frontend rebuild-backend-clean rebuild-frontend-clean

# Build and run commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

# Logging and status
logs:
	docker-compose logs -f

ps:
	docker-compose ps

# Cleaning commands
clean:
	docker-compose down --rmi local

clean-all:
	docker-compose down --rmi all
	docker system prune -af --volumes

# Helper commands
restart: down up

rebuild: clean build up

# Individual service rebuilds
rebuild-backend:
	docker compose build goodanalysis-api && docker compose up -d goodanalysis-api

rebuild-backend-clean:
	docker compose build --no-cache goodanalysis-api && docker compose up -d goodanalysis-api

rebuild-frontend:
	docker compose build ui && docker compose up -d ui

rebuild-frontend-clean:
	docker compose build --no-cache ui && docker compose up -d ui

