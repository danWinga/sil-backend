
Savannah Informatics – SIL Backend Engineer Assessment
Project Structure & Technologies
Python 3.12, Django 5.2, Django REST Framework
Celery for background tasks
PostgreSQL, RabbitMQ, Keycloak (OpenID Connect)
Containerization: Docker & Docker Compose
Orchestration: Kubernetes on OpenShift via Helm
CI/CD: GitHub Actions, GHCR
2. Local Setup

a) Clone and install:
git clone https://github.com/danWinga/sil-backend.git
cd sil-backend
poetry install

b) Configure environment:
cp .env.example .env

edit .env with your localhost values
c) Start services:
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

d) Test API:
curl -u admin:pass http://localhost:8000/api/categories/

3. Docker Compose Stack

postgres:15 → DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
rabbitmq:3-management → RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
keycloak:21.1.2 for OIDC
web: Django application
worker: Celery background service
Manage:
docker compose up -d
docker compose down --volumes

4. CI Pipeline (GitHub Actions)

ci-docker-compose.yml: builds images, spins up services, runs migrations, pytest.
build-and-push: logs into GHCR, pushes si-backend:latest + :sha.
5. Helm Charts

helm/si-backend-api → deploys web, uses secret si-backend-secret.
helm/si-notifications-worker → deploys worker, same secret.
Values: image.repository: ghcr.io/<org>/si-backend image.tag: latest secretName: si-backend-secret
6. OpenShift Deployment

a) Login & project:
oc login <API_URL> --token=<TOKEN>
oc new-project danwinga-dev

b) Install infra via Helm:
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install si-postgres bitnami/postgresql --set global.postgresql.auth.postgresPassword=postgres
helm install si-rabbitmq bitnami/rabbitmq --set auth.username=guest,auth.password=guest

c) Create Secret:
oc create secret generic si-backend-secret --from-literal=...

d) CD Job will:

Apply the secret
Run migrations via one-off Job
Helm upgrade API & worker
Wait for rollouts
e) Verify:
oc get pods,svc,route -n danwinga-dev
curl http://<route-host>/api/products/

7. Additional Notes

Keycloak runs persistent; you can manage it separately or via Helm chart.
For production, replace Django dev server with Gunicorn/Uvicorn behind a LoadBalancer.
Add resource limits, HPA, readiness/liveness probes as needed.

You can paste the above plain text into a Word document, adjust formatting (headers, bullet styles), and save as `deployment-guide.docx`. Then commit both:

```bash
git add README.md deployment-guide.docx
git commit -m "docs: add README and Word deployment guide"
git push