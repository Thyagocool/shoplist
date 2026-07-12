"""Fixtures for integration tests — test against the running API server."""
import uuid

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="session")
def base_url() -> str:
    return "http://api:8000"


@pytest.fixture
async def client(base_url: str):
    async with AsyncClient(base_url=base_url) as ac:
        yield ac


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a unique user and return user data + tokens."""
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "name": f"Test {suffix}",
        "email": f"test_{suffix}@test.com",
        "password": "123456",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    data = resp.json()
    return {
        "user": data["user"],
        "tokens": data["tokens"],
        "email": payload["email"],
        "password": payload["password"],
    }
