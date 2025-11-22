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
    def __init__(self, available_agents, json_file="sessions.json"):
        self.available_agents = available_agents
        self.client = client
        self.llm_model = "gemini-2.5-flash"
        self.json_file = json_file

        # Sessions: { session_id: [ {user, agent, response}, ... ] }
        self.sessions: Dict[str, List[Dict]] = {}
        self.load_sessions()

    # ===================================================
    #   Load & Save session
    # ===================================================
    def save_sessions(self):
        with open(self.json_file, "w") as f:
            json.dump(self.sessions, f, indent=2)

    def load_sessions(self):
        try:
            with open(self.json_file, "r") as f:
                self.sessions = json.load(f)
        except FileNotFoundError:
            self.sessions = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        self.save_sessions()
        return session_id

    # ===================================================
    #   AI extraction: Tự nhận biết sản phẩm & vùng miền
    # ===================================================
    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Trích xuất product + region từ câu hỏi.
        Ví dụ đầu ra:
        {
            "product": "gạo",
            "region": "long an"
        }
        """

        prompt = f"""
        Extract agricultural entities from this text:

        "{text}"

        Return JSON with:
        - product: main agriculture product mentioned
        - region: place/location mentioned (or "vietnam" if none)

        Example output:
        {{
            "product": "gạo",
            "region": "đồng bằng sông cửu long"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt,
                config=GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except:
            return {"product": "unknown", "region": "vietnam"}

    # ===================================================
    #   Gọi agent tool sau khi đã có product & region
    # ===================================================
    def _call_agent_tool(self, agent_name: str, product: str, region: str):
        agent_name = agent_name.lower()

        if agent_name == "price_agent":
            return self.available_agents['price_agent'].execute(product)

        elif agent_name == "recommend_agent":
            return self.available_agents['recommend_agent'].execute(region)

        elif agent_name == "demand_agent":
            return self.available_agents['demand_agent'].execute(product, region)

        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    # ===================================================
    #   Fallback LLM chat (giống ChatGPT thông thường)
    # ===================================================
    def _fallback_chat(self, user_input: str, session_id: str) -> str:
        history = self.sessions.get(session_id, [])
        history_text = ""

        for turn in history[-10:]:
            history_text += f"User: {turn['user']}\nAI: {turn['response']}\n"

        prompt = f"{history_text}User asked: {user_input}. Answer naturally."

        try:
            res = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt,
                config=GenerateContentConfig(response_mime_type="text/plain")
            )
            return res.text
        except Exception as e:
            return f"❌ Fallback LLM error: {e}"

    # ===================================================
    #   MAIN CHAT FUNCTION
    # ===================================================
    def chat(self, user_input: str, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # ------------------------------------
        # 1️⃣ Tự động nhận biết product & region
        # ------------------------------------
        entities = self.extract_entities(user_input)
        product = entities.get("product", "unknown")
        region = entities.get("region", "vietnam")

        # ------------------------------------
        # 2️⃣ Router LLM chọn agent
        # ------------------------------------
        tools_list = ", ".join(self.available_agents.keys())

        router_prompt = f"""
        User asked: "{user_input}"

        Available agents: {tools_list}

        Choose exactly 1 agent that best handles the request.
        Return JSON only.
        Example:
        {{"agent": "price_agent"}}
        """

        try:
            router_response = self.client.models.generate_content(
                model=self.llm_model,
                contents=router_prompt,
                config=GenerateContentConfig(response_mime_type="application/json")
            )

            router_json = json.loads(router_response.text)
            agent_name = router_json.get("agent")

            # ---------------------
            # 3️⃣ Gọi đúng agent
            # ---------------------
            if agent_name:
                print("Calling agent:", agent_name, "with product:", product, "and region:", region)
                final_output = self._call_agent_tool(agent_name, product, region)
            else:
                final_output = self._fallback_chat(user_input, session_id)

        except Exception as e:
            print("Router failed:", e)
            final_output = self._fallback_chat(user_input, session_id)
            agent_name = None

        # ------------------------------------
        # 4️⃣ Lưu lịch sử
        # ------------------------------------
        self.sessions[session_id].append({
            "user": user_input,
            "product": product,
            "region": region,
            "agent": agent_name,
            "response": final_output
        })

        self.save_sessions()

        return {
            "session_id": session_id,
            "product": product,
            "region": region,
            "agent": agent_name,
            "response": final_output
        }

    # ===================================================
    #   Get lịch sử session
    # ===================================================
    def get_history(self, session_id: str):
        return self.sessions.get(session_id, [])
