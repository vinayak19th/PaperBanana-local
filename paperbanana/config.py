from dotenv import load_dotenv
import os
import json

load_dotenv()

class Config:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        # Load from config.json if exists
        config_path = "config.json"
        file_config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config.json: {e}")

        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", file_config.get("GOOGLE_API_KEY"))
        self.VLM_MODEL = os.getenv("VLM_MODEL", file_config.get("VLM_MODEL", "gemini-3-pro-latest")) # upgraded default for better reasoning
        self.IMAGE_MODEL = os.getenv("IMAGE_MODEL", file_config.get("IMAGE_MODEL", "imagen-3.0-generate-001"))
        
        # Paths
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", file_config.get("OUTPUT_DIR", "outputs"))
        
        # Pipeline settings
        self.DEFAULT_ITERATIONS = int(os.getenv("DEFAULT_ITERATIONS", file_config.get("DEFAULT_ITERATIONS", 3)))

        # LLM Backend
        self.LLM_BACKEND = os.getenv("LLM_BACKEND", file_config.get("LLM_BACKEND", "gemini")) # "gemini" or "ollama"
        
        # LocalAI settings
        self.LOCALAI_BASE_URL = os.getenv("LOCALAI_BASE_URL", file_config.get("LOCALAI_BASE_URL", "http://localhost:8080/v1"))
        self.LOCALAI_MODEL = os.getenv("LOCALAI_MODEL", file_config.get("LOCALAI_MODEL", "gemma-3-12b-it"))
        self.LOCALAI_IMAGE_MODEL = os.getenv("LOCALAI_IMAGE_MODEL", file_config.get("LOCALAI_IMAGE_MODEL", "flux-2-klein"))



        # Draw.io settings
        self.DRAWIO_PATH = os.getenv("DRAWIO_PATH", file_config.get("DRAWIO_PATH"))
        self.OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", file_config.get("OUTPUT_FORMAT", "image")) # "image" or "drawio"

config = Config()
