from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.recommender import model, embeddings, df
from app.api.services.recommend_service import recommend, process_and_add_item

# Tạo router FastAPI
router = APIRouter()

# -------------------------------
# Schema cho API /recommend
# -------------------------------
class QueryItem(BaseModel):
    categoryName: str = ""
    productName: str = ""
    price: str = ""
    quantity: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""

@router.post("/")
def get_recommendation(query: QueryItem, top_k: int = 10):
    result = recommend(query.dict(), embeddings, df, model, top_k=top_k)
    return {
        "top_results": [
            {"id": r[0], "score": r[1]} 
            for r in result
        ]
    }


# -------------------------------
# Schema cho API /add-item
# -------------------------------
class AddItemPayload(BaseModel):
    id: str
    title: str
    content: str
    latitude: float
    longitude: float
    address: str
    categoryName: str
    productName: str
    price: str
    quantity: str

@router.post("/add-item")
def add_item_api(payload: AddItemPayload):
    """
    🎯 Format đầu vào mong muốn:
    {
        "id": "...",
        "title": "...",
        "content": "...",
        "latitude": 20.83,
        "longitude": 106.66,
        "address": "...",
        "categoryName": "...",
        "productName": "...",
        "price": "14.952 đ/kg",
        "quantity": "4.779 kg"
    }
    """
    return process_and_add_item(payload.dict(), model)
