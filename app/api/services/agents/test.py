# test_router_agent.py
from router_agent import RouterAgent
from agno.agent import Agent

# ===== Mock các agent cơ bản =====
class PriceAgentMock(Agent):
    name = "Price Agent"
    def execute(self, product_name):
        return {"price": f"{product_name} - 25000 đ/kg"}

class RecommendAgentMock(Agent):
    name = "Recommend Agent"
    def execute(self, region_name):
        return {"recommendation": f"Top products in {region_name}"}

class DemandAgentMock(Agent):
    name = "Demand Agent"
    def execute(self, product_name, region_name):
        return {"supply_demand": f"{product_name} demand in {region_name} is high"}

# ===== Khởi tạo RouterAgent =====
agents = [
    PriceAgentMock(),
    RecommendAgentMock(),
    DemandAgentMock()
]

user_request = "What is the current price of rice?"
product_name = "rice"
region_name = "Vietnam"

router_agent = RouterAgent(
    agents=agents,
    product_name=product_name,
    user_request=user_request,
    region_name=region_name
)

# ===== Chạy test =====
response = router_agent.execute()
print("RouterAgent response:", response)
