import json
import os
import requests
import sys
import argparse
from dotenv import load_dotenv


CONFIG_FILE = "config.json"
load_dotenv()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print(f"\n[SUCCESS] Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"\n[ERROR] Error saving config: {e}")

def get_input(prompt, default=None):
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{prompt}: ").strip()


def main():

    print("="*40)
    print("Paperbanana Configuration Tool")
    print("="*40)
    
    config = load_config()
    
    # 2. LLM Backend
    backend = get_input("Choose LLM Backend (gemini/open-web-ui)", config.get("LLM_BACKEND", "gemini"))
    assert backend in ["gemini", "open-web-ui"], "Backend must be 'gemini' or 'open-web-ui'"
    config["LLM_BACKEND"] = backend
    
    # 3. Output Format
    fmt = get_input("Choose Output Format (image/drawio)", config.get("OUTPUT_FORMAT", "image"))
    assert fmt in ["image", "drawio"], "Format must be 'image' or 'drawio'"
    config["OUTPUT_FORMAT"] = fmt
    
    # 4. Draw.io Path (if needed)
    if config["OUTPUT_FORMAT"] == "drawio":
        if(os.getenv("DRAWIO_PATH")==""):
            config["DRAWIO_PATH"] = get_input("Enter path to Draw.io executable (e.g. AppImage)", config.get("DRAWIO_PATH", ""))
        else:
            config["DRAWIO_PATH"] = os.getenv("DRAWIO_PATH")
        
    # 5. Open WebUI Specifics (if needed)
    if config["LLM_BACKEND"] == "open-web-ui":
        config["OPENWEBUI_BASE_URL"] = get_input("Open WebUI Base URL", config.get("OPENWEBUI_BASE_URL", "https://ai-lab.tail8befb3.ts.net/api"))
        config["OPENWEBUI_MODEL"] = get_input("Open WebUI Model", config.get("OPENWEBUI_MODEL", "gemma:12b"))
        config["OPENWEBUI_IMAGE_MODEL"] = get_input("Open WebUI Image Model", config.get("OPENWEBUI_IMAGE_MODEL", "flux-2-klein-4b"))
    
    # 6. General Models
    if config["LLM_BACKEND"] == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("\n[WARNING] GOOGLE_API_KEY not found in environment variables.")
            print("Please add it to your .env file or export it as an environment variable.")
            print("Example: GOOGLE_API_KEY=your_key_here")
        
        config["VLM_MODEL"] = get_input("Gemini VLM Model", config.get("VLM_MODEL", "gemini-3-pro-preview"))
        config["IMAGE_MODEL"] = get_input("Gemini Image Model", config.get("IMAGE_MODEL", "imagen-3.0-generate-001"))
    
    # Final Review
    print("\n" + "-"*40)
    print("Final Configuration:")
    print(json.dumps(config, indent=4))
    print("-"*40)
    
    confirm = input("\nSave this configuration? (y/n): ").lower()
    if confirm == 'y':
        save_config(config)
    else:
        print("Discarded changes.")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n[VALIDATION ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\nExiting...")

