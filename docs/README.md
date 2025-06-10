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


CI/CD Pipeline Documentation for si-backend
Overview
This GitHub Actions CI workflow automates testing, documentation generation, containerization, and deployment for the si-backend project using Docker Compose and GitHub Pages. It runs on every push or pull request to the main branch.

Workflow Name
CI via Docker Compose & GitHub Pages

Triggers
The workflow runs on:

Pushes to the main branch

Pull requests targeting the main branch

Permissions
The workflow requires:

contents: read: to checkout the repository

pages: write: to publish API documentation

id-token: write: for GitHub Pages deployment authentication

Environment Variable
IMAGE_NAME: Set as si-backend — used during Docker image build and push

Jobs Summary
1. test-and-docs
Runs tests, sets up services (PostgreSQL and RabbitMQ), and generates static API documentation.

Steps:
Checkout code – Clones the repository.

Set up Node.js – Required for possible frontend tasks (even if not used directly here).

Create .env file – Injects necessary secrets from GitHub into a temporary .env file.

Build & Start Services – Uses Docker Compose to start postgres and rabbitmq.

Wait for Services – Checks readiness of PostgreSQL and RabbitMQ.

Run Tests:

Applies Django migrations

Runs pytest with coverage

Tear Down Services – Shuts down Docker containers and removes volumes.

Generate API Documentation:

openapi.json generated via drf-spectacular

docs/index.html: Renders Redoc UI

docs/swagger.html: Renders Swagger UI

Upload Docs – Uploads generated docs to be deployed via GitHub Pages.

2. deploy-pages
Publishes the documentation built in the test-and-docs job to GitHub Pages.

Requirements:
Waits for test-and-docs job to complete

Uses actions/deploy-pages to publish files under the /docs directory

3. publish
Builds and publishes a Docker image of the backend service to GitHub Container Registry (GHCR).

Steps:
Checkout Code

Set up Docker Buildx – Ensures advanced build features

Log in to GHCR – Uses GitHub-provided credentials to push image

Normalize Owner Name – Converts GitHub owner to lowercase (GHCR requirement)

Build & Push Image:

Builds Docker image using Dockerfile

Pushes two tags:

latest

Commit SHA-specific tag (for traceability)

Outputs
✅ Tests Passed: Ensures code is functional before deployment

📄 API Docs: Available via GitHub Pages (docs/index.html for ReDoc, docs/swagger.html for Swagger)

🐳 Docker Image: Pushed to GitHub Container Registry (GHCR)

Troubleshooting
Secrets not found: Ensure all required secrets are set in the repository settings

Postgres/RabbitMQ startup delays: Increase wait times if readiness checks fail

Docker push errors: Verify permissions and token scopes

Adding New Secrets
Go to Repository > Settings > Secrets and variables > Actions, and add any missing secret keys mentioned in the .env creation step.



CD Pipeline Documentation — Deploy to OpenShift via Helm
Overview
This GitHub Actions workflow automates continuous deployment of the si-backend application to an OpenShift cluster using Helm charts. It securely manages secrets, updates Kubernetes deployments, and ensures a successful rollout of the API and worker components.

Workflow Name
CD → OpenShift via Helm

Triggers
This workflow runs on:

Pushes to the main branch (automated CD)

Manual trigger via workflow_dispatch (on-demand deployment)

Required Permissions
contents: read: to checkout source code

id-token: write: to support authenticated actions (if needed for OpenShift integration)

Environment Configuration
Variable	Description
PROJECT	OpenShift project name (e.g. danwinga-dev)
NAMESPACE	Kubernetes namespace to deploy into
SECRET_NAME	Kubernetes secret containing app config
CHART_API	Helm chart path for the backend API
CHART_WORKER	Helm chart path for the worker
IMAGE_REPO	Docker image repository (e.g. GHCR)
IMAGE_TAG	Docker image tag to deploy (e.g. latest)

Job: deploy
Runs on:
ubuntu-latest GitHub-hosted runner

Workflow Steps
1. Checkout Code
Retrieves the latest code from the main branch.

2. Install OpenShift CLI (oc)
Downloads and installs the OpenShift CLI tool required for interacting with the cluster.

3. Login to OpenShift
Authenticates with the OpenShift cluster using credentials stored in secrets:

OPENSHIFT_SERVER

OPENSHIFT_TOKEN

4. Create or Update Kubernetes Secret
Dynamically creates/updates a Secret in Kubernetes that contains sensitive environment values like:

Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.)

Database & broker URLs

Keycloak OIDC details

SMS/Email credentials

🔐 These values are securely injected using GitHub Secrets.

5. Set Up Helm
Installs Helm v3.12.0 to manage Kubernetes applications.

6. Add Bitnami Chart Repo
Adds Bitnami's Helm repository for any dependent charts (e.g., PostgreSQL, RabbitMQ).

7. Deploy or Upgrade API Service
Uses Helm to install or upgrade the si-api deployment with the specified:

Image repository and tag

Kubernetes secret name

8. Deploy or Upgrade Worker Service
Uses Helm to install or upgrade the si-worker deployment with the same configuration.

9. Wait for Successful Rollouts
Uses oc rollout status to confirm that both si-api and si-worker deployments succeed without timeouts.

Outcomes
🚀 Automatic deployment of backend API and worker services to OpenShift.

🔄 Helm-based deployment ensures configuration is versioned and declarative.

🔐 Secrets are centrally managed and securely injected.

✅ Rollout validation ensures only successful deployments complete the job.

Requirements
Before this workflow runs successfully:

Secrets must be defined in GitHub Repository > Settings > Secrets:

OPENSHIFT_SERVER

OPENSHIFT_TOKEN

SECRET_KEY, EMAIL_*, AFRICAS_TALKING_*, etc.

Kubernetes objects (like the namespace and service accounts) must already exist or be managed elsewhere.

Helm charts helm/si-backend-api and helm/si-notifications-worker must be correctly defined and maintained.

Troubleshooting Tips
Issue	Solution
oc login fails	Verify OPENSHIFT_SERVER and OPENSHIFT_TOKEN secrets
Helm chart error	Check the chart’s structure and required values
Rollout timeout	Review Pod logs and check OpenShift console for deployment errors
Secrets not updated	Ensure values in GitHub Secrets are correct and match what's used in the .yaml

Manual Deployment
You can manually trigger this workflow from the GitHub Actions tab using the “Run workflow” button (thanks to workflow_dispatch support).
