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

class OllamaClient(BaseClient):
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL

    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or self.model
        url = f"{self.base_url}/generate"
        
        # Handle list input (text + image) for multimodal
        images = []
        actual_prompt = prompt
        
        if isinstance(prompt, list):
            # Assumes list is [text_prompt, image_input]
            # Simple handling for now - robust implementation would parse this better
            actual_prompt = ""
            for item in prompt:
                if isinstance(item, str):
                    actual_prompt += item + "\n"
                elif isinstance(item, Image.Image):
                    # Convert PIL image to base64
                    buffered = io.BytesIO()
                    item.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    images.append(img_str)
        
        data = {
            "model": model,
            "prompt": actual_prompt,
            "stream": False,
            "images": images
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama text generation error: {e}")
            return ""

    def generate_image(self, prompt: str, model: str = None) -> Optional[Image.Image]:
        print("Warning: Ollama client does not support image generation natively yet. Returning None.")
        return None

def get_client() -> BaseClient:
    if config.LLM_BACKEND == "ollama":
        return OllamaClient()
    return GeminiClient()

client_instance = get_client()
