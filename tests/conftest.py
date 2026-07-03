import os

os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DB_NAME"] = "test_interview_prep"
os.environ["ANTHROPIC_API_KEY"] = "sk-test-placeholder"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
