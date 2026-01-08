from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
from strands import tool

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) 
#"Generate an image of gray tabby cat hugging an otter with an orange scarf"

@tool
async def image_generation_agent(input: str):
    response = client.responses.create(
        model="gpt-5",
        input=input,
        tools=[{"type": "image_generation"}],
    )

    # Save the image to a file
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
        
    if image_data:
        image_base64 = image_data[0]
        with open("otter.png", "wb") as f:
            f.write(base64.b64decode(image_base64))