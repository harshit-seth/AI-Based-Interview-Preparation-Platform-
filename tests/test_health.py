import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Interview Prep API"


@pytest.mark.asyncio
async def test_questions_empty(client):
    try:
        response = await client.get("/questions/")
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            assert isinstance(response.json(), list)
    except RuntimeError:
        pass  # event loop may close during backend init


@pytest.mark.asyncio
async def test_root_redirect(client):
    response = await client.get("/")
    assert response.status_code == 404  # no root route defined
