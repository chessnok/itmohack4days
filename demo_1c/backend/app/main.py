from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, List, Dict
from datetime import datetime, timezone

from .deps import get_collection, lifespan


app = FastAPI(lifespan=lifespan)

# Permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/create_document")
async def create_document(payload: Dict, collection=Depends(get_collection)):
    # persist creation timestamp in ISO 8601 for correct lexicographic sorting
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await collection.insert_one(payload)
    return {"inserted_id": str(result.inserted_id)}


@app.get("/api/get_documents")
async def get_documents(collection=Depends(get_collection)) -> List[Dict]:
    documents: List[Any] = []
    cursor = collection.find().sort("created_at", -1)
    async for doc in cursor:
        # Convert ObjectId to string for JSON serialization
        if "_id" in doc:
            doc["_id"] = str(doc["_id"]) 
        documents.append(doc)
    return documents


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
