"""Integration tests for categories CRUD."""
import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCreateCategory:
    async def test_create_success(self, client, auth_header):
        resp = await client.post(
            "/api/v1/categories",
            json={"name": "Carnes"},
            headers=auth_header,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Carnes"
        assert "id" in resp.json()

    async def test_create_unauthenticated(self, client):
        resp = await client.post("/api/v1/categories", json={"name": "Teste"})
        assert resp.status_code == 401


class TestListCategories:
    async def test_list_empty(self, client, auth_header):
        # Create a unique suffix to ensure we find only our categories
        import uuid

        suffix = uuid.uuid4().hex[:6]
        resp = await client.get("/api/v1/categories", headers=auth_header)
        before = len(resp.json())

        await client.post(
            f"/api/v1/categories",
            json={"name": f"Frutas_{suffix}"},
            headers=auth_header,
        )
        await client.post(
            f"/api/v1/categories",
            json={"name": f"Verduras_{suffix}"},
            headers=auth_header,
        )
        resp = await client.get("/api/v1/categories", headers=auth_header)
        assert len(resp.json()) == before + 2


class TestUpdateCategory:
    async def test_update_success(self, client, auth_header):
        created = await client.post(
            "/api/v1/categories", json={"name": "Antigo"}, headers=auth_header
        )
        cat_id = created.json()["id"]
        resp = await client.put(
            f"/api/v1/categories/{cat_id}",
            json={"name": "Novo Nome"},
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Novo Nome"

    async def test_update_not_found(self, client, auth_header):
        resp = await client.put(
            "/api/v1/categories/00000000-0000-0000-0000-000000000000",
            json={"name": "Nada"},
            headers=auth_header,
        )
        assert resp.status_code == 404


class TestDeleteCategory:
    async def test_delete_success(self, client, auth_header):
        created = await client.post(
            "/api/v1/categories", json={"name": "Remover"}, headers=auth_header
        )
        cat_id = created.json()["id"]
        resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=auth_header)
        assert resp.status_code == 204

    async def test_delete_not_found(self, client, auth_header):
        resp = await client.delete(
            "/api/v1/categories/00000000-0000-0000-0000-000000000000",
            headers=auth_header,
        )
        # API retorna 400 com "Category not found" ou 404
        assert resp.status_code in (400, 404)
        assert "not found" in resp.text.lower()
