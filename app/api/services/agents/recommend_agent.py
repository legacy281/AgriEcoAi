import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from google.genai.types import GenerateContentConfig
from google import genai
from agno.agent import Agent

load_dotenv()
GOOGLE_API_KEY = os.getenv("LLM_API_KEY")
print("GOOGLE_API_KEY loaded2:", GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# ==============================
# Schema JSON output
# ==============================
class ProductSupplyDemandSchema(BaseModel):
    product: str
    region: str
    predicted_supply: int
    predicted_demand: int
    source: str

# ==============================
# Agent
# ==============================
class RecommendAgent(Agent):
    """Agent dự đoán cung/cầu cho các sản phẩm nổi bật theo vùng."""
    name = "Recommend Agent"
    description = "Predicts supply and demand for top agricultural products in a specific region."

    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def predict_supply_demand_for_product(self, product: str, region: str) -> dict:
        """Dự đoán supply/demand cho 1 sản phẩm."""
        prompt = f"""
Bạn là chuyên gia phân tích nông nghiệp. 
Cho sản phẩm "{product}" ở vùng "{region}", 
dự đoán lượng cung và cầu trong đơn vị sản phẩm.
Trả về JSON đúng định dạng ProductSupplyDemandSchema.
Chỉ trả JSON, không giải thích.
"""
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProductSupplyDemandSchema.model_json_schema()
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Lỗi dự đoán cho sản phẩm {product}:", e)
            return {
                "product": product,
                "region": region,
                "predicted_supply": 12000,
                "predicted_demand": 10000,
                "source": "Fallback/Dummy / Historical Data"
            }

    def predict_top_products_in_region(self, location) -> list:
        """Tìm top N sản phẩm nổi bật trong vùng và dự đoán supply/demand."""
        # 1️⃣ Gợi ý danh sách sản phẩm nổi bật trong vùng
        prompt_products = f"""
Bạn là chuyên gia nông nghiệp. 
Liệt kê top 5 sản phẩm nông sản nổi bật ở vùng "{location}" 
có hoạt động thị trường sôi động. 
Trả về mảng JSON các tên sản phẩm như ["sản phẩm 1", "sản phẩm 2", ...].
Chỉ trả JSON, không giải thích.
"""
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt_products,
                config=GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            products = json.loads(response.text)
        except Exception as e:
            print("❌ Lỗi lấy top sản phẩm:", e)
            # Fallback dummy
            products = ["cam sành", "bưởi", "xoài", "nhãn", "chuối"]

        # 2️⃣ Dự đoán supply/demand cho từng sản phẩm
        results = []
        for product in products:
            data = self.predict_supply_demand_for_product(product, location)
            results.append(data)
        print("RecommendAgent results:", results)
        return results

# ==============================
# Test nhanh
# ==============================

