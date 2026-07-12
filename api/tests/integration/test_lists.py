"""Integration tests for shopping lists (full flow)."""
import uuid

import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def category_id(client, auth_header):
    resp = await client.post(
        "/api/v1/categories", json={"name": "Bebidas"}, headers=auth_header
    )
    return resp.json()["id"]


@pytest.fixture
async def item_id(client, auth_header, category_id):
    resp = await client.post(
        "/api/v1/items",
        json={
            "name": "Refrigerante",
            "category_id": category_id,
            "unit": "l",
            "default_quantity": "2.0",
            "min_stock": "1.0",
            "max_stock": "6.0",
        },
        headers=auth_header,
    )
    return resp.json()["id"]


class TestCreateList:
    async def test_create_success(self, client, auth_header):
        resp = await client.post(
            "/api/v1/lists", json={"name": "Feira Semanal"}, headers=auth_header
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Feira Semanal"
        assert data["status"] == "in_progress"

    async def test_create_with_store(self, client, auth_header):
        store = await client.post(
            "/api/v1/stores", json={"name": "Mercado"}, headers=auth_header
        )
        resp = await client.post(
            "/api/v1/lists",
            json={"name": "Lista Mercado", "store_id": store.json()["id"]},
            headers=auth_header,
        )
        assert resp.status_code == 201


class TestListItemFlow:
    """Full flow: create list → add items → toggle → complete."""

    async def test_add_and_checkout(self, client, auth_header, item_id):
        # Create list
        lst = await client.post(
            "/api/v1/lists", json={"name": "Lista Teste Checkout"}, headers=auth_header
        )
        list_id = lst.json()["id"]

        # Add catalog item using pre_registered_item_id
        add_resp = await client.post(
            f"/api/v1/lists/{list_id}/items",
            json={
                "pre_registered_item_id": item_id,
                "estimated_quantity": "2.0",
            },
            headers=auth_header,
        )
        assert add_resp.status_code == 201
        item_data = add_resp.json()
        item_list_id = item_data["id"]

        # Toggle check — rota: PATCH /api/v1/lists/items/{item_id}/toggle
        toggle_resp = await client.patch(
            f"/api/v1/lists/items/{item_list_id}/toggle",
            headers=auth_header,
        )
        assert toggle_resp.status_code == 200
        assert toggle_resp.json()["checked"] is True

        # Checkout — precisa enviar body com items
        checkout_resp = await client.post(
            f"/api/v1/lists/{list_id}/checkout",
            json={
                "items": [
                    {
                        "shopping_list_item_id": str(item_list_id),
                        "price_cents": 899,
                    }
                ]
            },
            headers=auth_header,
        )
        assert checkout_resp.status_code == 200
        data = checkout_resp.json()
        assert data["list_status"] == "completed"
        assert len(data["movements"]) > 0
        # Movement deve ter código sequencial
        assert data["movements"][0]["sequential_code"].startswith("MOV-")


class TestRemoveItem:
    async def test_remove_item_from_list(self, client, auth_header, item_id):
        # Create list
        lst = await client.post(
            "/api/v1/lists", json={"name": "Lista Remover"}, headers=auth_header
        )
        list_id = lst.json()["id"]

        # Add item
        add_resp = await client.post(
            f"/api/v1/lists/{list_id}/items",
            json={"pre_registered_item_id": item_id, "estimated_quantity": "1"},
            headers=auth_header,
        )
        assert add_resp.status_code == 201
        item_list_id = add_resp.json()["id"]

        # Remove item
        remove_resp = await client.delete(
            f"/api/v1/lists/items/{item_list_id}", headers=auth_header
        )
        assert remove_resp.status_code == 204

        # Verify removed
        get_resp = await client.get(f"/api/v1/lists/{list_id}", headers=auth_header)
        assert len(get_resp.json()["items"]) == 0

    async def test_remove_not_found(self, client, auth_header):
        resp = await client.delete(
            "/api/v1/lists/items/00000000-0000-0000-0000-000000000000",
            headers=auth_header,
        )
        assert resp.status_code == 404


class TestCancelList:
    async def test_cancel(self, client, auth_header):
        lst = await client.post(
            "/api/v1/lists", json={"name": "Cancelar"}, headers=auth_header
        )
        list_id = lst.json()["id"]
        cancel_resp = await client.post(
            f"/api/v1/lists/{list_id}/cancel", headers=auth_header
        )
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"
