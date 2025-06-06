# sil-backend

A Django + Celery backend for Savannah Informatics’ take-home assessment.

Features
--------
- OIDC Auth (Keycloak)
- Category/Product hierarchy (django-mptt)
- Category average-price endpoint
- Order placement → SMS (Africa’s Talking) + admin email
- PostgreSQL, RabbitMQ, Keycloak via Helm charts
- pytest suite (>90% coverage)
- CI: GitHub Actions (Compose tests, GHCR build/push)
- CD: GitHub Actions → Helm → OpenShift

Table of Contents
-----------------
1. [Prerequisites](#prerequisites)  
2. [Local Development](#local-development)  
3. [Docker-Compose Stack](#docker-compose-stack)  
4. [API Usage Examples](#api-usage-examples)  
5. [Running Tests & CI](#running-tests-ci)  
6. [Publish Docker Image](#publish-docker-image)  
7. [Helm Charts](#helm-charts)  
8. [OpenShift Deployment](#openshift-deployment)  
9. [Troubleshooting](#troubleshooting)  
10. [License](#license)

Prerequisites
-------------
- Git  
- Docker & Docker-Compose  
- Python 3.12 & Poetry (for linting locally)  
- `oc` CLI + access to OpenShift project  
- Helm 3  
- GitHub repo with GHCR enabled  
- GitHub Secrets:
 - `SECRET_KEY`, `DATABASE_URL`, `RABBITMQ_URL`  
 - OIDC: `OIDC_OP_ISSUER`, `OIDC_RP_CLIENT_ID`, `OIDC_RP_CLIENT_SECRET`  
 - SMS/Email: `AFRICAS_TALKING_USERNAME`, `AFRICAS_TALKING_API_KEY`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `ADMIN_EMAIL`  
 - OpenShift: `OPENSHIFT_SERVER`, `OPENSHIFT_TOKEN`

Local Development
-----------------
1. Clone & install
  ```bash
  git clone https://github.com/danWinga/sil-backend.git
  cd sil-backend
  poetry install
  cp .env.example .env   # fill in values
Start services
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
Visit:
API: http://localhost:8000/api/
Keycloak: http://localhost:8080
Example: List categories
curl -u admin:pass http://localhost:8000/api/categories/
Docker-Compose Stack
The compose file defines:
postgres:15
rabbitmq:3-management
keycloak:21.1.2
web (Django)
worker (Celery)
Start & stop with:
docker compose up -d
docker compose down --volumes
API Usage Examples
Obtain a token from Keycloak:
TOKEN=$(curl -s -X POST http://localhost:8080/realms/si/protocol/openid-connect/token \
 -d "grant_type=password" \
 -d "client_id=si-backend" \
 -d "client_secret=supersecret" \
 -d "username=testuser" \
 -d "password=password" | jq -r .access_token)
Create a category:
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
 -d '{"name":"Electronics","slug":"electronics"}' \
 http://localhost:8000/api/categories/
Bulk-upload products:
curl -X POST -H "Authorization: Bearer $TOKEN" \
 -H "Content-Type: application/json" \
 -d '[{"name":"Phone","description":"Smart","price":"199.99","categories":[1]}]' \
 http://localhost:8000/api/products/
Get average price:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/categories/1/average_price/
Place an order:
curl -X POST -H "Authorization: Bearer $TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"items":[{"product_id":1,"quantity":2}]}' \
 http://localhost:8000/api/orders/
Running Tests & CI
Locally run:
docker compose run --rm web pytest --cov=.
CI job (.github/workflows/ci-docker-compose.yml) will:
Build & start compose services
Run migrations + tests
Tear down services
Publish Docker Image
After tests, CI “publish” job builds and pushes to GHCR:
ghcr.io/<org>/si-backend:latest
ghcr.io/<org>/si-backend:<commit-sha>
Helm Charts
Your charts live under helm/si-backend-api and helm/si-notifications-worker. They accept:
image:
 repository: ghcr.io/<org>/si-backend
 tag: latest
secretName: si-backend-secret
replicaCount: 1
OpenShift Deployment
CD job (deploy-to-openshift.yml) will:
oc login & project select
oc apply secret with runtime env
Run a one-off Job to apply migrations
helm upgrade --install your API & worker
Wait for rollout
Troubleshooting
Cannot resolve “postgres”: ensure DATABASE_URL host matches Helm release service si-postgres-postgresql
Migrations unapplied: check CD “migrate” job logs (oc logs job/migrate-<run_id>)
Worker not connecting: verify RABBITMQ_URL points to si-rabbitmq service
License
MIT

