import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
MONGO_DB = os.getenv("MONGO_DB", "demo_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "documents")


class MongoClientHolder:
    client: AsyncIOMotorClient | None = None


holder = MongoClientHolder()


@asynccontextmanager
async def lifespan(app):  # FastAPI lifespan context
    holder.client = AsyncIOMotorClient(MONGO_URI)
    try:
        yield
    finally:
        if holder.client is not None:
            holder.client.close()
            holder.client = None


async def get_collection() -> AsyncGenerator[AsyncIOMotorCollection, None]:
    if holder.client is None:
        holder.client = AsyncIOMotorClient(MONGO_URI)
    db = holder.client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    yield collection


