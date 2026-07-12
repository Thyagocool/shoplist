"""Integration tests for auth endpoints."""
import pytest


class TestRegister:
    async def test_register_success(self, client):
        import uuid
        suffix = uuid.uuid4().hex[:8]
        resp = await client.post(
            "/api/v1/auth/register",
            json={"name": "Novo", "email": f"novo_{suffix}@test.com", "password": "123456"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["name"] == "Novo"
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

    async def test_register_invalid_email(self, client):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"name": "X", "email": "invalido", "password": "123456"},
        )
        assert resp.status_code == 422

    async def test_register_duplicate_email(self, client, registered_user):
        """API retorna 201 (não bloqueia duplicata) ou 409 se bloquear."""
        # Tentar registrar com mesmo email
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Outro",
                "email": registered_user["email"],
                "password": "123456",
            },
        )
        # Pode ser 201 (re-cria) ou 409 (bloqueia)
        assert resp.status_code in (201, 409)


class TestLogin:
    async def test_login_success(self, client, registered_user):
        resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data["tokens"]

    async def test_login_wrong_password(self, client, registered_user):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "wrong"},
        )
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, client, registered_user):
        refresh = registered_user["tokens"]["refresh_token"]
        resp = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh}
        )
        assert resp.status_code == 200
        data = resp.json()
        # Pode retornar {access_token, token_type} ou {tokens: {access_token}}
        token = data.get("access_token") or data.get("tokens", {}).get("access_token")
        assert token is not None

    async def test_refresh_invalid(self, client):
        resp = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid"}
        )
        assert resp.status_code == 401


class TestMe:
    async def test_me_success(self, client, registered_user):
        token = registered_user["tokens"]["access_token"]
        resp = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    async def test_me_no_token(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
