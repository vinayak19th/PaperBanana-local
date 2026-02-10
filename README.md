> Unofficial local implementation of [Dawei Zhu, undefined., et al, "PaperBanana: Automating Academic Illustration for AI Scientists," 2026.](https://arxiv.org/abs/2601.23265)

# Paperbanana
Codebase to generate scientific diagrams from text descriptions. 


**Disclaimer:** This project is for research purposes. Generated diagrams should be manually reviewed for scientific correctness.

## Setup

1.  **Clone the repository:**
    ```bash
    https://github.com/vinayak19th/PaperBanana-local.git
    cd PaperBanana-local
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

Paperbanana is highly configurable. You can choose different LLM backends (Gemini/Ollama) and output formats (Image/Draw.io).

### Interactive Configuration (Recommended)

The easiest way to configure Paperbanana is using the interactive configuration tool. It will prompt you for all necessary settings:

```bash
python configure.py
```

This tool allows you to:
- Set your **Google API Key**.
- Choose between **Gemini** and **Ollama** backends.
- Choose between **Image** (PNG) and **Draw.io** (Vector/XML) output.
- Configure specific **Ollama models** (Text, VLM, Image).
- Set the path to your **draw.io executable** (required for Draw.io mode).

Settings are saved to `config.json` and persist across runs.

### Backends

#### 1. Google Gemini (Default)
Recommended for highest quality. Requires a `GOOGLE_API_KEY`.
- **VLM Model:** default `gemini-3-pro-preview`
- **Image Model:** default `imagen-3.0-generate-001`

#### 2. Ollama (Local)
Run models locally via Ollama. 
- **OLLAMA_VLM_MODEL:** The single model used for all text reasoning (planning, styling) and vision tasks (critiquing). Example: `llava`.
- **OLLAMA_IMAGE_MODEL:** Experimental placeholders for image generation.

*Note: The agents now automatically use the globally configured model for the selected backend, simplifying per-agent model management.*

### Draw.io Generation

Paperbanana can generate editable `.drawio` XML files with LaTeX support. 
To use this:
1. Run `python configure.py`.
2. Set **Output Format** to `drawio`.
3. Provide the path to your Draw.io executable (e.g., `drawio-x86_64.AppImage` on Linux).

---


## Usage

### Basic Usage

```bash
python main.py -h                                                                   
usage: main.py [-h] --input INPUT [--caption CAPTION] --output OUTPUT [--iterations ITERATIONS]

PaperBanana: Automated Academic Illustration

options:
  -h, --help            show this help message and exit
  --input INPUT         Path to input text file containing methodology description.
  --caption CAPTION     Caption for the diagram.
  --output OUTPUT       Path to save the final output image.
  --iterations ITERATIONS
                        Number of refinement iterations.
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

Paperbanana follows a multi-agent pipeline:

-   **Retriever:** Fetches relevant reference examples to guide the style and content.
-   **Planner:** Creates a detailed textual description of the diagram.
-   **Stylist:** Refines the description for aesthetic compliance (e.g., NeurIPS style).
-   **Visualizer / SketchGenerator:** Generates the initial visual (Image or Prototype Sketch).
-   **DrawIOBuilder:** (Draw.io mode) Generates editable XML with LaTeX support.
-   **Renderer:** (Draw.io mode) Renders XML to image using local CLI for feedback.
-   **Critic / DiagramCritic:** Reviews the generated output and provides improvement suggestions.

