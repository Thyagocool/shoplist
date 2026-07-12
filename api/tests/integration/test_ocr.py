"""Integration tests for OCR endpoint."""
import io

import pytest


@pytest.fixture
async def auth_header(client, registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestOCR:
    async def test_upload_small_image(self, client, auth_header):
        """Create a tiny valid PNG and upload it."""
        # Minimal valid PNG (1x1 pixel)
        png_bytes = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000d49444154789c626000000002000198e19525000000004945ae426082"
        )
        files = {"file": ("test.png", io.BytesIO(png_bytes), "image/png")}
        resp = await client.post("/api/v1/ocr", files=files, headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert "raw_text" in data
        assert "items" in data

    async def test_upload_no_file(self, client, auth_header):
        resp = await client.post("/api/v1/ocr", headers=auth_header)
        assert resp.status_code == 422

    async def test_upload_invalid_extension(self, client, auth_header):
        files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
        resp = await client.post("/api/v1/ocr", files=files, headers=auth_header)
        assert resp.status_code == 400
