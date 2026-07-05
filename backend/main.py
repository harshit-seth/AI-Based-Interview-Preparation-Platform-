import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routes import auth, feedback, history, questions
from backend.services.db_service import db_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    logger.info("Starting up...")
    yield
    if db_service.client:
        logger.info("Shutting down — disconnecting MongoDB...")
        await db_service.disconnect()
        logger.info("MongoDB disconnected.")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(feedback.router)
app.include_router(history.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/db-test")
async def db_test():
    try:
        col = await db_service.get_collection("questions")
        if col is None:
            return {"status": "disconnected"}
        await db_service.client.admin.command("ping")
        return {"status": "connected", "database": settings.MONGO_DB_NAME}
    except Exception as e:
        logger.exception("DB health check failed")
        return {"status": "error", "detail": str(e)}
