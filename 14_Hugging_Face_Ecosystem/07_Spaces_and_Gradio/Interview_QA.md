# Spaces and Gradio — Interview Q&A

## Beginner Level

**Q1: What is Gradio and what problem does it solve for ML practitioners?**

<details>
<summary>💡 Show Answer</summary>

**A:** Gradio is a Python library that converts any Python function into an interactive web application. You define the function signature (inputs and outputs), Gradio generates the UI automatically, and you get a working web app with text boxes, sliders, image uploaders, and more — with zero HTML, CSS, or JavaScript.

The problem it solves: sharing ML models with non-technical users, getting feedback from stakeholders, and demonstrating research without requiring anyone to install Python or run code locally. Before Gradio, showing a model demo to a product manager required either building a custom web app (weeks of work) or scheduling a screen share. With Gradio, you share a URL and they try it immediately in their browser.

It integrates naturally with the Hugging Face ecosystem — a `pipeline()` output can be wrapped in `gr.Interface` in about 5 lines of code.

</details>

---

**Q2: What is the difference between `gr.Interface` and `gr.Blocks`?**

<details>
<summary>💡 Show Answer</summary>

**A:** Both create Gradio web apps, but they offer different levels of control:

**`gr.Interface`** is the simple, opinionated approach. You provide a function, input components, and output components, and Gradio handles the layout automatically — inputs on the left, outputs on the right, Submit button in the middle. Perfect for single-function demos.

```python
demo = gr.Interface(fn=my_fn, inputs=gr.Textbox(), outputs=gr.Textbox())
```

**`gr.Blocks`** is the flexible, layout-first approach. You use `gr.Row`, `gr.Column`, and `gr.Tab` to arrange components exactly as you want. You manually wire up events with `.click()`, `.change()`, etc. Better for complex apps with tabs, multi-step pipelines, state, and custom interactions.

```python
with gr.Blocks() as demo:
    with gr.Tab("Analysis"):
        txt = gr.Textbox()
        btn = gr.Button("Run")
        out = gr.Textbox()
        btn.click(fn=analyze, inputs=txt, outputs=out)
```

Rule of thumb: start with `gr.Interface` for demos, graduate to `gr.Blocks` when you need a multi-tab app or complex layout.

</details>

---

**Q3: What is a Hugging Face Space and how do you deploy a Gradio app to one?**

<details>
<summary>💡 Show Answer</summary>

**A:** A Space is a Hugging Face-hosted repository that runs a web application — Gradio or Streamlit — and gives it a public URL at `huggingface.co/spaces/username/app-name`. It's free for CPU-based apps and provides paid GPU tiers for heavier models.

**Deployment is just a Git push:**

1. Create a new Space at huggingface.co/new-space, choose the Gradio SDK
2. Create `app.py` (your Gradio app code) and `requirements.txt` (dependencies)
3. Push to the Space's Git repository:
```bash
git clone https://huggingface.co/spaces/your-username/my-space
# Copy your app.py and requirements.txt into the cloned folder
git add app.py requirements.txt
git commit -m "Deploy app"
git push
```

The Space automatically builds and starts your app. When the build completes, your app is live at the Space URL. Any subsequent `git push` rebuilds the Space.

</details>

---

## Intermediate Level

**Q4: Why should model loading happen outside the inference function in a Gradio app? What happens if you don't?**

<details>
<summary>💡 Show Answer</summary>

**A:** If you load the model inside the inference function, it reloads on every user request. For a model like BERT (440MB), this means:
- Downloading from Hub or disk: 1-5 seconds per request
- Model initialization: 0.5-2 seconds per request
- GPU memory allocation and deallocation on every request

A 3-second overhead per request is catastrophic for user experience. For concurrent requests, it causes GPU memory fragmentation and potential OOM errors.

**The correct pattern:**
```python
import gradio as gr
from transformers import pipeline

# ✅ Load ONCE at module initialization — runs when the Space starts
classifier = pipeline("sentiment-analysis")

def predict(text):
    # ✅ Model already loaded — just call it
    return classifier(text)[0]['label']

demo = gr.Interface(fn=predict, inputs=gr.Textbox(), outputs=gr.Textbox())
demo.launch()
```

