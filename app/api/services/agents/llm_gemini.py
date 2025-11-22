import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Union
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from agno.models.response import ModelResponse


load_dotenv()
GOOGLE_API_KEY = os.getenv("LLM_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("LLM_API_KEY not found in environment variables. Please set it in your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)
model_name = 'gemini-2.5-flash'
model = genai.GenerativeModel(model_name)

# We create a custom LLM class that Agno/LangChain can use
class GeminiFlashLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "gemini-flash"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"

    def _get_api_key(self) -> str:
        return GOOGLE_API_KEY
    # Add the missing 'id' attribute
    @property
    def id(self) -> str:
        return model_name

    @property
    def provider(self) -> str:
        return "Google"
    
    @property
    def assistant_message_role(self) -> str:
        # In Gemini's conversational models, the assistant's role is typically 'model'.
        return "model"
    
    def get_instructions_for_model(self, tools: List[Any]) -> str:
        """
        Returns instructions for the model on how to use tools.
        """
        if not tools:
            return ""

        tool_instructions = "You have access to the following tools:\n"
        for tool in tools:
            tool_name = getattr(tool, 'name', str(tool))
            tool_desc = getattr(tool, 'description', 'No description available')
            tool_args = getattr(tool, 'args', getattr(tool, 'parameters', {}))
            
            tool_instructions += f"- **Tool Name:** {tool_name}\n"
            tool_instructions += f"  **Tool Description:** {tool_desc}\n"
            tool_instructions += f"  **Tool Schema:** {tool_args}\n"

        tool_instructions += (
            "\nWhen appropriate, you can call a tool by using the `Tool` function. "
            "You must include the tool's name and its parameters in the tool call. "
            "For example: `Tool(name='tool_name', parameters={'param1': 'value1'})`"
        )
        return tool_instructions

    def get_system_message_for_model(self, tools: List[Any]) -> str:
        """
        Generates a system message for the model, including tool instructions.
        """
        return self.get_instructions_for_model(tools)
    
    def response(self, messages, **kwargs) -> ModelResponse:
        """
        Processes messages and returns a ModelResponse object.
        """
        if not messages:
            return ModelResponse(
                content=""
            )

        if isinstance(messages, str):
            user_message_content = messages
        elif isinstance(messages, list):
            if not messages:
                user_message_content = ""
            elif hasattr(messages[-1], 'content'):
                user_message_content = messages[-1].content
            elif isinstance(messages[-1], dict):
                user_message_content = messages[-1].get('content', str(messages[-1]))
            else:
                user_message_content = str(messages[-1])
        else:
            user_message_content = str(messages)
        
        try:
            model_response = model.generate_content(user_message_content)
            response_text = model_response.text if model_response.text else ""
            
            return ModelResponse(
                content=response_text
            )
        except Exception as e:
            return ModelResponse(
                content=f"Error generating response: {e}"
            )
# This is the instance that you will import and use
llm = GeminiFlashLLM()