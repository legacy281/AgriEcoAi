import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from google.genai.types import GenerateContentConfig
from google import genai
from agno.agent import Agent
load_dotenv()
GOOGLE_API_KEY = os.getenv("LLM_API_KEY")
print("GOOGLE_API_KEY loaded1:", GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# ==============================
# Schema JSON output
# ==============================
class SupplyDemandSchema(BaseModel):
    product: str
    region: str
    predicted_supply: int
    predicted_demand: int
    source: str

# ==============================
# Agent
# ==============================
class DemandAgent(Agent):
    """Agent dùng GenAI SDK mới để dự đoán lượng cung/cầu nông sản."""
    name = "Demand Agent"
    description = "Predicts supply and demand for a specific agricultural product."

    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def predict_supply_demand(self, product: str, region: str = "Việt Nam", month: str = "4", year: str = None) -> dict:
        """Dự đoán supply/demand theo sản phẩm, vùng và thời điểm."""
        prompt = f"""
        You are an expert agricultural analyst.
        Predict the expected supply and demand for the product "{product}" in region "{region}" 
        for the next {month} months.
        Return strictly valid JSON matching SupplyDemandSchema.
        Respond ONLY with JSON, no explanations.
        """
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SupplyDemandSchema.model_json_schema()
                )
            )
            print("DemandAgent API response:", response.text)
            return json.loads(response.text)
        except Exception as e:
            print("❌ Supply/Demand API error:", e)
            # Fallback dummy data
            return {
                "product": product,
                "region": region,
                "predicted_supply": 12000,
                "predicted_demand": 10000,
                "source": "Fallback/Dummy / Historical Data"
            }


