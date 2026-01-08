import os
import re
from typing import Optional
from strands import Agent
from strands.models.openai import OpenAIModel
from src.agents.config import Config, MASTER_AGENT_PROMPT
from src.tools.websearch_tool import websearch
from src.tools.image_generator import generate_image
from src.tools.image_editor import edit_image


class MasterAgent:

    def __init__(self):
        print("Initializing Sarvo AI Master Agent")

        self.model = OpenAIModel(
            client_args = {"api_key": Config.OPENAI_API_KEY},
            model_id = Config.CHAT_MODEL,
        )

        self.agent = Agent(
            model = self.model,
            system_prompt = MASTER_AGENT_PROMPT,
            tools = [websearch, generate_image, edit_image]
        
        )

        self._history = []

        self._curreent_image_url = None

        print("Master Agent Initialized successfully")

    def set_current_image(self, image_url: str):
        self._curreent_image_url = image_url
        print(f"Current Image set to :{image_url}")

    def process(self, user_input: str, image_url: Optional[str] = None) ->dict:
        try:
            full_input = user_input

            if image_url:
                self._curreent_image_url = image_url
                full_input = f"{user_input}\n\n[User has provided an image : {image_url}]"
            elif self._curreent_image_url:
                edit_keywords = ["edit", "modify", "change", "update", "fix", "add", "remove"]
                if any(kw in user_input.lower() for kw in edit_keywords):
                    full_input = f"{user_input}\n\n[Priviously uploaded image : {self._curreent_image_url}]"
            
            print(f"User Input : {user_input}")

            response = self.agent(full_input)

            response_text = str(response)

            print(f"Agent Response: {response_text}")

            result = self._parse_response(response_text)

            
            self._history.append({
                "role":"User",
                "content": user_input
            })

            self._history.append({
                "role":"User",
                "content": result["content"]
            })

            return result
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            print(f"❌ Error: {error_msg}")
            return {
                "type": "text",
                "content": error_msg,
                "image_url": None
            }
        
    def _parse_response(self, response_text: str)-> dict:
        image_match = re.search(r'\[IMAGE_PATH:([^\]]+)\]', response_text)
        

        if image_match:
            image_path = image_match.group(1)

            clean_text = re.sub(r'\[IMAGE_PATH:[^\]]+\]', '', response_text).strip()
            
            filename = os.path.basename(image_path)

            return{
                "type":"image",
                "content":clean_text or "Here is your image",
                "image_url": f"/outputs/{filename}"
            }
        
        markdown_match = re.search(r'sandbox:/outputs/([a-zA-Z0-9_\-\.]+)', response_text)
        if markdown_match:
            filename = markdown_match.group(1)

            # Remove markdown image block
            clean_text = re.sub(r'!\[.*?\]\(sandbox:/outputs/.*?\)', '', response_text).strip()

            return {
                "type": "image",
                "content": clean_text or "Here is your image",
                "image_url": f"/outputs/{filename}"
            }        
    
        return{
            "type": "text",
            "content": response_text,
            "image_url": None
        }
    
_master_agent_instance = None

def get_master_agent()->MasterAgent:
    global _master_agent_instance

    if _master_agent_instance is None:
        _master_agent_instance = MasterAgent()

    return _master_agent_instance