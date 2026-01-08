import os 
import base64
import uuid
from datetime import datetime
from strands import tool
from openai import OpenAI
from src.agents.config import Config

# from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


client = OpenAI(api_key=Config.OPENAI_API_KEY)

@tool
def generate_image(prompt: str, size: str = "1024x1024", quality: str = "high")-> str:
    """
    Generate a NEW image from a text description.
    
    Use this tool when the user wants to CREATE a new image from scratch.
    
    Trigger words: "generate", "create", "make", "draw", "design" + image/picture/photo
    
    Args:
        prompt: Detailed description of what to create.
                Be SPECIFIC about:
                - Subject: What's in the image
                - Style: Realistic, cartoon, oil painting, etc.
                - Colors: Color scheme or specific colors
                - Mood: Happy, dark, peaceful, etc.
                - Composition: Close-up, wide shot, etc.
                
                Example: "A golden retriever puppy playing in autumn leaves, 
                         realistic photography style, warm orange colors, 
                         joyful mood, close-up shot"
        
        size: Image dimensions. Options:
              - "1024x1024" (square, default)
              - "1536x1024" (landscape/wide)
              - "1024x1536" (portrait/tall)
              - "auto" (let model decide)
        
        quality: Image quality level:
                - "low" - Fastest, cheapest (~$0.02)
                - "medium" - Balanced (~$0.07)
                - "high" - Best quality (~$0.19, default)
    
    Returns:
        Success: Path to generated image file
        Failure: Error message explaining what went wrong
    
    Examples:
        generate_image("A cute cat wearing a tiny hat, cartoon style")
        generate_image("Modern minimalist logo for a tech startup called 'Nova'")
        generate_image("Sunset over mountains, oil painting style", size="1536x1024")
    """

    try:
        print(f"Generating image: {prompt}")

        response = client.images.generate(
            model=Config.IMAGE_MODEL,
            prompt=prompt,
            n=1,
            size=size,
            quality=quality
            
        )

        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"generated_{timestamp}_{unique_id}.png"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
       
       
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        print(f"✅ Image saved to: {filepath}")
        
        # Return success message with special marker
        # The [IMAGE_PATH:...] marker helps the system identify the image location
        return f"Image generated successfully! The image shows: {prompt[:100]}... [IMAGE_PATH:{filepath}]"
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Image generation failed: {error_msg}")
        
        # Provide helpful error messages
        if "rate_limit" in error_msg.lower():
            return "Image generation failed: Rate limit reached. Please wait a moment and try again."
        elif "content_policy" in error_msg.lower():
            return "Image generation failed: The request was blocked by content policy. Please try a different prompt."
        elif "invalid_api_key" in error_msg.lower():
            return "Image generation failed: Invalid API key. Please check your OpenAI API key."
        else:
            return f"Image generation failed: {error_msg}"
