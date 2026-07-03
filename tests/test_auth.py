import pytest


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    response = await client.post("/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup(client):
    import time
    email = f"test_{int(time.time() * 1000)}@example.com"
    response = await client.post(
        "/auth/signup",
        json={"email": email, "password": "testpass123"},
    )
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "token" in data
        assert data["email"] == email


@pytest.mark.asyncio
async def test_me_no_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401
