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

## Configuration Guide

Paperbanana is highly configurable, allowing you to balance diagram quality, execution speed, and privacy. The easiest way to configure the system is using the interactive tool:

```bash
python configure.py
```

### 1. LLM Backend
This choice determines which AI models will be used for reasoning, planning, and image generation.

| Backend | Best For | Requirement |
| :--- | :--- | :--- |
| **Google Gemini** | Highest quality, complex reasoning, and state-of-the-art image generation. | `GOOGLE_API_KEY` (set via `.env`) |
| **Google Gemini** | Highest quality, complex reasoning, and state-of-the-art image generation. | `GOOGLE_API_KEY` (set via `.env`) |
| **Open WebUI** | Privacy-focused, local execution, and avoiding API costs/limits. | Open WebUI instance (e.g., via Docker or Tailscale) |

> [!TIP]
> **Our Recommendation:** Use **Gemini** for the best scientific accuracy and aesthetic results. Use **Open WebUI** if you need to run entirely offline or have privacy constraints.

### 2. Output Format
This determines how the final diagram is produced.

*   **Image (PNG):** Directly generates a final raster image.
    *   *Pros:* Fast, easy to use, handles complex artistic styles.
    *   *Cons:* Not easily editable after generation.
*   **Draw.io (Vector/XML):** Generates an editable `.drawio` XML file.
    *   *Pros:* Fully editable, supports LaTeX for math formulas, resolution-independent (vector).
    *   *Cons:* Requires the Draw.io desktop app for rendering during refinement.

### 3. Backend Specifics

#### Open WebUI Integration
If you choose the `open-web-ui` backend, you will be prompted for:
- **Base URL:** The URL where your Open WebUI instance is reachable (default: `https://ai-lab.tail8befb3.ts.net/api`).
- **Text model:** The model for reasoning (e.g., `gemma:12b`).
- **Image Model:** The model for generating the visual sketch (e.g., `flux-2-klein-4b`).

#### Gemini Integration
- **VLM Model:** Default `gemini-3-pro-preview`.
- **Image Model:** Default `imagen-3.0-generate-001`.

> [!NOTE]
> Settings are saved to `config.json` and persist across runs. Environment-sensitive variables like `GOOGLE_API_KEY` should be placed in your `.env` file instead.


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

