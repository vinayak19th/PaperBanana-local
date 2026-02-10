from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    VLM_MODEL = "gemini-3.0-flash"
    IMAGE_MODEL = "imagen-3.0-generate-001"
    
    # Paths
    OUTPUT_DIR = "outputs"
    
    # Pipeline settings
    DEFAULT_ITERATIONS = 3

    # LLM Backend
    LLM_BACKEND = os.getenv("LLM_BACKEND", "gemini") # "gemini" or "ollama"
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    
config = Config()
