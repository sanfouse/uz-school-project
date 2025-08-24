# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a microservices-based system for educational services with web scraping capabilities, deployed on Kubernetes. The system consists of:

- **frontend/** - Streamlit web interface for managing scrapers
- **scrapers-api/** - FastAPI service for managing Kubernetes jobs and scraper lifecycle
- **profi-scraper/** - Web scraper service using Playwright and RabbitMQ
- **teachers-api/** - FastAPI service for managing teachers, lessons, and invoices with PostgreSQL
- **teachers-bot/** - Telegram bot for teacher interactions using aiogram
- **notification-bot/** - Service for sending notifications
- **lesson-checker/** - Service for lesson validation

## Development Commands

### Local Development
```bash
# Start local dependencies (PostgreSQL, RabbitMQ)
docker-compose up -d

# Run individual services locally
cd frontend && poetry install && poetry run streamlit run app.py
cd scrapers-api && poetry install && poetry run python main.py
cd teachers-api && poetry install && poetry run python main.py
cd teachers-bot && poetry install && poetry run python main.py
cd profi-scraper && poetry install && poetry run python main.py
```

### Testing
```bash
# Run tests for profi-scraper (only service with configured tests)
cd profi-scraper && poetry run pytest
```

### Code Formatting
All services use Black for code formatting:
```bash
cd <service-directory> && poetry run black .
```

### Kubernetes Development
```bash
# Development with hot reload
skaffold dev

# Production deployment
skaffold run

# Production with custom values
skaffold run -f skaffold-prod.yaml

# View logs
kubectl logs -l app=frontend -f
kubectl logs -l app=scrapers-api -f

# Delete all resources
skaffold delete
```

### Database Migrations (teachers-api)
```bash
cd teachers-api
# Create migration
poetry run alembic revision --autogenerate -m "description"
# Apply migrations
poetry run alembic upgrade head
```

## Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Frontend**: Streamlit
- **Messaging**: RabbitMQ with FastStream
- **Database**: PostgreSQL, Redis
- **Scraping**: Playwright, BeautifulSoup
- **Bot**: aiogram (Telegram Bot API)
- **Containerization**: Docker, Kubernetes
- **Deployment**: Skaffold, Helm

## Service Communication

Services communicate via:
- **RabbitMQ**: Async messaging between scrapers, bots, and notification services
- **HTTP APIs**: REST endpoints between frontend and APIs
- **Redis**: Caching and job state management
- **PostgreSQL**: Persistent data storage for teachers-api

## Configuration

Each service uses pydantic-settings for configuration management. Environment variables are typically defined in:
- Docker Compose files for local development
- Kubernetes manifests for production
- `.env` files for local overrides

## Deployment Architecture

The system is designed for cloud deployment with:
- **Ingress Controller**: nginx-ingress for external access
- **Container Registry**: Private registry (aadbccd8-cute-cygnus.registry.twcstorage.ru)
- **Kubernetes**: Multi-service deployment with Helm charts
- **Cloud Providers**: Supports GKE, EKS, and AKS

## Development Workflow

1. Use `docker-compose up -d` for local dependencies
2. Develop services individually with poetry
3. Test changes with `skaffold dev` for full integration
4. Format code with `poetry run black .` before committing
5. Use `pytest` for testing where configured

## Quick Access Commands

```bash
# Get external IP for access
kubectl get service -n ingress-nginx ingress-nginx-controller

# Port forward for local access
kubectl port-forward service/frontend 8501:8501

# Monitor resources
kubectl get all
kubectl get pods -w
```