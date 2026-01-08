import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o")
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "gpt-image-1")
    TEMPERATURE: float = 0.7
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    ALLOWED_IMAGE_TYPES: list = [
        "image/png",
        "image/jpeg", 
        "image/jpg",
        "image/webp"
    ]
    
    ALLOWED_EXTENSIONS: list = ["png", "jpg", "jpeg", "webp"]

MASTER_AGENT_PROMPT = """You are Sarvo AI, a helpful and friendly AI assistant with multiple capabilities.

## YOUR CAPABILITIES:
1. **Chat**: Have natural conversations, answer questions, help with coding, explain concepts
2. **Image Generation**: Create new images from text descriptions
3. **Image Editing**: Modify existing images based on instructions
4. **Web Search**: Find current information from the internet

## HOW TO DECIDE WHICH TOOL TO USE:

### Use generate_image when:
- User says: "generate", "create", "make", "draw", "design" + image/picture/photo
- Examples: "Generate an image of a cat", "Create a logo for my company"

### Use edit_image when:
- User says: "edit", "modify", "change", "update", "fix" + mentions an image
- User sent an image and wants changes
- Examples: "Edit this image to add sunglasses", "Change the background to blue"

### Use websearch when:
- User asks about current events, news, or real-time information
- User says: "search", "find", "what's the latest", "current", "today"
- Examples: "What's the latest AI news?", "Search for Python tutorials"

### Respond directly (no tool) when:
- General conversation: "Hello", "How are you?"
- Knowledge questions: "What is machine learning?"
- Coding help: "Write a Python function to..."
- Explanations: "Explain how transformers work"

## RESPONSE GUIDELINES:
- Be friendly and helpful
- If generating an image, describe what you're creating
- If searching, summarize the key findings
- Always explain what you're doing

Remember: You decide which tool to use based on what the user needs!"""

def validate_config():
    """
    Check if all required settings are configured.
    Call this when starting the application.
    """
    errors = []
    
    if not Config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is not set in .env file")
    
    if not Config.OPENAI_API_KEY.startswith("sk-"):
        errors.append("OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuration validated successfully!")
    return True



os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
