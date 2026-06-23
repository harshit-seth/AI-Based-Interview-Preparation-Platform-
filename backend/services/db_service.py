from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from backend.config import settings


class MongoDBService:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB_NAME]
        try:
            await self.client.admin.command("ping")
            print("Connected to MongoDB")
        except ConnectionFailure:
            print("MongoDB connection failed")
            raise

    async def disconnect(self):
        if self.client:
            self.client.close()

    async def get_collection(self, name: str):
        return self.db[name]

    async def insert_one(self, collection: str, document: dict) -> str:
        col = await self.get_collection(collection)
        result = await col.insert_one(document)
        return str(result.inserted_id)

    async def find_one(self, collection: str, query: dict) -> dict | None:
        col = await self.get_collection(collection)
        return await col.find_one(query)

    async def find_many(
        self, collection: str, query: dict, limit: int = 50
    ) -> list[dict]:
        col = await self.get_collection(collection)
        cursor = col.find(query).limit(limit)
        return await cursor.to_list(length=limit)

    async def update_one(self, collection: str, query: dict, update: dict) -> bool:
        col = await self.get_collection(collection)
        result = await col.update_one(query, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, collection: str, query: dict) -> bool:
        col = await self.get_collection(collection)
        result = await col.delete_one(query)
        return result.deleted_count > 0

    async def get_user_history(self, user_id: str) -> list[dict]:
        col = await self.get_collection("sessions")
        cursor = col.find({"user_id": user_id}).sort("timestamp", -1)
        return await cursor.to_list(length=100)

    async def save_session(
        self, user_id: str, topic: str, question_id: str, score: int | None = None
    ) -> str:
        col = await self.get_collection("sessions")
        doc = {
            "user_id": user_id,
            "topic": topic,
            "question_id": question_id,
            "score": score,
            "timestamp": datetime.utcnow(),
        }
        result = await col.insert_one(doc)
        return str(result.inserted_id)


db_service = MongoDBService()
