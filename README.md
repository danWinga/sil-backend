# 💼 SI Backend – Django + Celery + OpenShift CI/CD

A **Django-based backend** system built for Savannah Informatics, powered by OpenShift, GitHub Actions, and Keycloak OIDC.

---

## 🔧 Tech Stack
- Django REST Framework
- PostgreSQL
- RabbitMQ + Celery
- Keycloak (OIDC Auth)
- Docker & Kubernetes (OpenShift)
- Poetry
- Helm 3
- GitHub Actions (CI/CD)
- Africastalking API (SMS)

---

## 🚀 Features
- 🔐 OIDC login via Keycloak
- 📦 Category & Product hierarchy (`django-mptt`)
- 🧯 Category average price endpoint
- 🛒 Order placement triggers:
  - SMS (Africastalking)
  - Admin email
- 🧪 >90% pytest coverage
- ⚙️ Full CI pipeline using Docker Compose & GitHub Pages
- 🔄 CD deployment via Helm → OpenShift (with secrets)

---

## 📂 Table of Contents
1. [Local Development](#local-development)
2. [Docker-Compose Stack](#docker-compose-stack)
3. [API Examples](#api-usage-examples)
4. [Testing & CI](#running-tests-ci)
5. [CD with Helm & OpenShift](#openshift-deployment)
6. [Admin Consoles](#admin-consoles)
7. [Deployment URLs](#openshift-deployment-urls)
8. [Production cURL Test](#production-curl-test)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

---

## 💻 Local Development
```bash
git clone https://github.com/danWinga/sil-backend.git
cd sil-backend
poetry install
cp .env.example .env  # fill values
```

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Visit:
- API → [http://localhost:8000/api/](http://localhost:8000/api/)
- Keycloak → [http://localhost:8080](http://localhost:8080)

---

## 🐳 Docker-Compose Stack
- PostgreSQL 15
- RabbitMQ 3-management
- Keycloak 21
- Django Web
- Celery Worker

Start stack:
```bash
docker compose up -d
docker compose down --volumes
```

---

## 🧪 API Usage Examples
### Get Token
```bash
curl -X POST "https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/realms/si/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=si-backend" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=password" \
  -d "username=testuser" \
  -d "password=YOUR_PASSWORD" \
  | jq -r .access_token > access_token.txt
```

### Create Product (Production)
```bash
TOKEN=$(cat access_token.txt)

curl -X POST "https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/api/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "name": "Smartphone", "price": "699.00", "categories": [1] }'
```

### Place Order (Production)
```bash
curl -X POST "https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/api/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "items": [ { "product_id": 1, "quantity": 2 } ] }'
```

---

## ✅ CI Pipeline (GitHub Actions)
- `ci-docker-compose.yaml` runs on PRs and main pushes
- Runs pytest & drf-spectacular docs
- Publishes:
  - 📄 ReDoc: `/docs/index.html`
  - 📄 Swagger: `/docs/swagger.html`
- Pushes Docker image to GHCR

CI Status: ![CI](https://github.com/danWinga/sil-backend/actions/workflows/ci-docker-compose.yaml/badge.svg)

---

## 📦 CD Pipeline: OpenShift via Helm
- Secrets managed via `oc create secret generic si-backend-secret`
- Helm charts deploy:
  - `si-api`
  - `si-worker`
- Images pulled from GHCR (by tag or latest)

Secrets include:
- `DATABASE_URL`, `SECRET_KEY`, `RABBITMQ_URL`
- `OIDC_*`, `AFRICAS_TALKING_*`, `EMAIL_*`

---

## 🔐 Admin Consoles
- **Keycloak**: [Keycloak Admin](https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/)
- **Django Admin**: [SI Admin](https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/admin/)

---

## 🚩 OpenShift Deployment URLs
- **API Base URL**: [https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/api/](https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/api/)
- **Admin Panel**: [https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/admin/](https://si-api-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/admin/)
- **Keycloak Auth Server**: [https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/](https://si-keycloak-danwinga-dev.apps.rm3.7wse.p1.openshiftapps.com/)

These are public-facing endpoints deployed to OpenShift on AWS.

---

## 🔃 Production cURL Test
Use these examples to test the live deployment:

### 1. Get Token
See: [API Usage Examples → Get Token](#get-token)

### 2. Create Product
See: [API Usage Examples → Create Product (Production)](#create-product-production)

### 3. Place Order
See: [API Usage Examples → Place Order (Production)](#place-order-production)

---

## 🛠️ Troubleshooting
| Issue                        | Fix |
|-----------------------------|-----|
| 401 Unauthorized            | Check Keycloak user/creds |
| 403 Forbidden               | Missing role in realm |
| Helm deployment hangs       | Check pod logs in OpenShift |
| Missing secrets             | Add all required vars in GitHub/oc secrets |

---

## 📜 License
MIT License © 2025 [Daniel Ooro Winga](https://www.linkedin.com/in/daniel-winga-8b910032/)
