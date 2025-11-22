import json
import os
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai 
from agno.agent import Agent


load_dotenv()
GOOGLE_API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# ==============================
# Schema để Gemini trả JSON
# ==============================
class MarketPriceSchema(BaseModel):
    average_price: int
    min_price: int
    max_price: int
    source: str

class PredictedPriceSchema(BaseModel):
    predicted_price: int
    confidence: str

# ==============================
# Agent
# ==============================
class PriceAgent(Agent):
    """Agent dùng GenAI SDK mới để tra cứu giá sản phẩm."""
    name = "Price Agent"
    description = "Get market price data for agricultural products."

    def __init__(self):
        print("Initializing PriceAgent...")
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def llm_search_market_price(self, product: str, region: str) -> dict:
        print("Searching market price for", product, "in", region)
        prompt = f"""
        You are an expert agricultural market analyst. 
        Given the product "{product}" and region "{region}", 
        return the current average market price, min and max price, 
        in JSON strictly matching MarketPriceSchema.
        Respond ONLY with JSON, no explanations.
        """
        try:
            response = self.client.models.generate_content(
                model = MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MarketPriceSchema.model_json_schema()
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print("❌ Market price API error:", e)
            return {
                "average_price": 25000,
                "min_price": 23000,
                "max_price": 27000,
                "source": "Fallback/Dummy"
            }

    def llm_predict_future_price(self, product: str, region: str) -> dict:
        prompt = f"""
You are an expert agricultural market analyst. 
Given the product "{product}" and region "{region}", 
predict the price for the next month and provide a confidence level.
Return strictly JSON matching PredictedPriceSchema.
Respond ONLY with JSON.
"""
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PredictedPriceSchema.model_json_schema()
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print("❌ Predicted price API error:", e)
            return {
                "predicted_price": 26000,
                "confidence": "80%"
            }

    def suggest_price(self, current_price: int, predicted_price: int) -> int:
        return int((current_price + predicted_price) / 2)
    def format_price_response(self, product: str, region: str, market: dict, future: dict, suggested: int) -> str:
        """
        Gửi dữ liệu sang Gemini để viết lại thành câu trả lời tự nhiên.
        """
        prompt = f"""
You are an agricultural market advisor.
Rewrite the following data into a natural, human-friendly explanation:

Product: {product}
Region: {region}

Current Market Price:
- Average: {market['average_price']} đ/kg
- Min: {market['min_price']} đ/kg
- Max: {market['max_price']} đ/kg
- Source: {market['source']}

Predicted Future Price:
- Next Month: {future['predicted_price']} đ/kg
- Confidence: {future['confidence']}

Suggested Trading Price:
- {suggested} đ/kg

Write the answer as a friendly advisory message for farmers.
Do NOT output JSON. Respond in natural Vietnamese.
"""
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print("❌ Natural response API error:", e)
            return (
                f"Giá {product} tại {region} hiện trung bình khoảng {market['average_price']:,} đ/kg. "
                f"Dự đoán tháng tới khoảng {future['predicted_price']:,} đ/kg. "
                f"Giá giao dịch gợi ý: {suggested:,} đ/kg."
            )

    def execute(self, product: str, region: str = "Việt Nam") -> str:
        market_data = self.llm_search_market_price(product, region)
        future_data = self.llm_predict_future_price(product, region)
        suggested_price = self.suggest_price(
            market_data.get("average_price", 25000),
            future_data.get("predicted_price", 26000)
        )

        # 🔥 Gọi hàm tạo câu trả lời tự nhiên
        natural_text = self.format_price_response(
            product, region, market_data, future_data, suggested_price
        )

        return natural_text


