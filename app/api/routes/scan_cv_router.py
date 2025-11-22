from fastapi import APIRouter
from pydantic import BaseModel
import re
from app.api.services.chat_service import ChatService
import json

router = APIRouter()
chat_service = ChatService()

# =======================
# Schema
# =======================
class PostDescription(BaseModel):
    description: str

class PostInfo(BaseModel):
    category: str
    categoryName: str
    productName: str
    productType: str
    quantity: str
    price: str

CATEGORY_NAMES = ["Rau củ", "Cây ăn quả", "Cây công nghiệp"]

# =======================
# Endpoint
# =======================
@router.post("/extract-post", response_model=PostInfo)
async def extract_post_info(payload: PostDescription):
    text = payload.description
    category = "Nông sản"

    # =======================
    # Prompt LLM
    # =======================
    prompt = f"""
You are a structured data extraction assistant. 
Extract the following fields from the post description below.

Rules:
1. categoryName: one of {CATEGORY_NAMES}. If unclear, pick the closest.
2. productName: Extract the name of the product being sold.
   - Examples: 
       - 'cam sành'
       - 'Táo Envy'
3. productType: one of 'Hữu cơ', 'Sạch', 'Thường'
4. quantity: numeric value with unit 'kg', e.g., '2.744 kg'
5. price: numeric value with unit 'đ/kg', e.g., '31.695 đ/kg'

Return strictly valid JSON with ONLY these keys: categoryName, productName, productType, quantity, price. 
Do NOT add any text or explanation.

Post description:
{text}
"""

    # =======================
    # Khởi tạo giá trị
    # =======================
    categoryName = productName = productType = quantity = price = None

    # =======================
    # 1️⃣ Try LLM extraction
    # =======================
    try:
        ai_data = chat_service.json_chat(prompt)
        print('ai_response:', ai_data)
        print("AI Data:", ai_data)
        categoryName = ai_data.get("categoryName")
        productName = ai_data.get("productName")
        productType = ai_data.get("productType")
        quantity = ai_data.get("quantity")
        price = ai_data.get("price")
    except Exception as e:
        print("LLM extraction failed, falling back to rule-based extraction.", e)
        pass

    # =======================
    # 2️⃣ Fallback rule-based
    # =======================
    # categoryName
    if not categoryName or not isinstance(categoryName, str):
        categoryName = None
        for name in CATEGORY_NAMES:
            if name.lower() in text.lower():
                categoryName = name
                break
        if not categoryName:
            categoryName = "Cây ăn quả"  # default

    # productName
    if not productName or not isinstance(productName, str):
        # Tìm cụm từ trước "kg"
        match = re.search(r"([\w\s\-]+)\s*kg", text, re.IGNORECASE)
        if match:
            product_candidate = match.group(1).strip()
            # Loại bỏ số ở đầu
            product_candidate = re.sub(r"^[\d\.,]+\s*", "", product_candidate)
            productName = product_candidate if product_candidate else "Unknown"
        else:
            productName = "Unknown"

    # productType
    if not productType or not isinstance(productType, str):
        if "hữu cơ" in text.lower():
            productType = "Hữu cơ"
        elif "sạch" in text.lower():
            productType = "Sạch"
        else:
            productType = "Thường"

    # quantity
    if not quantity or not isinstance(quantity, str):
        match = re.search(r"([\d\.,]+)\s*kg", text)
        quantity = match.group(1) + " kg" if match else "Unknown"

    # price
    if not price or not isinstance(price, str):
        match = re.search(r"([\d\.,]+)\s*(đ|vnd)/kg", text.lower())
        price = match.group(1) + " đ/kg" if match else "Unknown"

    # =======================
    # Return
    # =======================
    return PostInfo(
        category=category,
        categoryName=categoryName,
        productName=productName,
        productType=productType,
        quantity=quantity,
        price=price
    )
