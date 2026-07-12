"""Integration tests for inventory flow."""
import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def category_id(client, auth_header):
    resp = await client.post(
        "/api/v1/categories", json={"name": "Limpeza"}, headers=auth_header
    )
    return resp.json()["id"]


@pytest.fixture
async def items(client, auth_header, category_id):
    ids = []
    for name, stock in [("Sabão", 5), ("Detergente", 3)]:
        resp = await client.post(
            "/api/v1/items",
            json={
                "name": name,
                "category_id": category_id,
                "unit": "un",
                "min_stock": "1.0",
                "max_stock": str(stock),
            },
            headers=auth_header,
        )
        ids.append(resp.json()["id"])
    return ids


class TestInventory:
    async def test_declare_and_get(self, client, auth_header, items):
        # Create list
        list_resp = await client.post(
            "/api/v1/lists", json={"name": "Inv List"}, headers=auth_header
        )
        list_id = list_resp.json()["id"]

        # Declare — usa pre_registered_item_id (não item_id)
        resp1 = await client.post(
            "/api/v1/inventory",
            json={
                "shopping_list_id": list_id,
                "pre_registered_item_id": items[0],
                "declared_quantity": "2.0",
            },
            headers=auth_header,
        )
        assert resp1.status_code == 201
        assert float(resp1.json()["calculated_need"]) == 3.0  # max 5, tenho 2

        resp2 = await client.post(
            "/api/v1/inventory",
            json={
                "shopping_list_id": list_id,
                "pre_registered_item_id": items[1],
                "declared_quantity": "4.0",
            },
            headers=auth_header,
        )
        assert resp2.status_code == 201
        assert float(resp2.json()["calculated_need"]) == 0.0  # max 3, tenho 4

        # Get inventory for list (via query param)
        get_resp = await client.get(
            "/api/v1/inventory",
            params={"list_id": str(list_id)},
            headers=auth_header,
        )
        assert get_resp.status_code == 200
        decl = get_resp.json()
        assert len(decl) == 2
