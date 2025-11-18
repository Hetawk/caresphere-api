from __future__ import annotations

import os
import importlib

from fastapi.testclient import TestClient

# Ensure sqlite is used for tests (avoid touching remote DB)
os.environ["DB_URL"] = "sqlite:///:memory:"

# reload settings & database modules to pick up test DB_URL
import app.main as main
import app.config as config

client = TestClient(main.app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"


def test_settings_load_from_env(monkeypatch):
    # Temporarily set env and reload settings
    monkeypatch.setenv("DB_URL", "sqlite:///:memory:")
    importlib.reload(config)
    assert config.settings.DATABASE_URL.startswith("sqlite")
