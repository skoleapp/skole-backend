from __future__ import annotations

from django.test.client import Client


def test_health_check() -> None:
    client = Client()
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b""
