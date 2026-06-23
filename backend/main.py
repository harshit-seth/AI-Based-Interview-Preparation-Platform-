from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import feedback, history, questions
from backend.services.db_service import db_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_service.connect()
    yield
    await db_service.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(feedback.router)
app.include_router(history.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/db-test")
async def db_test():
    try:
        await db_service.client.admin.command("ping")
        return {"status": "connected", "database": settings.MONGO_DB_NAME}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
