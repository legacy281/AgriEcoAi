import json
import uuid
from typing import Dict, List
import os
from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel
import dotenv

dotenv.load_dotenv()

API_KEY = os.environ.get("LLM_API_KEY")
client = genai.Client(api_key=API_KEY)

class ChatBackend:
    def __init__(self, available_agents, product_name: str, region_name: str = "vietnam"):
        self.available_agents = available_agents
        self.product_name = product_name
        self.region_name = region_name
        self.client = client
        self.llm_model = "gemini-2.5-flash"

    def _call_agent_tool(self, agent_name: str) -> dict:
        agent_name = agent_name.lower()
        if agent_name == "price_agent":
            return self.available_agents['price_agent'].execute(self.product_name)
        elif agent_name == "recommend_agent":
            return self.available_agents['recommend_agent'].execute(self.region_name)
        elif agent_name == "demand_agent":
            return self.available_agents['demand_agent'].execute(self.product_name, self.region_name)
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    def _fallback_chat(self, user_input: str) -> str:
        prompt = f"User asked: {user_input}. Answer naturally."
        try:
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt,
                config=GenerateContentConfig(response_mime_type="text/plain")
            )
            return response.text
        except Exception as e:
            return f"❌ LLM fallback error: {e}"

    # ===================================================
    #   BỎ SESSION — Chỉ xử lý câu hỏi 1 lần rồi trả về
    # ===================================================
    def chat(self, user_input: str) -> Dict:

        tools_list = ", ".join(self.available_agents.keys())
        prompt = f"""
You are an AI router. User asked: "{user_input}"
Available tools/agents: {tools_list}
Decide which agent/tool to call and return only the agent name in JSON:
{{
  "agent": "price_agent"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt,
                config=GenerateContentConfig(response_mime_type="application/json")
            )

            response_json = json.loads(response.text)

            agent_name = response_json.get("agent")
            if agent_name:
                print(f"Calling agent: {agent_name}")
                final_output = self._call_agent_tool(agent_name)
            else:
                final_output = self._fallback_chat(user_input)

        except Exception as e:
            print("Router LLM failure, using fallback:", e)
            final_output = self._fallback_chat(user_input)

        return {
            "response": final_output
        }

    # optional — bỏ luôn nếu không cần lịch sử
    def get_history(self):
        return []
