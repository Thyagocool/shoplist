"""Integration tests for items (pre-registered) CRUD."""
import uuid

import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def category_id(client, auth_header):
    resp = await client.post(
        "/api/v1/categories", json={"name": "Grãos"}, headers=auth_header
    )
    return resp.json()["id"]


class TestCreateItem:
    async def test_create_success(self, client, auth_header, category_id):
        resp = await client.post(
            "/api/v1/items",
            json={
                "name": "Arroz",
                "category_id": category_id,
                "unit": "kg",
                "default_quantity": "1.0",
                "min_stock": "1.0",
                "max_stock": "5.0",
            },
            headers=auth_header,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Arroz"
        assert data["active"] is True


class TestListItem:
    async def test_list_all(self, client, auth_header, category_id):
        suffix = uuid.uuid4().hex[:6]
        await client.post(
            "/api/v1/items",
            json={"name": f"ItemA_{suffix}", "category_id": category_id, "unit": "un"},
            headers=auth_header,
        )
        await client.post(
            "/api/v1/items",
            json={"name": f"ItemB_{suffix}", "category_id": category_id, "unit": "un"},
            headers=auth_header,
        )
        resp = await client.get("/api/v1/items", headers=auth_header)
        items = [i for i in resp.json() if suffix in i["name"]]
        assert len(items) == 2


class TestSoftDelete:
    async def test_deactivate_item(self, client, auth_header, category_id):
        suffix = uuid.uuid4().hex[:6]
        created = await client.post(
            "/api/v1/items",
            json={
                "name": f"ItemX_{suffix}",
                "category_id": category_id,
                "unit": "un",
            },
            headers=auth_header,
        )
        item_id = created.json()["id"]
        # Soft delete
        resp = await client.delete(f"/api/v1/items/{item_id}", headers=auth_header)
        assert resp.status_code == 204
        # Should not appear in listing
        resp2 = await client.get("/api/v1/items", headers=auth_header)
        names = [i["name"] for i in resp2.json()]
        assert f"ItemX_{suffix}" not in names
