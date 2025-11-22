from agri_chat import ChatBackend
from price_agent import PriceAgent
from recommend_agent import RecommendAgent
from demand_agent import DemandAgent

# Khởi tạo các agent
agents = {
    "price_agent": PriceAgent(),
    "recommend_agent": RecommendAgent(),
    "demand_agent": DemandAgent()
}

# Khởi tạo backend chat
chat_backend = ChatBackend(available_agents=agents, product_name="cam sành", region_name="Nghệ An")

# --- Chat lần đầu: hỏi giá ---
result1 = chat_backend.chat("Cho tôi biết giá thị trường của quả táo hiện tại")
session_id = result1["session_id"]
# print("Response 1:", result1["response"])

# --- Chat tiếp theo: hỏi vùng ---
result2 = chat_backend.chat("Tôi nên trồng gì ở Hà Tĩnh?", session_id=session_id)
print("Response 2:", result2["response"])

# --- Chat bình thường: câu hỏi chung chung ---
# result3 = chat_backend.chat("Dự đoán cung cầu cho cam sành ở Nghệ An", session_id=session_id)
# print("Response 3:", result3["response"])

# # --- Chat bình thường: câu hỏi chung chung ---
# result4 = chat_backend.chat("hello", session_id=session_id)
# print("Response 4:", result4["response"])

# --- Lịch sử chat ---
history = chat_backend.get_history(session_id)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
