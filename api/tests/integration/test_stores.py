"""Integration tests for stores CRUD."""
import uuid

import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCreateStore:
    async def test_create_success(self, client, auth_header):
        resp = await client.post(
            "/api/v1/stores",
            json={"name": "Supermercado ABC"},
            headers=auth_header,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Supermercado ABC"
        # address não é retornado pela API
        assert "id" in data


class TestListStores:
    async def test_list(self, client, auth_header):
        suffix = uuid.uuid4().hex[:6]
        await client.post(
            "/api/v1/stores", json={"name": f"LojaA_{suffix}"}, headers=auth_header
        )
        await client.post(
            "/api/v1/stores", json={"name": f"LojaB_{suffix}"}, headers=auth_header
        )
        resp = await client.get("/api/v1/stores", headers=auth_header)
        stores = [s for s in resp.json() if suffix in s["name"]]
        assert len(stores) == 2


class TestUpdateStore:
    async def test_update(self, client, auth_header):
        created = await client.post(
            "/api/v1/stores", json={"name": "Antiga"}, headers=auth_header
        )
        store_id = created.json()["id"]
        resp = await client.put(
            f"/api/v1/stores/{store_id}",
            json={"name": "Nova"},
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Nova"


class TestDeleteStore:
    async def test_delete(self, client, auth_header):
        created = await client.post(
            "/api/v1/stores", json={"name": "Remover"}, headers=auth_header
        )
        store_id = created.json()["id"]
        resp = await client.delete(f"/api/v1/stores/{store_id}", headers=auth_header)
        assert resp.status_code == 204
