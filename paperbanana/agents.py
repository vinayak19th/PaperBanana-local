from .client import client_instance
from .config import config
from PIL import Image
import io
import json
import subprocess
import os

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
        return client_instance.generate_text(prompt)

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
        return client_instance.generate_text(prompt)

class Visualizer:
    """Generates an image from the description."""
    def visualize(self, description: str) -> Image.Image:
        # Using configured image model
        return client_instance.generate_image(description)


class SketchGenerator:
    """Generates a rough prototype sketch to guide the final diagram creation."""
    def sketch(self, description: str) -> Image.Image:
        prompt = f"""
        Create a rough, low-fidelity prototype sketch for the following scientific diagram.
        Focus on layout, composition, and relative positioning of elements.
        Do not worry about fine details or text legibility.
        
        Description:
        {description}
        """
        # Using configured image model
        return client_instance.generate_image(prompt)

class DrawIOBuilder:
    """Generates Draw.io XML based on the refined description and sketch critique."""
    def build(self, description: str, critique_suggestions: str = None) -> str:
        prompt = f"""
        You are an expert in creating Draw.io (mxGraph) XML diagrams.
        Your task is to generate the XML code for a scientific diagram based on the description below.
        
        Description:
        {description}
        
        {f"Critique Suggestions to Incorporate: {critique_suggestions}" if critique_suggestions else ""}
        
        Requirements:
        1. Use standard mxGraph XML format.
        2. For any text containing math or equations, use LaTeX syntax (e.g., $$x^2$$ or \( \alpha \)).
        3. Ensure the diagram is well-laid out and readable.
        4. Output ONLY the raw XML code. Do not include markdown code blocks (e.g., ```xml).
        """
        
        response = client_instance.generate_text(prompt)
        
        # Clean up response if it contains markdown code blocks
        clean_xml = response.replace('```xml', '').replace('```', '').strip()
        return clean_xml

class Renderer:
    """Handles rendering of Draw.io XML to images using the local Draw.io CLI."""
    def render(self, xml_path: str, output_path: str) -> bool:
        
        drawio_path = config.DRAWIO_PATH
        if not drawio_path or not os.path.exists(drawio_path):
            print("Error: DRAWIO_PATH not configured or executable not found.")
            return False
            
        # Command: {DRAWIO_PATH} -x -f png -o {output_path} {xml_path}
        # -x: Export
        # -f png: Format PNG
        # --crop: Crop to content (optional but good)
        cmd = [drawio_path, "-x", "-f", "png", "--crop", "-o", output_path, xml_path]
        
        try:
            # Setting environment for headless run if needed (e.g. xvfb-run)
            # For now assuming AppImage works directly or user has set up environment
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error rendering Draw.io XML: {e}")
            print(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error during rendering: {e}")
            return False

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
        response_text = client_instance.generate_text([prompt_text, image])
        
        try:
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Error parsing critic JSON: {e}")
            return {"revised_description": previous_description, "critic_suggestions": "Error parsing response."}

class DiagramCritic:
    """Specialized critic for reviewing rendered Draw.io diagrams."""
    def critique(self, image: Image.Image, original_context: str) -> str:
        prompt_text = f"""
        You are a Technical Editor. Review this rendered Draw.io diagram.
        
        Original Context:
        {original_context}
        
        Check for:
        1. Correct rendering of LaTeX equations.
        2. Alignment and layout issues.
        3. Readability of text and connections.
        
        Provide a concise list of specific changes needed to improve the diagram XML.
        If the diagram is perfect, say "No changes needed."
        
        Output format: Plain text list of suggestions.
        """
        
        return client_instance.generate_text([prompt_text, image])


