# Paperbanana

Paperbanana is a simplified implementation of a multi-agent AI system designed to generate scientific diagrams from text descriptions. It orchestrates several specialized agents (Retriever, Planner, Stylist, Visualizer, Critic) to iteratively refine and generate high-quality visual outputs.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd paperbanana_ocal
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure you have `google-genai`, `Pillow`, `python-dotenv`, and `requests` installed)*

3.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

## Configuration & Supported Models

Paperbanana supports two backends: **Google Gemini** (default) and **Ollama** (for local models).

You can configure the backend using environment variables in your `.env` file or by exporting them in your shell.

### 1. Google Gemini (Default)

This is the recommended backend for the highest quality results, especially for image generation.

-   **Required Env Var:** `GOOGLE_API_KEY`
-   **Backend Setting:** `LLM_BACKEND="gemini"` (default)
-   **Recommended Models:**
    -   Text/Planning: `gemini-1.5-pro-latest` or `gemini-1.5-flash`
    -   Image Generation: `imagen-3.0-generate-001`

### 2. Ollama (Local)

Use this backend to run open-weights models locally.
**Note:** Image generation is currently mocked/not supported directly via Ollama in this implementation.

-   **Backend Setting:** `LLM_BACKEND="ollama"`
-   **Base URL:** `OLLAMA_BASE_URL="http://localhost:11434/v1"` (default)
-   **Model:** `OLLAMA_MODEL="llama3"` (default)

**Recommended Local Models:**
-   `llama3`: Good balance of speed and performance.
-   `mistral`: Strong alternative for reasoning.
-   `gemma`: Google's open weights model.

To run Ollama:
1.  Install Ollama from [ollama.com](https://ollama.com).
2.  Pull a model: `ollama pull llama3`.
3.  Start the server: `ollama serve`.

## Usage

### Basic Usage

Run the main script to generate a diagram from the default or hardcoded input:

```bash
python main.py
```

### Parallel Batch Execution

To process multiple requests in parallel, you can use the `generate_batch` method in your code:

```python
from paperbanana.pipeline import Pipeline

pipeline = Pipeline()
inputs = [
    "A diagram showing the structure of a neuron",
    "A flowchart of the photosynthesis process"
]
pipeline.generate_batch(inputs)
```

## Architecture

-   **Retriever:** Fetches relevant reference examples.
-   **Planner:** Creates a detailed textual description.
-   **Stylist:** Refines the description for aesthetic compliance (e.g., NeurIPS style).
-   **Visualizer:** Generates the image (currently via Imagen 3 on Gemini backend).
-   **Critic:** Reviews the generated image and provides improvement suggestions.
