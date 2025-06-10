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



SI-Backend OpenShift Deployment & CI/CD User Guide
This guide walks you step-by-step through:

• Prerequisites
• OpenShift setup (PostgreSQL, RabbitMQ, Keycloak, Secrets)
• GitHub Actions CI/CD pipeline for SI-API and SI-Worker
• Triggering migrations and deployments

All “secret” values shown here are dummy placeholders—replace them with your real credentials!

Prerequisites
• An OpenShift cluster and CLI (oc) configured
• Helm 3 installed
• A GitHub repository with your SI-Backend code and the provided workflows
• kubectl / oc authenticated (token or kubeconfig)
• A DNS (or OpenShift Routes) pointing at your services

2. OpenShift Project & Login

Log in to your cluster and switch to your project (namespace):

oc login https://api.rm3.7wse.p1.openshiftapps.com:6443 \
  --token=sha256~DUMMY_OPENSHIFT_TOKEN
oc new-project danwinga-dev || oc project danwinga-dev
3. Add the Bitnami Helm Repo

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
4. Deploy PostgreSQL

helm upgrade --install si-postgres bitnami/postgresql \
  --namespace danwinga-dev \
  --set global.postgresql.auth.postgresPassword=postgres123 \
  --set global.postgresql.auth.username=postgres_user \
  --set global.postgresql.auth.database=si_db
This will create a StatefulSet si-postgres-postgresql with:

• Username: postgres_user
• Password: postgres123
• Database: si_db

5. Deploy RabbitMQ

helm upgrade --install si-rabbitmq bitnami/rabbitmq \
  --namespace danwinga-dev \
  --set auth.username=guest_user \
  --set auth.password=guest_pass
RabbitMQ will be available at the Kubernetes service si-rabbitmq.

6. Create SI-Backend Secrets

All runtime‐config environment variables live in a single OpenShift Secret named si-backend-secret.  Here's an example with dummy values:

oc create secret generic si-backend-secret \
  --namespace=danwinga-dev \
  --from-literal=SECRET_KEY='CHANGE_ME_TO_A_RANDOM_SECRET' \
  --from-literal=DEBUG='False' \
  --from-literal=ALLOWED_HOSTS='si-api.apps.example.com,si-keycloak.apps.example.com' \
  --from-literal=CSRF_TRUSTED_ORIGINS='https://si-api.apps.example.com,https://si-keycloak.apps.example.com' \
  --from-literal=DATABASE_URL='postgres://postgres_user:postgres123@si-postgres-postgresql:5432/si_db' \
  --from-literal=RABBITMQ_URL='amqp://guest_user:guest_pass@si-rabbitmq:5672/' \
  --from-literal=BROKER_URL='amqp://guest_user:guest_pass@si-rabbitmq:5672/' \
  --from-literal=CELERY_BROKER_URL='amqp://guest_user:guest_pass@si-rabbitmq:5672/' \
  --from-literal=OIDC_OP_ISSUER='https://si-keycloak.apps.example.com/realms/si' \
  --from-literal=OIDC_RP_CLIENT_ID='si-backend' \
  --from-literal=OIDC_RP_CLIENT_SECRET='SUPER_SECRET_CLIENT_SECRET' \
  --from-literal=AFRICAS_TALKING_USERNAME='sandbox_user' \
  --from-literal=AFRICAS_TALKING_API_KEY='atsk_dummyapikey1234567890' \
  --from-literal=EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend' \
  --from-literal=EMAIL_HOST='smtp.gmail.com' \
  --from-literal=EMAIL_PORT='587' \
  --from-literal=EMAIL_USE_TLS='True' \
  --from-literal=EMAIL_HOST_USER='you@example.com' \
  --from-literal=EMAIL_HOST_PASSWORD='EMAIL_PASSWORD_HERE' \
  --from-literal=DEFAULT_FROM_EMAIL='noreply@example.com' \
  --from-literal=ADMIN_EMAIL='admin@example.com'
7. Deploy Keycloak (Optional)

Your repository contains an OpenShift YAML at openshift/keycloak-defaultdb.yaml.  To deploy Keycloak using the built-in H2 DB:

oc apply -f openshift/keycloak-defaultdb.yaml
Once Keycloak is up, create a realm si and a client si-backend with your desired roles and client secret.

8. CI/CD in GitHub Actions

Your .github/workflows/ci-docker-compose.yaml does the following:

Checks out code, sets up Node.js
Builds your Docker Compose stack (Postgres, RabbitMQ, Keycloak if configured)
Runs migrations & test suite (pytest) in the web service
Generates docs/openapi.json via python manage.py spectacular
Creates two static HTML files in docs/ – • index.html (ReDoc) • swagger.html (Swagger-UI)
Uploads docs/ to GitHub Pages using upload-pages-artifact & deploy-pages actions
Separately builds & pushes your container image to GitHub Container Registry
Secrets to configure in GitHub repo settings (under Settings → Secrets & variables → Actions):

• SECRET_KEY
• DATABASE_URL
• RABBITMQ_URL
• OIDC_OP_ISSUER, OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET
• AFRICAS_TALKING_USERNAME, AFRICAS_TALKING_API_KEY
• EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, etc.

Once those are set, every push to main will:

Run your tests
Regenerate API docs
Publish them to: https://<your-org>.github.io/<your-repo>/index.html https://<your-org>.github.io/<your-repo>/swagger.html
Build & push Docker images
9. Triggering a Deployment

After you have:

• Deployed your infra (Postgres, RabbitMQ, Keycloak)
• Created si-backend-secret
• Configured GitHub secrets

Simply push your code to main:

git add .
git commit -m "feat: ready for OpenShift deploy"
git push origin main
GitHub Actions will automatically:

