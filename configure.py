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

def install_models():
    """Triggers model installation in LocalAI."""
    print("\n" + "="*40)
    print("LocalAI Model Installer")
    print("="*40)
    
    base_url = get_input("LocalAI Base URL", "http://localhost:8080")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]
        
    models_to_install = {
        "gemma-3-12b-it": "huggingface://bartowski/gemma-3-12b-it-GGUF/gemma-3-12b-it-Q4_K_M.gguf",
        "flux-2-klein": "huggingface://unsloth/FLUX.2-klein-4B-GGUF/FLUX.2-klein-4B-Q4_K_M.gguf"
    }
    
    print(f"\nAttempting to install: {', '.join(models_to_install.keys())}")
    print(f"Target: {base_url}/models/apply")
    
    for name, uri in models_to_install.items():
        print(f"\nInstalling {name}...")
        try:
            # Use /models/apply to install from a base configuration with a custom GGUF file
            payload = {
                "url": "github:mudler/LocalAI/gallery/base.yaml@master",
                "name": name,
                "files": [
                    {
                        "uri": uri,
                        "filename": f"{name}.gguf"
                    }
                ]
            }
            
            response = requests.post(f"{base_url}/models/apply", json=payload)
            if response.status_code == 200:
                job_id = response.json().get("uuid", "unknown")
                print(f"[SUCCESS] Installation job created for {name}. Job UUID: {job_id}")
                print(f"Check LocalAI logs for progress (docker logs paperbanana_localai).")
            else:
                print(f"[ERROR] Failed to trigger installation for {name}. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            print("Make sure LocalAI is running (docker-compose up -d).")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-models", action="store_true", help="Trigger installation of default models in LocalAI")
    args = parser.parse_args()
    
    if args.install_models:
        install_models()
        return

    print("="*40)
    print("Paperbanana Configuration Tool")
    print("="*40)
    
    config = load_config()
    
    # 2. LLM Backend
    backend = get_input("Choose LLM Backend (gemini/localai)", config.get("LLM_BACKEND", "gemini"))
    assert backend in ["gemini", "localai"], "Backend must be 'gemini' or 'localai'"
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
        
    # 5. LocalAI Specifics (if needed)
    if config["LLM_BACKEND"] == "localai":
        config["LOCALAI_BASE_URL"] = get_input("LocalAI Base URL", config.get("LOCALAI_BASE_URL", "http://localhost:8080/v1"))
        config["LOCALAI_MODEL"] = get_input("LocalAI Model (Text/VLM)", config.get("LOCALAI_MODEL", "gemma-3-12b-it"))
        config["LOCALAI_IMAGE_MODEL"] = get_input("LocalAI Image Model", config.get("LOCALAI_IMAGE_MODEL", "flux-2-klein"))
    
    # 6. General Models
    if config["LLM_BACKEND"] == "gemini":
        if(os.getenv("GOOGLE_API_KEY")==""):
            config["GOOGLE_API_KEY"] = get_input("Enter Google API Key", config.get("GOOGLE_API_KEY", ""))
        else:
            config["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
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

