from .client import client_instance
from .config import config
from PIL import Image
import io
import json

class Retriever:
    """Mock retriever that returns hardcoded examples."""
    def retrieve(self, query: str, k: int = 3):
        # In a real implementation, this would search a vector DB.
        # Here we return a static list of relevant examples.
        return [
            "Example 1: A diagram showing a transformer architecture with encoder and decoder stacks.",
            "Example 2: A flow chart depicting a multi-agent reinforcement learning process.",
            "Example 3: A scatter plot comparing the performance of 3 different models across 5 benchmarks."
        ]

class Planner:
    """Generates a detailed visual description based on the input and retrieved examples."""
    def plan(self, input_text: str, examples: list[str]) -> str:
        prompt = f"""
        You are an expert scientific illustrator.
        Based on the following input text and reference examples, create a detailed textual description for a scientific diagram.
        
        Input: {input_text}
        
        Examples:
        {chr(10).join(examples)}
        
        Detailed Description:
        """
        return client_instance.generate_text(prompt, model=config.VLM_MODEL)

class Stylist:
    """Refines the description to adhere to aesthetic guidelines."""
    def style(self, description: str) -> str:
        prompt = f"""
        You are a design expert. Refine the following diagram description to strictly follow NeurIPS style guidelines.
        Ensure clarity, professional color palette (avoiding saturated primaries), and legible typography.
        
        Description:
        {description}
        
        Refined Description:
        """
        return client_instance.generate_text(prompt, model=config.VLM_MODEL)

class Visualizer:
    """Generates an image from the description."""
    def visualize(self, description: str) -> Image.Image:
        # Using configured image model
        return client_instance.generate_image(description, model=config.IMAGE_MODEL)

class Critic:
    """Evaluates the generated image and provides feedback."""
    def critique(self, image: Image.Image, original_context: str, previous_description: str) -> dict:
        prompt_text = f"""
        You are a Lead Visual Designer. Critique this generated diagram based on the original context.
        
        Original Context:
        {original_context}
        
        Previous Description:
        {previous_description}
        
        Your task is to provide a critique and a REVISED description.
        
        Output stricly in JSON format:
        {{
            "critic_suggestions": "Detailed critique...",
            "revised_description": "The fully revised detailed description..."
        }}
        """
        
        # Pass text and image to client (multimodal request)
        # Note: client implementation handles list of inputs
        response_text = client_instance.generate_text([prompt_text, image], model=config.VLM_MODEL)
        
        try:
            # Clean up response if it contains markdown code blocks
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Error parsing critic JSON: {e}")
            return {"revised_description": previous_description, "critic_suggestions": "Error parsing response."}

