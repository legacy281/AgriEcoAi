import json
import uuid
from typing import Dict, List
import os
from google import genai
from google.genai.types import GenerateContentConfig
import dotenv

dotenv.load_dotenv()

API_KEY = os.environ.get("LLM_API_KEY")
client = genai.Client(api_key=API_KEY)


class ChatBackend:
    def __init__(self, available_agents, product_name: str, region_name: str = "vietnam", json_file="sessions.json"):
        self.available_agents = available_agents
        self.product_name = product_name
        self.region_name = region_name
        self.client = client
        self.llm_model = "gemini-2.5-flash"
        self.json_file = json_file

        # 🌟 Lưu session + lịch sử chat
        # { session_id: [ {user, agent, response}, ... ] }
        self.sessions: Dict[str, List[Dict]] = {}
        self.load_sessions()

    # ===================================================
    #   Lưu sessions ra JSON
    # ===================================================
    def save_sessions(self):
        with open(self.json_file, "w") as f:
            json.dump(self.sessions, f, indent=2)

    # ===================================================
    #   Load sessions từ JSON
    # ===================================================
    def load_sessions(self):
        try:
            with open(self.json_file, "r") as f:
                self.sessions = json.load(f)
        except FileNotFoundError:
            self.sessions = {}

    # ===================================================
    #   Tạo session mới
    # ===================================================
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        self.save_sessions()
        return session_id

    # ===================================================
    #   Gọi agent tool
    # ===================================================
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

    # ===================================================
    #   Fallback chat với LLM, dùng lịch sử session
    # ===================================================
    def _fallback_chat(self, user_input: str, session_id: str) -> str:
        history_text = ""
        history = self.sessions.get(session_id, [])
        for turn in history[-10:]:  # chỉ lấy 10 lượt gần nhất
            history_text += f"User: {turn['user']}\nAI: {turn['response']}\n"

        prompt = f"{history_text}User asked: {user_input}. Answer naturally."

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
    #   Chat theo session
    # ===================================================
    def chat(self, user_input: str, session_id: str) -> Dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        tools_list = ", ".join(self.available_agents.keys())
        prompt = f"""
You are an AI router. User asked: "{user_input}"
Available tools/agents: {tools_list}
Decide which agent/tool to call and return only the agent name in JSON:
{{"agent": "price_agent"}}
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
                final_output = self._call_agent_tool(agent_name)
            else:
                final_output = self._fallback_chat(user_input, session_id)

        except Exception as e:
            print("Router LLM failure, using fallback:", e)
            final_output = self._fallback_chat(user_input, session_id)

        # 🌟 Lưu vào lịch sử session
        self.sessions[session_id].append({
            "user": user_input,
            "agent": agent_name if agent_name else None,
            "response": final_output
        })
        self.save_sessions()  # lưu ngay ra file JSON

        return {"response": final_output, "session_id": session_id}

    # ===================================================
    #   Lấy lịch sử session
    # ===================================================
    def get_history(self, session_id: str):
        return self.sessions.get(session_id, [])
