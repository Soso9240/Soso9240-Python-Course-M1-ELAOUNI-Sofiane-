"""Tests for api/main.py routes."""

import os

os.environ["API_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "cpu_percent" in body
    assert "memory_percent" in body
    assert "disk_percent" in body


def test_register_server_without_api_key_is_forbidden():
    resp = client.post("/servers", json={"name": "srv1", "host": "10.0.0.1", "port": 8080})
    assert resp.status_code == 403


def test_register_server_with_valid_api_key():
    resp = client.post(
        "/servers",
        json={"name": "srv1", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": "test-secret-key"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "srv1"
    assert body["status"] == "unknown"


def test_get_nonexistent_server_returns_404():
    resp = client.delete(
        "/servers/9999", headers={"X-API-Key": "test-secret-key"}
    )
    assert resp.status_code == 404
