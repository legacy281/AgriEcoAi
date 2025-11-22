# agents/router_agent.py
import os
from agno.agent import Agent
from typing import List, Any
import json
from agno.tools import tool 
# from agno.models.google import Gemini
from agents.prompt import ROUTER_PROMPT
from agno.models.response import ModelResponse
from pydantic import BaseModel, Field
from agno.utils.log import logger
from agents.llm_gemini import llm
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class RouterAgent(Agent):
    name = "Router Agent"
    description = "Routes user queries to the appropriate agent based on the user's intent."
    
    def __init__(self, 
                 agents: List[Agent], 
                 product_name: str, 
                 user_request: str, 
                 region_name: str = "vietnam",
                 **kwargs):
        self.available_agents = {str(agent.name).replace(" ", "_").lower(): agent for agent in agents}
        self.user_request = user_request
        self.product_name = product_name
        self.region_name = region_name
        self.response = None
        # Correctly create a list of Agno-compatible tools from the agents
        tools = [self._create_tool_for_agent(agent) for agent in agents]
        
        super().__init__(
            model=llm,
            tools=tools, 
            instructions=[ROUTER_PROMPT],
            **kwargs
        )
    def _create_tool_for_agent(self, agent: Agent):
        agent_name = str(agent.name).replace(" ", "_").lower()
        tool_desc = f"Use this tool to route a message to the {agent.name}."
               
        def price_agent_tool():
            return self.available_agents['price_agent'].execute(
                self.product_name
            )

        def recommend_agent_tool():
            return self.available_agents['recommend_agent'].execute(
                self.region_name
            )
        def demand_agent_tool():
            return self.available_agents['demand_agent'].execute(
                self.product_name,
                self.region_name
            )
        
        if agent_name == "price_agent":
            return tool(
                name="price_agent_tool",
                description=tool_desc,
            )(price_agent_tool)
        elif agent_name == "recommend_agent_tool":
            return tool(
                name="recommend_agent_tool",
                description=tool_desc,
            )(recommend_agent_tool)
        elif agent_name == "demand_agent":
            return tool(
                name="demand_agent_tool",
                description=tool_desc,
            )(demand_agent_tool)
        else:
            print(f"Agent name provided {agent_name} for tool creation.")
            raise ValueError(f"Invalid agent name provided {agent_name} for tool creation.")

    def execute(self):
        full_query = f"User's Request: {self.user_request}"
        response = self.run(full_query)
        return response



# class RouterAgent(Agent):
#     name = "Router Agent"
#     description = "Routes user queries to the appropriate agent based on the user's intent."
    
#     def __init__(self, agents: List[Agent], 
#                  resume_content: str, 
#                  jd_content: str, 
#                  user_request: str, 
#                  **kwargs):
#         self.available_agents = {str(agent.name).replace(" ", "_").lower(): agent for agent in agents}
#         self.user_request = user_request
#         self.resume_content = resume_content
#         self.jd_content = jd_content
#         self.response = None
#         # Correctly create a list of Agno-compatible tools from the agents
#         tools = [self._create_tool_for_agent(agent) for agent in agents]
        
#         super().__init__(
#             model=llm,
#             tools=tools, 
#             instructions=[ROUTER_PROMPT],
#             **kwargs
#         )
        
#     def _create_tool_for_agent(self, agent: Agent):
#         agent_name = str(agent.name).replace(" ", "_").lower()
#         tool_desc = f"Use this tool to route a message to the {agent.name}."
        
#         # Define the Pydantic model for the tool's parameters
#         class RouteParams(BaseModel):
#             message: str = Field(..., description="The user's original message to be passed to the agent.")
        
#         # The tool's function needs to be a proper callable that the model can invoke.
#         # This function will handle the routing logic.
#         def route_to_agent_tool(agent_name) :
#             self.response = self.available_agents[agent_name].execute(self.resume_content, 
#                                                                       self.jd_content, 
#                                                                       self.user_request)
#             logger.info(f"Route to {agent_name} successful with response: {self.response}")
#             return self.response
        

#         return tool(
#             name=agent_name,
#             description=tool_desc,
#         )(route_to_agent_tool)

#     def execute(self) -> ModelResponse:
#         # full_query = f"{ROUTER_PROMPT}\n\nUser's Request: {self.user_request}"
#         full_query = f"{ROUTER_PROMPT}\n\nUser's Request: {self.user_request}"
#         # response_content = self.run(full_query)

#         # We now have the content from the executed agent.
#         return self.run(full_query)