from abc import ABC, abstractmethod
from typing import Optional, List
from google import genai
from google.genai import types
from PIL import Image
import io
import requests
import json
import base64
from .config import config

class BaseClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, model: str = None) -> str:
        pass

    @abstractmethod
    def generate_image(self, prompt: str, model: str = None) -> Optional[Image.Image]:
        pass

class GeminiClient(BaseClient):
    def __init__(self):
        self.client = genai.Client(api_key=config.GOOGLE_API_KEY)
        
    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or config.VLM_MODEL
        try:
             # Check if prompt contains image data (e.g. for critic)
            if isinstance(prompt, list):
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json" if "application/json" in str(prompt) else "text/plain"
                    )
                )
            else:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
            return response.text
        except Exception as e:
            print(f"Gemini text generation error: {e}")
            return ""

    def generate_image(self, prompt: str, model: str = None) -> Optional[Image.Image]:
        model = model or config.IMAGE_MODEL
        try:
            response = self.client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1
                )
            )
            image_bytes = response.generated_images[0].image.image_bytes
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            print(f"Gemini image generation error: {e}")
            return None
            
    # Keep for backward compatibility if needed, but we should migrate agents
    def get_client(self):
        return self.client

class LocalAIClient(BaseClient):
    def __init__(self):
        self.base_url = config.LOCALAI_BASE_URL
        self.model = config.LOCALAI_MODEL
        self.image_model = config.LOCALAI_IMAGE_MODEL

    def generate_text(self, prompt: str, model: str = None) -> str:
        url = f"{self.base_url}/chat/completions"
        selected_model = model or self.model
        
        messages = []
        
        if isinstance(prompt, str):
            messages.append({"role": "user", "content": prompt})
        elif isinstance(prompt, list):
            # Handle multimodal input (Text + Image)
            content = []
            for item in prompt:
                if isinstance(item, str):
                    content.append({"type": "text", "text": item})
                elif isinstance(item, Image.Image):
                    buffered = io.BytesIO()
                    item.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    content.append({
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{img_str}"}
                    })
            messages.append({"role": "user", "content": content})

        data = {
            "model": selected_model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LocalAI text generation error: {e}")
            if 'response' in locals():
                print(f"Response: {response.text}")
            return ""

    def generate_image(self, prompt: str, model: str = None) -> Optional[Image.Image]:
        url = f"{self.base_url}/images/generations"
        selected_model = model or self.image_model
        
        data = {
            "model": selected_model,
            "prompt": prompt,
            "n": 1,
            "size": "512x512" # Default, maybe configurable?
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            # OpenAI API returns url or b64_json
            # LocalAI typically matches OpenAI
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                img_data = data["data"][0]
                if "url" in img_data:
                    # Depending on setup, this URL might be local container URL.
                    # Ideally we want b64_json if possible, or we fetch the URL.
                    return Image.open(requests.get(img_data["url"], stream=True).raw)
                if "b64_json" in img_data:
                    return Image.open(io.BytesIO(base64.b64decode(img_data["b64_json"])))
            
            print(f"Unexpected image response format: {data}")
            return None
            
        except Exception as e:
            print(f"LocalAI image generation error: {e}")
            if 'response' in locals():
                print(f"Response: {response.text}")
            return None

def get_client() -> BaseClient:
    if config.LLM_BACKEND == "localai":
        return LocalAIClient()
    return GeminiClient()

client_instance = get_client()
