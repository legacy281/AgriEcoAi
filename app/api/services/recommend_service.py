# app/api/services/recommend_service.py
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from math import radians, sin, cos, sqrt, atan2
import re
import os
from pathlib import Path
from typing import Dict
import csv
# -----------------------------
# Tiền xử lý
# -----------------------------
def safe_str(x):
    return "" if pd.isna(x) else str(x).strip()

def extract_number(x):
    if x is None or pd.isna(x): 
        return np.nan
    s = str(x).replace(".", "").replace(",", ".")
    nums = re.findall(r"[\d\.]+", s)
    return float(nums[0]) if nums else np.nan

def extract_province(address):
    if not address or pd.isna(address):
        return ""
    parts = [p.strip() for p in str(address).split(",")]
    return ", ".join(parts[-2:]) if len(parts) >= 2 else str(address).strip()

# -----------------------------
# Load dữ liệu
# -----------------------------
BASE_DIR = Path(__file__).parent  # thư mục hiện tại: app/api/services/
EMB_DIR = BASE_DIR / "emb_files"  # app/api/services/emb_files/

EMB_FILE = EMB_DIR / "semantic_vectors.npy"
META_FILE = EMB_DIR / "product_metadata_nopro.csv"

def load_data(    
              emb_file=EMB_DIR / "semantic_vectors.npy",
    meta_file=EMB_DIR / "product_metadata_nopro.csv"
):
    embeddings = np.load(emb_file)
    df = pd.read_csv(meta_file, quotechar='"')
    
    # Preprocess semantic fields
    df["province"]     = df["address"].apply(lambda x: extract_province(x) if pd.notna(x) else "")
    df["categoryName"] = df["categoryName"].apply(safe_str)
    df["productName"]  = df["productName"].apply(safe_str)
    
    # Preprocess numerical fields
    df["price_num"]    = df["price"].apply(lambda x: extract_number(x) if pd.notna(x) else np.nan)
    df["quantity_num"] = df["quantity"].apply(lambda x: extract_number(x) if pd.notna(x) else np.nan)
    
    # Lat/Lon
    df["latitude"]  = df["latitude"].astype(float).fillna(np.nan)
    df["longitude"] = df["longitude"].astype(float).fillna(np.nan)
    
    return embeddings, df
# -----------------------------
# Cập nhật metadata và embeddings nếu cần
# -----------------------------

import os
import csv
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# File paths (đặt đúng với project)
EMB_FILE = "emb_files/semantic_vectors.npy"
META_FILE = "emb_files/product_metadata_nopro.csv"

# Hàm tiền xử lý
def safe_str(x):
    return "" if pd.isna(x) else str(x).strip()

def extract_number(x):
    if pd.isna(x) or x is None: 
        return np.nan
    x = str(x).replace(".", "").replace(",", ".")
    nums = re.findall(r"[\d\.]+", x)
    return float(nums[0]) if nums else np.nan

def extract_province(address):
    if not address or pd.isna(address):
        return ""
    parts = [p.strip() for p in address.split(",")]
    return ", ".join(parts[-2:]) if len(parts) >= 2 else address.strip()

# Hàm xử lý và thêm item
def process_and_add_item(data: dict, model: SentenceTransformer):
    """
    data: dict chứa item mới từ client
    model: SentenceTransformer đã được load
    """
    import re
    import csv

    try:
        # 1. Chuyển dữ liệu thành DataFrame
        df = pd.DataFrame([data])

        # 2. Drop các cột không cần thiết
        df = df.drop(columns=["title", "content"], errors="ignore")

        # 3. Tiền xử lý semantic fields
        df["province"]     = df["address"].apply(extract_province)
        df["categoryName"] = df["categoryName"].apply(safe_str)
        df["productName"]  = df["productName"].apply(safe_str)

        # 4. Tiền xử lý numerical fields
        df["price_num"]    = df["price"].apply(extract_number)
        df["quantity_num"] = df["quantity"].apply(extract_number)

        # 5. Lat/Lon
        df["latitude"]  = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)

        # 6. Tạo semantic_text
        df["semantic_text"] = (
            df["categoryName"] + " | " +
            df["productName"]
        ).apply(safe_str)

        # 7. Sắp xếp lại thứ tự cột chuẩn
        df = df[
            [
                "id", "categoryName", "productName", "price", "quantity",
                "latitude", "longitude", "address", "province",
                "price_num", "quantity_num", "semantic_text"
            ]
        ]

        semantic_text = df.loc[0, "semantic_text"]
        META_FILE = EMB_DIR / "product_metadata_nopro.csv"

        # 8. Append metadata vào CSV trước
        df.to_csv(
            META_FILE,
            mode="a",
            header=not os.path.exists(META_FILE),
            index=False,
            quoting=csv.QUOTE_ALL
        )

        # 9. Nếu metadata ghi thành công thì tạo embedding
        embedding = model.encode(semantic_text, normalize_embeddings=True)
        EMB_FILE = EMB_DIR / "semantic_vectors.npy"

        # 10. Append embedding vào semantic_vectors.npy
        if not os.path.exists(EMB_FILE):
            np.save(EMB_FILE, embedding.reshape(1, -1))
        else:
            old = np.load(EMB_FILE)
            new_vectors = np.vstack([old, embedding.reshape(1, -1)])
            np.save(EMB_FILE, new_vectors)

        return {
            "status": "success",
            "semantic_text": semantic_text,
            "embedding_dim": len(embedding)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# -----------------------------
# Similarity cơ bản
# -----------------------------
def price_similarity(p1, p2):
    if np.isnan(p1) or np.isnan(p2): return 0.0
    return max(0.0, 1 - abs(p1-p2)/max(p1,p2))

def quantity_similarity(q1, q2):
    if np.isnan(q1) or np.isnan(q2): return 0.0
    return max(0.0, 1 - abs(q1-q2)/max(q1,q2))

def location_similarity(lat1, lon1, lat2, lon2, max_km=50):
    if np.isnan(lat1) or np.isnan(lat2) or np.isnan(lon1) or np.isnan(lon2):
        return 0.0
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    dist = R * c
    return max(0.0, 1 - dist/max_km)

# -----------------------------
# Hàm recommend từ query dict
# -----------------------------
def recommend(query, embeddings, df, model, top_k=20, alpha=0.6, beta=0.1, gamma=0.2, delta=0.1):
    province = extract_province(query.get("address",""))
    category = query.get("categoryName","") or ""
    product = query.get("productName","") or ""
    price = extract_number(query.get("price", np.nan))
    quantity = extract_number(query.get("quantity", np.nan))
    latitude = float(query.get("latitude", np.nan))
    longitude = float(query.get("longitude", np.nan))

    semantic_text = f"{province} | {category} | {product}"
    query_vec = model.encode([semantic_text], normalize_embeddings=True)[0]

    semantic_scores = util.cos_sim(query_vec, embeddings)[0].cpu().numpy()
    top100_idx = semantic_scores.argsort()[-100:][::-1]

    results = []
    for idx in top100_idx:
        sem_score = float(semantic_scores[idx])
        pri_score = price_similarity(price, df.loc[idx,"price_num"])
        loc_score = location_similarity(latitude, longitude, df.loc[idx,"latitude"], df.loc[idx,"longitude"])
        qty_score = quantity_similarity(quantity, df.loc[idx,"quantity_num"])
        final_score = alpha*sem_score + beta*pri_score + gamma*loc_score + delta*qty_score
        results.append((df.loc[idx,"id"], final_score))

    results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
    return results