**The wrong pattern:**
```python
def predict(text):
    # ❌ Reloads model on EVERY request — extremely slow
    classifier = pipeline("sentiment-analysis")
    return classifier(text)[0]['label']
```

Module-level code in `app.py` runs once when the Space starts. Everything inside the function runs on every request. Keep slow operations (model loading, data loading) at the module level.

</details>

---

**Q5: How does `gr.State` work and when do you need it?**

<details>
<summary>💡 Show Answer</summary>

**A:** `gr.State` is a Gradio component that stores data between function calls for a single user session. It's invisible in the UI but acts as a persistent variable that survives across button clicks.

The most common use case is chatbot conversation history:

```python
import gradio as gr

def respond(message, history):
    """
    history is a list of [user_msg, assistant_msg] pairs.
    It's automatically maintained by gr.ChatInterface.
    """
    response = f"You said: {message}"
    return response

# gr.ChatInterface manages history state automatically
demo = gr.ChatInterface(fn=respond)
demo.launch()
```

For manual state management in `gr.Blocks`:

```python
def add_to_list(item, current_list):
    """current_list persists between button clicks."""
    current_list.append(item)
    return current_list, current_list  # Return new state + display update

with gr.Blocks() as demo:
    state = gr.State([])   # Initialize with empty list
    text_in = gr.Textbox(label="Add item")
    display = gr.JSON(label="Current list")
    btn = gr.Button("Add")
    btn.click(fn=add_to_list, inputs=[text_in, state], outputs=[state, display])
```

Without `gr.State`, you would need global variables (which break with concurrent users — all users would share the same history). `gr.State` gives each user session an isolated state.

</details>

---

**Q6: What are Gradio examples and why are they important for deployed Spaces?**

<details>
<summary>💡 Show Answer</summary>

**A:** Examples are pre-filled sample inputs that users can click to instantly populate the interface and see the model run. They're defined in `gr.Interface` with the `examples` parameter:

```python
demo = gr.Interface(
    fn=classify_text,
    inputs=gr.Textbox(label="Text"),
    outputs=gr.Label(label="Sentiment"),
    examples=[
        ["I absolutely love this product!"],
        ["This was a terrible experience."],
        ["The weather is fine today."],
    ],
    cache_examples=True,  # Pre-compute outputs so they appear instantly
)
```

**Why they matter for Spaces:**

1. **Reduce friction** — users don't have to think of their own inputs to try the demo; they can immediately see what the model does
2. **Load management** — `cache_examples=True` pre-computes example outputs at startup and caches them. This means example clicks don't hit the model at all — they return cached results instantly, reducing load on the Space
3. **First impressions** — a Space with 0 examples looks unfinished; examples with interesting inputs tell users what the model is good at
4. **Demo videos** — Spaces automatically generate a demo GIF by running through examples, shown on the Hub model card

For image/audio demos, examples are especially important since users may not have a suitable test file ready to upload.

</details>

---

## Advanced Level

**Q7: How would you build a Gradio app that lets users choose between multiple models and compare their outputs side by side?**

<details>
<summary>💡 Show Answer</summary>

**A:** This is a classic comparison demo pattern using `gr.Blocks` with multiple output columns:

```python
import gradio as gr
from transformers import pipeline

# Load multiple models at startup
models = {
    "DistilBERT": pipeline("sentiment-analysis",
                           model="distilbert-base-uncased-finetuned-sst-2-english"),
    "RoBERTa": pipeline("sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest"),
    "VADER": None,  # Could be a rule-based approach
}

def run_all_models(text):
    results = {}
    for name, model in models.items():
        if model is not None:
            result = model(text)[0]
            results[name] = f"{result['label']} ({result['score']:.2%})"
        else:
            results[name] = "Not available"
    return results["DistilBERT"], results["RoBERTa"]

with gr.Blocks(title="Model Comparison") as demo:
    gr.Markdown("# Sentiment Analysis — Model Comparison")
    gr.Markdown("Compare outputs from different models on the same input.")

    text_input = gr.Textbox(
        label="Input Text",
        placeholder="Enter text to analyze...",
        lines=3
    )
    btn = gr.Button("Compare All Models", variant="primary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### DistilBERT (SST-2)")
            out1 = gr.Textbox(label="Result", interactive=False)

        with gr.Column():
            gr.Markdown("### RoBERTa (Twitter)")
            out2 = gr.Textbox(label="Result", interactive=False)

    btn.click(fn=run_all_models, inputs=text_input, outputs=[out1, out2])

    gr.Examples(
        examples=["I love this!", "This is terrible.", "It was okay."],
        inputs=text_input,
        outputs=[out1, out2],
        fn=run_all_models,
        cache_examples=True,
    )

demo.launch()
```