Run tests
Publish API docs to GitHub Pages
Build & push your SI-Backend image
You can then deploy your SI-Backend & SI-Worker to OpenShift via your own Deployment YAMLs (not covered here), using the image tags published to GHCR.

10. Verifying

• API Docs (ReDoc):
https://<your-org>.github.io/<your-repo>/index.html

• API Docs (Swagger-UI):
https://<your-org>.github.io/<your-repo>/swagger.html

• Raw OpenAPI JSON:
https://<your-org>.github.io/<your-repo>/openapi.json

• Container Images:
ghcr.io/<your-org>/si-backend:latest
ghcr.io/<your-org>/si-backend:<git-sha>

• OpenShift services:
– Postgres at si-postgres-postgresql.danwinga-dev.svc.cluster.local
– RabbitMQ at si-rabbitmq.danwinga-dev.svc.cluster.local
– Keycloak at your Route URL

SI-Backend API Testing Guide
This document walks you through obtaining an OAuth2 token from Keycloak and exercising the SI-Backend REST API endpoints (Categories, Products, Orders) via curl. Replace placeholder values with your real URLs, client credentials, and tokens.

Prerequisites
• Keycloak realm si is running and reachable at https://si-keycloak-…/realms/si
• A client in that realm with ID si-backend and a client secret
• A test user (testuser / password) exists in the si realm
• The SI-Backend API is deployed at https://si-api-…/api/
• curl is installed on your workstation

Set the following environment variables (example):

export KEYCLOAK_URL="https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com"
export API_URL="https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/api"
export CLIENT_ID="si-backend"
export CLIENT_SECRET="supersecret"
export USERNAME="testuser"
export PASSWORD="password"
1. Obtain an Access Token
Use the Resource Owner Password grant to get a bearer token:

curl -s -X POST "$KEYCLOAK_URL/realms/si/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "grant_type=password" \
  -d "username=$USERNAME" \
  -d "password=$PASSWORD" \
  | jq -r .access_token \
  > access_token.txt
• The token will be saved in access_token.txt.
• You can verify it:

TOKEN=$(cat access_token.txt)
echo "Bearer $TOKEN"
2. Categories Endpoints
2.1 Create a Category
TOKEN=$(cat access_token.txt)

curl -X POST "$API_URL/categories/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":   "Electronics",
    "slug":   "electronics",
    "parent": null
  }'
Response (201 Created):

{
  "id":       1,
  "name":     "Electronics",
  "slug":     "electronics",
  "parent":   null,
  "created":  "...",
  "modified": "..."
}
2.2 List Categories
curl -X GET "$API_URL/categories/" \
  -H "Authorization: Bearer $TOKEN"
Response (200 OK):

[
  {
    "id":     1,
    "name":   "Electronics",
    "slug":   "electronics",
    "parent": null,
    ...
  },
  ...
]
3. Products Endpoints
3.1 Create a Single Product
curl -X POST "$API_URL/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":        "Smartphone X",
    "description": "Latest model smartphone",
    "price":       "699.00",
    "categories":  [1]
  }'
Response (201 Created):

{
  "id":          1,
  "name":        "Smartphone X",
  "description": "Latest model smartphone",
  "price":       "699.00",
  "categories":  [1],
  ...
}
3.2 Bulk Create Products
curl -X POST "$API_URL/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name":        "Tablet Y",
      "description": "10-inch tablet",
      "price":       "299.00",
      "categories":  [1]
    },
    {
      "name":        "Laptop Z",
      "description": "15-inch laptop",
      "price":       "1299.00",
      "categories":  [1]
    }
  ]'
Response (201 Created):

[
  { "id": 2, ... },
  { "id": 3, ... }
]
4. Orders Endpoint
4.1 Create an Order
curl -X POST "$API_URL/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "product_id": 1, "quantity": 2 },
      { "product_id": 2, "quantity": 1 }
    ]
  }'
Response (201 Created):

{
  "id":          1,
  "user":        "testuser",
  "items":       [
      { "product_id": 1, "quantity": 2, "price": "699.00" },
      { "product_id": 2, "quantity": 1, "price": "299.00" }
  ],
  "total_price": "1697.00",
  "status":      "pending",
  ...
}
5. Refreshing Your Token
Access tokens expire (often in 5 minutes). To avoid re-authenticating your password, obtain a refresh token:

curl -s -X POST "$KEYCLOAK_URL/realms/si/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=$(jq -r .refresh_token < access_token.txt)" \
  | jq -r .access_token \
  > access_token.txt
6. Troubleshooting
401 Unauthorized → check your token, client credentials, or user password.
403 Forbidden → ensure testuser has the correct roles in Keycloak.
404 Not Found → verify API_URL and endpoint paths.
400 Bad Request → inspect your JSON payload for missing/invalid fields.

7. Admin Consoles
===============

Beyond exercising the public API, you have two admin UIs:

Keycloak Admin Console
SI-API (Django) Admin
—

Keycloak Admin Console
• URL:
https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/aadmin
• Username: admin
• Password: admin

Use this to manage your si realm, users, roles, clients (e.g. si-backend), etc.

—

2. SI-API (Django) Admin

• URL:
https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/admin/
• Username: user
• Password: password

Use the Django admin to manage Products, Categories, Orders, and other models directly.

Notes
– If you need to create or reset these accounts, log into Keycloak as the admin user and adjust credentials in the si realm or add a Django superuser via the shell in your web container:

docker compose run --rm web python manage.py createsuperuser
– Ensure your ALLOWED_HOSTS and CORS/CSRF settings (in your si-backend-secret) include both the Keycloak and SI-API admin hostnames.







