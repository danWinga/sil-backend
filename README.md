# si-backend

A Django-based backend service for Savannah Informatics 

## Tech Stack
- Django REST Framework
- PostgreSQL
- RabbitMQ
- OpenID Connect
- Poetry
- Docker & Kubernetes

## Local Quickstart
1. `poetry install`
2. Copy `.env.example` → `.env` and fill in.
3. `docker-compose up -d`
4. `python manage.py migrate`
5. `python manage.py runserver`
