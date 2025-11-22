import json
import os
# Xóa: import google.generativeai as genai
# Import client từ thư viện mới
from google import genai 
from pydantic import BaseModel
# Import cấu hình từ thư viện mới
from google.genai.types import GenerateContentConfig
from app.core.config import MODEL_NAME
# Khởi tạo client
API_KEY = os.environ.get("LLM_API_KEY")
client = genai.Client(api_key=API_KEY)
class ExtractSchema(BaseModel):
    categoryName: str
    productName: str
    productType: str
    quantity: str
    price: str

class ChatService:
    """Chat Service."""

    @staticmethod
    def general_chat(message: str):
        """General Chat."""

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(message)
        print(response)
        text = response._result.candidates[0].content.parts[0].text
        return text
  
    @staticmethod
    def json_chat(prompt: str) -> dict:
        """
        Gọi Gemini để trả về JSON theo ExtractSchema bằng GenAI SDK mới.
        """
        try:
            # SỬA LỖI: Dùng client.models.generate_content
            response = client.models.generate_content( 
                model=MODEL_NAME, # Bắt buộc phải truyền model khi dùng Client
                contents=prompt,
                # SỬ DỤNG 'config' (tham số này đúng cho Client mới)
                config=GenerateContentConfig( 
                    response_mime_type="application/json",
                    # .model_json_schema() là đúng cho Pydantic v2
                    response_schema=ExtractSchema.model_json_schema(), 
                ),
            )
            
            text = response.text
            return json.loads(text)
        
        except Exception as e:
            # ... (xử lý lỗi)
            print(f"Lỗi API hoặc lỗi khác: {e}")
            return {}