</details>

---

**Q8: What are the differences between using Gradio and Streamlit for ML demos? When would you choose each?**

<details>
<summary>💡 Show Answer</summary>

**A:**

**Gradio:**
- **Execution model:** Reactive — you define functions and wire up events; the framework manages when things run
- **ML-specific components:** `gr.Chatbot`, `gr.Label` (confidence bars), `gr.AnnotatedImage` (bounding boxes), built-in examples cache
- **Interface style:** Declarative — `gr.Interface(fn=fn, inputs=..., outputs=...)` is 5 lines
- **Best for:** Model inference demos, research prototypes, single-function showcases, chatbots
- **Limitation:** Complex data dashboards with many interconnected charts are awkward to build

**Streamlit:**
- **Execution model:** Imperative top-to-bottom — the entire script reruns on every user interaction
- **Data components:** `st.dataframe`, `st.line_chart`, `st.map`, rich pandas/plotly integration
- **Interface style:** Script-like — write procedural code as if explaining to a reader
- **Best for:** Data dashboards, exploratory data analysis apps, apps with lots of charts and tables
- **Limitation:** The rerun-everything model can cause performance issues with expensive operations (use `@st.cache_resource` to mitigate)

**Decision:**
- Deploying a model demo → Gradio
- Building a data exploration dashboard → Streamlit
- Chatbot → Gradio (gr.ChatInterface is much simpler than building equivalent in Streamlit)
- Complex analytics with many charts → Streamlit

Both are fully supported on Hugging Face Spaces — create your Space with the appropriate SDK.

</details>

---

**Q9: How would you optimize a Gradio Space that's running too slowly on the free CPU tier?**

<details>
<summary>💡 Show Answer</summary>

**A:** The free CPU tier has no GPU and limited RAM (~16GB). Several optimization strategies:

**Strategy 1 — Model quantization for CPU:**
```python
# Use ONNX Runtime for 2-4× faster CPU inference
from optimum.onnxruntime import ORTModelForSequenceClassification
model = ORTModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english",
    from_transformers=True
)
```

**Strategy 2 — Smaller models:**
Use the smallest model that achieves acceptable quality:
- `distilbert` (66M) instead of `bert-base` (110M)
- `distilgpt2` (82M) instead of `gpt2` (117M)
- `facebook/mobilebert-uncased` (25M) for extreme CPU optimization

**Strategy 3 — Cache expensive results:**
```python
import gradio as gr
from functools import lru_cache

@lru_cache(maxsize=100)
def predict_cached(text):
    return classifier(text)[0]['label']

# For examples: use cache_examples=True in gr.Interface
```

**Strategy 4 — Lazy loading:**
If your Space has multiple models across tabs but users typically only use one:
```python
model_cache = {}

def get_model(model_name):
    if model_name not in model_cache:
        model_cache[model_name] = pipeline("...", model=model_name)
    return model_cache[model_name]
```

**Strategy 5 — Upgrade to GPU Space:**
For models that genuinely need GPU, a T4-Small Space tier (~$0.60/hour) provides a T4 GPU. Compare your demo's value vs the cost — for research demos, it's often worth it.

**Strategy 6 — Quantize to GGUF for CPU generation:**
For text generation demos, use a quantized GGUF model via llama-cpp-python — significantly faster than PyTorch for CPU-based autoregressive generation.

</details>

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Gradio and Spaces explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | Complete working Gradio apps |

⬅️ **Prev:** [Inference Optimization](../06_Inference_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section README](../Readme.md)
