from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from src.agents.master_agent import get_master_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    type: str
    content: str
    image_url: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get the master agent
        agent = get_master_agent()
        
        # Process the message
        result = agent.process(
            user_input=request.message,
            image_url=request.image_url
        )
        
        return ChatResponse(
            type=result["type"],
            content=result["content"],
            image_url=result.get("image_url")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )