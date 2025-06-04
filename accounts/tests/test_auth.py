# accounts/tests/test_auth.py

import pytest
import requests
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


def get_token():
    """
    Fetch a user token via Keycloak password grant.
    """
    resp = requests.post(
        "http://localhost:8080/realms/si/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "si-backend",
            "client_secret": "supersecret",
            "username": "testuser",
            "password": "password",
        },
    )
    assert resp.status_code == 200, "Failed to get token"
    return resp.json()["access_token"]


def test_no_auth_returns_403(client):
    resp = client.get("/api/products/")
    assert resp.status_code == 403  # PermissionDenied


def test_bad_token_returns_403(client):
    client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token")
    resp = client.get("/api/products/")
    assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.skip(reason="Integration against Keycloak skipped in CI/Docker")
def test_valid_token_allows_access(client):
    token = get_token()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.get("/api/products/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
