# Spaces and Gradio

## The Story 📖

You built an amazing AI model that classifies medical images, translates 50 languages, or generates poetry. It works perfectly on your laptop. But it lives inside a Jupyter notebook that only you can run, with dependencies nobody else has installed, on hardware nobody else can access. Your model exists, but nobody can use it. Hugging Face Spaces combined with Gradio is like giving your model a website with a front door that anyone in the world can walk through — no installation, no Python knowledge required, just a URL.

👉 This is why we need **Spaces and Gradio** — they turn a Python function into a shareable, interactive web application in minutes.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[What is Gradio?](#what-is-gradio) · [What are Spaces?](#what-are-hugging-face-spaces) · [How It Works](#how-it-works--step-by-step)

**Should Learn** — important for real projects and interviews:
[gr.Interface vs gr.Blocks](#grinterface-vs-grblocks) · [Deploying to Spaces](#deploying-to-hugging-face-spaces) · [Common Mistakes](#common-mistakes-to-avoid-)

**Good to Know** — useful in specific situations, not needed daily:
[Gradio Components](#gradio-components-reference) · [ChatInterface](#building-a-chatbot-with-grchatinterface)

**Reference** — skim once, look up when needed:
[Streamlit Alternative](#streamlit--the-alternative)

---

## What is Gradio?

**Gradio** is a Python library that creates web interfaces for machine learning models. You write a Python function, you tell Gradio what the inputs and outputs are, and it builds the UI automatically.

Think of it as the difference between handing someone your Python code and saying "run this" vs handing them a polished app with buttons and text boxes. Same model, completely different user experience.

Gradio supports two interface styles:
- **`gr.Interface`** — simple, quick. Define input components, output components, and a function. Done.
- **`gr.Blocks`** — full layout control. Build complex multi-tab apps with custom arrangements, state, and event flows.

---

## What are Hugging Face Spaces?

**Spaces** is Hugging Face's free hosting platform for interactive ML demos. You push a Gradio (or Streamlit) app to a Space, and it becomes a live URL accessible to anyone in the world.

Think of Spaces as GitHub Pages but for AI demos:
- Free tier available (CPU-based)
- Paid tiers for GPU-powered Spaces
- Each Space is a Git repository (you push code just like GitHub)
- Your Space gets a URL: `huggingface.co/spaces/your-username/your-app`

---

## Why It Exists — The Problem It Solves

**Problem 1 — Sharing is hard.** Sharing an ML model traditionally required the recipient to install Python, install dependencies, download model weights, and run scripts. Most non-technical users (and many technical ones) can't do this. Gradio + Spaces makes sharing as simple as sending a URL.

**Problem 2 — Demos are expensive to build.** Building a proper web app for an ML model requires frontend skills (HTML/CSS/JavaScript), a backend server, deployment infrastructure — weeks of work. Gradio provides all of this in one Python function call.

**Problem 3 — Iteration is slow without real user feedback.** Researchers often only show their work via papers and GitHub repos. Spaces lets anyone immediately try a model, providing real usage feedback that papers can't capture.

---

## How It Works — Step by Step

```mermaid
flowchart TD
    A[Write a Python function] --> B[Define input/output types with Gradio]
    B --> C[gr.Interface or gr.Blocks wraps the function]
    C --> D{Where to run?}
    D -->|Locally| E[demo.launch() starts local server]
    D -->|Public| F[Push to HF Spaces repository]
    E --> G[localhost:7860]
    F --> H[Live at huggingface.co/spaces/username/app-name]
    G --> I[User enters input in browser]
    H --> I
    I --> J[Gradio sends input to your Python function]
    J --> K[Function returns output]
    K --> L[Gradio renders output in browser]
```

### Step 1 — Create a simple demo with `gr.Interface`

```python
import gradio as gr
from transformers import pipeline

# Load your model
classifier = pipeline("sentiment-analysis")

# Define the function you want to expose
def classify_sentiment(text):
    result = classifier(text)[0]
    return f"{result['label']} ({result['score']:.2%})"

# Wrap it in a Gradio interface
demo = gr.Interface(
    fn=classify_sentiment,          # Your function
    inputs=gr.Textbox(label="Enter text"),   # Input component
    outputs=gr.Textbox(label="Sentiment"),   # Output component
    title="Sentiment Analyzer",
    description="Enter any text to analyze its sentiment.",
)

demo.launch()  # Opens browser at http://localhost:7860
```

### Step 2 — Make it public

Share a temporary public URL (72-hour link):
```python
demo.launch(share=True)
# → Running on public URL: https://xxxx.gradio.live
```

For permanent hosting, deploy to Hugging Face Spaces.

---

## Gradio Components Reference

Gradio has input and output components for every media type:

| Component | Use for | Example |
|-----------|---------|---------|
| `gr.Textbox` | Text input/output | Prompt, generated text |
| `gr.Slider` | Numeric value (with range) | Temperature, max tokens |
| `gr.Dropdown` | Choose from a list | Model selection |
| `gr.Checkbox` | Boolean toggle | Enable feature |
| `gr.Image` | Upload/display images | Image classification, editing |
| `gr.Audio` | Upload/play audio | Speech recognition, TTS |
| `gr.Video` | Upload/play video | Video analysis |
| `gr.File` | Upload any file | PDF processing |
| `gr.DataFrame` | Tabular data | CSV analysis |
| `gr.Label` | Classification output (with confidences) | Multi-class results |
| `gr.Plot` | Charts (matplotlib, plotly) | Attention visualization |
| `gr.JSON` | Raw JSON display | Structured model output |
| `gr.Markdown` | Formatted text | Rich text output |
| `gr.Chatbot` | Multi-turn conversation display | Chatbot UI |

---

## gr.Interface vs gr.Blocks

### `gr.Interface` — Simple and Automatic

Best for: single-function demos with a clear input → output flow.

```python
demo = gr.Interface(
    fn=my_function,
    inputs=[gr.Textbox(), gr.Slider(0, 1, step=0.1)],
    outputs=gr.Textbox(),
    examples=[["Hello world", 0.7], ["Test text", 0.9]],  # Clickable examples
    flagging_mode="never",    # Disable the "flag" button
)
```

### `gr.Blocks` — Full Control

Best for: complex layouts, multi-step pipelines, tabs, state management, and chatbots.

```python
with gr.Blocks(title="My AI App", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# My AI Application")

    with gr.Tab("Text Analysis"):
        with gr.Row():
            input_text = gr.Textbox(label="Input", lines=5)
            output_text = gr.Textbox(label="Output", lines=5)
        btn = gr.Button("Analyze", variant="primary")
        btn.click(fn=analyze, inputs=input_text, outputs=output_text)

    with gr.Tab("Settings"):
        temperature = gr.Slider(0, 1, value=0.7, label="Temperature")
        model_choice = gr.Dropdown(["gpt2", "opt-125m"], label="Model")
```

---

## Deploying to Hugging Face Spaces

A Space is a Git repository with your app code. Three steps:

**Step 1 — Create the Space** at [huggingface.co/new-space](https://huggingface.co/new-space). Choose SDK: Gradio.

**Step 2 — Prepare your files:**

```
my-space/
├── app.py        ← Your Gradio app code (entry point)
├── requirements.txt  ← Python dependencies
└── README.md     ← Space description (optional)
```

**`app.py`** must end with `demo.launch()` (no `share=True` needed in Spaces).

**`requirements.txt`** example:
```
transformers>=4.35.0
torch>=2.0.0
gradio>=4.0.0
```

**Step 3 — Push to Hub:**
```bash
git clone https://huggingface.co/spaces/your-username/my-space
# Add your files
git add app.py requirements.txt
git commit -m "Add Gradio app"
git push
# Space builds automatically
```

Or use the Python API:
```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="app.py",
    path_in_repo="app.py",
    repo_id="your-username/my-space",
    repo_type="space"
)
```

---

## Building a Chatbot with gr.ChatInterface

For LLM-powered chatbots, Gradio has a purpose-built `gr.ChatInterface`:

```python
import gradio as gr
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

def respond(message, history):
    # history is a list of [user, assistant] message pairs
    response = generator(message, max_new_tokens=100)[0]['generated_text']
    return response.replace(message, "").strip()

demo = gr.ChatInterface(
    fn=respond,
    title="Chat with GPT-2",
    chatbot=gr.Chatbot(height=400),
    textbox=gr.Textbox(placeholder="Type a message..."),
    examples=["Tell me a joke", "What is AI?"],
)

demo.launch()
```

---

## Streamlit — The Alternative

Hugging Face Spaces also supports **Streamlit**, another popular Python web framework:

```python
# app.py
import streamlit as st
from transformers import pipeline

st.title("Sentiment Analyzer")
text = st.text_area("Enter text:")
if st.button("Analyze"):
    clf = pipeline("sentiment-analysis")
    result = clf(text)[0]
    st.write(f"**{result['label']}** — confidence: {result['score']:.2%}")
```

**Gradio vs Streamlit:**
- **Gradio:** Better for model demos, has ML-specific components (Chatbot, Label), runs as a function
- **Streamlit:** Better for data dashboards, more general-purpose, imperative execution model

For pure model demos, Gradio is usually simpler. For data applications with charts and tables, Streamlit is often more natural.

---

## Where You'll See This in Real AI Systems

- **Research demos** — virtually every AI paper with an interactive demo uses Hugging Face Spaces + Gradio. Stable Diffusion, Whisper, LLaMA demos all started this way.
- **Community evaluation** — product teams share internal demos via Spaces to get feedback from non-technical stakeholders
- **Educational tools** — university AI courses use Spaces for students to interact with models without any setup
- **Startup MVPs** — many AI startups build their initial product demo on Spaces before investing in custom infrastructure

---

## Common Mistakes to Avoid ⚠️

- **Not specifying `requirements.txt`** — without it, Spaces only has the default packages. Your model will fail to load with `ModuleNotFoundError`.
- **Loading model inside the function** — the function runs on every request; load the model at the top level (outside the function) so it loads once, not on every call.
- **Using `demo.launch(share=True)` in a Space** — `share=True` creates a Gradio tunnel, which doesn't work properly inside Spaces. Just use `demo.launch()`.
- **Hardcoding file paths** — Spaces uses a different directory structure; use relative paths or `Path(__file__).parent`.
- **Exceeding free tier limits** — the free CPU tier has limited RAM (~16GB) and no GPU. Large models need GPU Spaces (paid). Test with small models first.

---

## Connection to Other Concepts 🔗

- **Transformers library** (02_Transformers_Library) — the `pipeline()` you use inside Gradio apps
- **Hub** (01_Hub_and_Model_Cards) — Spaces are a Hub feature; models load from Hub inside the app
- **Inference optimization** (06_Inference_Optimization) — critical for Spaces with GPU tiers; quantize your model to reduce costs

---

✅ **What you just learned:** Gradio wraps any Python function into an interactive web UI with pre-built components, and Hugging Face Spaces provides free hosting — together making AI model sharing as easy as pushing code to a Git repository.

🔨 **Build this now:** Install Gradio (`pip install gradio`), load a sentiment analysis pipeline, wrap it in `gr.Interface` with a Textbox input and Textbox output, and run `demo.launch()`. Paste in some text and see it work in your browser.

➡️ **Next step:** You've completed Section 14 — the Hugging Face Ecosystem! Head back to the [Section README](../Readme.md) for a summary of what you've learned and suggested next sections.

---

## 🛠️ Practice Project

Apply what you just learned → **[I4: Custom LoRA Fine-Tuning](../../22_Capstone_Projects/09_Custom_LoRA_Fine_Tuning/03_GUIDE.md)**
> This project uses: building a gr.Interface for your fine-tuned model, deploying it to HF Spaces with a public URL

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| 📄 **Theory.md** | Gradio and Spaces overview (you are here) |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Gradio components quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Complete Gradio app examples |

⬅️ **Prev:** [Inference Optimization](../06_Inference_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section README](../Readme.md)
