import os
import base64
import uuid
import requests
from datetime import datetime
from strands import tool
from openai import OpenAI
from PIL import Image
import io
from src.agents.config import Config

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

@tool
def edit_image(
    image_url: str,
    edit_instructions: str,
    mask_path: str = None
) -> str:
    """
    Edit an EXISTING image based on text instructions.
    
    Use this tool when the user wants to MODIFY an existing image.
    The user must have uploaded an image first.
    
    Trigger words: "edit", "modify", "change", "update", "fix", "add to", "remove from"
    
    Args:
        image_path: Path to the image file to edit.
                   This comes from the /upload endpoint.
                   Example: "uploads/abc123.png"
        
        edit_instructions: What changes to make.
                          Be SPECIFIC about:
                          - What to change
                          - How to change it
                          - What to keep the same
                          
                          Good: "Add red sunglasses to the person's face"
                          Bad: "Make it better"
        
        mask_path: Optional path to a mask image.
                  - White areas = will be edited
                  - Black areas = will be preserved
                  - If not provided, AI auto-detects what to change
    
    Returns:
        Success: Path to the edited image file
        Failure: Error message explaining what went wrong
    
    Examples:
        edit_image("uploads/photo.png", "Add a santa hat to the person")
        edit_image("uploads/room.png", "Change the wall color to blue")
        edit_image("uploads/logo.png", "Make the background transparent")
    """
    try:
        print(f"✏️ Editing image: {image_url}")
        print(f"   Instructions: {edit_instructions[:50]}...")
        
        # Validate image exists
        if not image_url:
            return "Error: Image URL not provided."

        # ✅ FIX: Download image URL into bytes
        image_file = download_image_from_url(image_url)
        
        # Read and prepare the image
        
        
        # Build the edit request
        edit_params = {
            "model": Config.IMAGE_MODEL,
            "image": ("image.png", image_file, "image/png"),
            "prompt": edit_instructions,
            "n": 1,
            "size": "1024x1024",
         
        }

        # Call OpenAI Image Edit API
        response = client.images.edit(**edit_params)
        
        # Extract the edited image
        edited_base64 = response.data[0].b64_json
        
        # Generate output filename (preserve original name + add "_edited")
        original_name = os.path.splitext(os.path.basename(image_url))[0]
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{original_name}_edited_{timestamp}.png"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        # Save edited image
        image_bytes = base64.b64decode(edited_base64)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        print(f"✅ Edited image saved to: {filepath}")
        
        return f"Image edited successfully! Changes made: {edit_instructions[:100]}... [IMAGE_PATH:{filepath}]"
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Image editing failed: {error_msg}")
        
        if "rate_limit" in error_msg.lower():
            return "Image editing failed: Rate limit reached. Please wait a moment and try again."
        elif "content_policy" in error_msg.lower():
            return "Image editing failed: The edit request was blocked by content policy."
        elif "invalid" in error_msg.lower() and "image" in error_msg.lower():
            return "Image editing failed: The image format is not supported. Please use PNG, JPG, or WEBP."
        else:
            return f"Image editing failed: {error_msg}"


def download_image_from_url(image_url: str) -> io.BytesIO:
    """
    Download an image from a public URL and return it as BytesIO (PNG).
    """
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    img = Image.open(io.BytesIO(response.content))

    # Convert to RGBA PNG (OpenAI friendly)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

def prepare_image_for_edit(image_path: str) -> bytes:
    """
    Prepare an image file for the OpenAI edit API.
    
    OpenAI requires:
    - PNG format
    - Less than 4MB (for DALL-E 2) or 50MB (for gpt-image-1)
    - Square images work best
    
    This function handles conversion if needed.
    """
    # Open the image with PIL
    with Image.open(image_path) as img:
        # Convert to RGBA (PNG format with transparency support)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Resize if too large (optional, for faster processing)
        max_size = 2048
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save to bytes buffer as PNG
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer.read()


def create_mask_from_selection(
    image_path: str,
    x: int, y: int,
    width: int, height: int
) -> str:
    """
    Create a mask image for selective editing.
    
    This creates a black image with a white rectangle
    where you want edits to happen.
    
    Args:
        image_path: Original image path (to get dimensions)
        x, y: Top-left corner of edit area
        width, height: Size of edit area
    
    Returns:
        Path to the created mask file
    """
    # Open original to get dimensions
    with Image.open(image_path) as img:
        original_size = img.size
    
    # Create black image (areas to preserve)
    mask = Image.new("RGBA", original_size, (0, 0, 0, 255))
    
    # Draw white rectangle (area to edit)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rectangle([x, y, x + width, y + height], fill=(255, 255, 255, 255))
    
    # Save mask
    mask_path = os.path.join(Config.OUTPUT_DIR, f"mask_{uuid.uuid4().hex[:8]}.png")
    mask.save(mask_path)
    
    return mask_path