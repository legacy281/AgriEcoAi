# app/core/recommender.py

from app.api.services.recommend_service import load_data, process_and_add_item
from sentence_transformers import SentenceTransformer


# Load model và embeddings **1 lần khi startup**
print("Loading model and embeddings...")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
embeddings, df = load_data()

print(f"Model loaded: {model.__class__.__name__}")
print(f"Embeddings shape: {embeddings.shape}, Metadata rows: {len(df)}")

def add_new_item(data: dict):
    global embeddings, df  # cho phép update ngay trong RAM

    result = process_and_add_item(data, model)

    # Reload embeddings & metadata sau khi append
    embeddings, df = load_data()

    return result