import os
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator
from src.tools.websearch_tool import websearch

load_dotenv()
router = APIRouter()

api_key = os.getenv("OPENAI_API_KEY")
model = OpenAIModel(
    client_args={"api_key": api_key},
    model_id="gpt-5",
)

class UserInput(BaseModel):
    user_input: str

class AIOutput(BaseModel):
    ai_output: str

agent = Agent(
    model = model,
    system_prompt="you are helpfull assistand for me so you have to give correct answer",
    structured_output_model=AIOutput,
    tools=[websearch]
)
    
response = agent("hi can you do websearch and tell 2026 latest ai news")
print(f"AI Response: {response}")



