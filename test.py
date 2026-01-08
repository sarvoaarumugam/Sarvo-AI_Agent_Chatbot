

import os
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator
from src.tools.websearch_tool import websearch
from src.agents.image_generating_agent import image_generation_agent

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
    system_prompt="you are helpfull assistand for me so you have to give correct answer and if it is websearch you have to use websearch or if user ask image generation then you have to do image generation",
    structured_output_model=AIOutput,
    tools=[websearch, image_generation_agent]
)
    
response = agent("hi can you do Generate an image of gray tabby cat hugging an otter with an orange scarf")
print(f"AI Response: {response}")


# @router.post("/agent-chat-bot")
# async def agent_chat_bot(request: UserInput):
#     print(f"start user input: {request.user_input}")
