import google.generativeai as genai

from app.core.config import MODEL_NAME


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
