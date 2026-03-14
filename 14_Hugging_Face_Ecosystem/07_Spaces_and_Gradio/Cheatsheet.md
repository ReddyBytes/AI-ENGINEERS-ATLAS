# Spaces and Gradio — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Gradio** | Python library that turns a function into a web UI |
| **Space** | Hugging Face-hosted URL for a live Gradio or Streamlit app |
| **gr.Interface** | Simple one-function wrapper: inputs → function → outputs |
| **gr.Blocks** | Full layout control with tabs, rows, columns, and custom event wiring |
| **gr.ChatInterface** | Built-in chat UI — pass a (message, history) → response function |
| **component** | A UI element: Textbox, Image, Audio, Slider, Dropdown, etc. |
| **demo.launch()** | Starts the Gradio server (locally or in a Space) |
| **share=True** | Creates a temporary 72-hour public URL (for local sharing only) |
| **app.py** | Required entry point filename for a Space |
| **requirements.txt** | Lists Python packages the Space must install at startup |

---

## Minimal Interface

```python
import gradio as gr

# Pattern: function + input components + output components
def my_fn(text):
    return text.upper()

demo = gr.Interface(
    fn=my_fn,
    inputs=gr.Textbox(label="Input"),
    outputs=gr.Textbox(label="Output"),
    title="My App",
    description="What this app does."
)

demo.launch()
```

---

## Input Components

```python
# Text
gr.Textbox(label="Text", lines=3, placeholder="Type here...")
gr.Textbox(label="Long text", max_lines=20, autoscroll=True)

# Numbers
gr.Slider(minimum=0, maximum=1, step=0.1, value=0.7, label="Temperature")
gr.Number(label="Max tokens", value=100, minimum=1, maximum=2048)

# Selection
gr.Dropdown(choices=["gpt2", "opt-125m", "distilgpt2"], label="Model", value="gpt2")
gr.Radio(choices=["Positive", "Negative"], label="Label")
gr.Checkbox(label="Enable sampling", value=True)
gr.CheckboxGroup(choices=["A", "B", "C"], label="Options")

# Media
gr.Image(type="pil", label="Upload Image")          # Returns PIL.Image
gr.Image(type="numpy", label="Upload Image")        # Returns numpy array
gr.Audio(type="filepath", label="Upload Audio")     # Returns path to file
gr.Video(label="Upload Video")
gr.File(label="Upload File", file_types=[".pdf", ".txt"])
```

---

## Output Components

```python
gr.Textbox(label="Result")
gr.Label(label="Classification", num_top_classes=3)  # Shows label+confidence bars
gr.Image(label="Output Image")
gr.Audio(label="Output Audio")
gr.Video(label="Output Video")
gr.JSON(label="Raw Output")
gr.Markdown()
gr.HTML()
gr.DataFrame(label="Results Table")
gr.Plot(label="Chart")        # For matplotlib/plotly figures
```

---

## gr.Blocks Layout System

```python
import gradio as gr

with gr.Blocks(title="My App", theme=gr.themes.Soft()) as demo:

    # Header
    gr.Markdown("# My AI Application")

    # Tabs
    with gr.Tab("Tab 1"):

        # Row: side-by-side
        with gr.Row():
            inp = gr.Textbox(label="Input", scale=2)   # scale controls width ratio
            out = gr.Textbox(label="Output", scale=2)

        # Column: stacked
        with gr.Column():
            slider = gr.Slider(0, 1, label="Temperature")
            btn = gr.Button("Run", variant="primary")  # "primary", "secondary", "stop"

    with gr.Tab("Tab 2"):
        gr.Markdown("Second tab content")

    # Events: button click, text change, etc.
    btn.click(
        fn=my_function,
        inputs=[inp, slider],
        outputs=out,
    )

    # Trigger on text change (real-time)
    inp.change(fn=my_function, inputs=[inp, slider], outputs=out)

demo.launch()
```

---

## Chatbot Pattern

```python
import gradio as gr
from transformers import pipeline

gen = pipeline("text-generation", model="gpt2")

def respond(message, history):
    """
    message: current user message (string)
    history: list of [user_msg, assistant_msg] pairs
    Returns: string (assistant response)
    """
    response = gen(message, max_new_tokens=100, do_sample=True)[0]['generated_text']
    return response[len(message):].strip()

demo = gr.ChatInterface(
    fn=respond,
    title="AI Chat",
    examples=["Hello!", "Tell me a fact about space."],
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
)
demo.launch()
```

---

## Space File Structure

```
my-space/
├── app.py           ← REQUIRED: entry point (must have demo.launch())
├── requirements.txt ← REQUIRED: one package per line
├── README.md        ← Optional: Space description
└── model/           ← Optional: local model files (avoid — use Hub instead)
```

**requirements.txt example:**
```
gradio>=4.0.0
transformers>=4.35.0
torch>=2.1.0
```

**app.py ending:**
```python
# Works locally AND in Spaces:
if __name__ == "__main__":
    demo.launch()
```

---

## Deploying to Spaces — CLI

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
cd YOUR_SPACE

# Add your files
cp /path/to/app.py .
cp /path/to/requirements.txt .

# Push
git add .
git commit -m "Initial app"
git push

# Your app is live at:
# https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
```

---

## When to Use gr.Interface vs gr.Blocks

| ✅ Use `gr.Interface` when | ✅ Use `gr.Blocks` when |
|--------------------------|------------------------|
| Single input → output function | Multiple function pipeline |
| Quick demo / prototype | Complex layout needed |
| You don't care about layout | Tabs, conditional visibility |
| Input examples are important | State management needed |
| — | Chatbot with history |

---

## Golden Rules

1. **Load models at the top level** (module scope), not inside the function — avoids reloading on every request.
2. **Never use `share=True` in a Space** — it creates a tunnel that conflicts with Spaces hosting.
3. **Always include `requirements.txt`** — without it, imports will fail in Spaces.
4. **Use `gr.State` for stateful components** (like conversation history) — don't use global variables.
5. **Keep Spaces apps lightweight** on the free CPU tier — use `pipeline` with small models or load with quantization.
6. **Pin package versions** in `requirements.txt` — Spaces builds are more stable with pinned versions.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Gradio and Spaces explanation |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Complete working Gradio apps |

⬅️ **Prev:** [Inference Optimization](../06_Inference_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section README](../Readme.md)
