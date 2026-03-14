# Spaces and Gradio — Code Examples

## Setup

```python
# pip install gradio transformers torch pillow

import gradio as gr
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
```

---

## Example 1: Minimal Gradio App — Sentiment Analysis

```python
import gradio as gr
from transformers import pipeline

# ✅ Load model ONCE at startup — not inside the function
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def analyze_sentiment(text):
    """Returns sentiment label and confidence."""
    if not text.strip():
        return "Please enter some text."
    result = classifier(text)[0]
    label = result['label']
    confidence = result['score']
    emoji = "😊" if label == "POSITIVE" else "😞"
    return f"{emoji} {label} — {confidence:.2%} confidence"

demo = gr.Interface(
    fn=analyze_sentiment,
    inputs=gr.Textbox(
        label="Enter text",
        placeholder="Type something here...",
        lines=3,
    ),
    outputs=gr.Textbox(label="Sentiment"),
    title="Sentiment Analyzer",
    description="Classifies text as positive or negative using DistilBERT.",
    examples=[
        ["I absolutely love this product! Best purchase I've ever made."],
        ["This was a complete waste of money. Terrible quality."],
        ["The weather today is okay, nothing special."],
    ],
    cache_examples=True,   # Pre-compute examples for instant loading
)

demo.launch()
# Open http://localhost:7860 in your browser
```

---

## Example 2: Multiple Inputs and Outputs

```python
import gradio as gr
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length, min_length):
    """Summarize text with configurable length."""
    if len(text.split()) < 50:
        return "Text too short to summarize (need at least 50 words).", ""

    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,
        truncation=True
    )[0]['summary_text']

    original_words = len(text.split())
    summary_words = len(summary.split())
    compression = (1 - summary_words/original_words) * 100

    return summary, f"Compression: {compression:.0f}% ({original_words} → {summary_words} words)"

demo = gr.Interface(
    fn=summarize_text,
    inputs=[
        gr.Textbox(label="Article text", lines=10, placeholder="Paste an article here..."),
        gr.Slider(30, 200, value=100, step=10, label="Max summary length (tokens)"),
        gr.Slider(10, 100, value=30, step=5, label="Min summary length (tokens)"),
    ],
    outputs=[
        gr.Textbox(label="Summary", lines=5),
        gr.Textbox(label="Stats"),
    ],
    title="Article Summarizer",
    description="Summarize long articles using BART.",
)

demo.launch()
```

---

## Example 3: Image Classification App

```python
import gradio as gr
from transformers import pipeline
from PIL import Image

# Load image classifier
image_clf = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)

def classify_image(image):
    """Classify an uploaded image."""
    if image is None:
        return {}

    # pipeline returns list of {label, score} dicts
    results = image_clf(image)

    # Return as dict for gr.Label component (shows confidence bars)
    return {r['label']: r['score'] for r in results[:5]}

demo = gr.Interface(
    fn=classify_image,
    inputs=gr.Image(type="pil", label="Upload an image"),
    outputs=gr.Label(num_top_classes=5, label="Predictions"),
    title="Image Classifier",
    description="Identifies objects in images using Vision Transformer (ViT).",
    examples=[
        # List of image paths for examples
        # ["path/to/cat.jpg"],
        # ["path/to/dog.jpg"],
    ],
)

demo.launch()
```

---

## Example 4: Multi-Tab App with gr.Blocks

```python
import gradio as gr
from transformers import pipeline

# Load models at startup
sentiment_clf = pipeline("sentiment-analysis",
                          model="distilbert-base-uncased-finetuned-sst-2-english")
ner_model = pipeline("token-classification",
                      model="dbmdz/bert-large-cased-finetuned-conll03-english",
                      aggregation_strategy="simple")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", truncation=True)

def analyze_sentiment(text):
    result = sentiment_clf(text)[0]
    return f"{result['label']} ({result['score']:.2%})"

def extract_entities(text):
    entities = ner_model(text)
    if not entities:
        return "No entities found."
    lines = [f"**{e['entity_group']}**: {e['word']} ({e['score']:.0%})" for e in entities]
    return "\n".join(lines)

def summarize(text, max_length):
    result = summarizer(text, max_length=max_length, min_length=20)[0]
    return result['summary_text']

# Build the multi-tab UI
with gr.Blocks(title="NLP Toolkit", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# NLP Toolkit — Multiple Tools in One App")

    with gr.Tab("Sentiment Analysis"):
        gr.Markdown("Classify the sentiment of any text.")
        with gr.Row():
            sa_input = gr.Textbox(label="Input text", lines=4, scale=3)
            sa_output = gr.Textbox(label="Sentiment", scale=1)
        sa_btn = gr.Button("Analyze Sentiment", variant="primary")
        sa_btn.click(fn=analyze_sentiment, inputs=sa_input, outputs=sa_output)
        gr.Examples(
            examples=["I love this!", "This is terrible."],
            inputs=sa_input, outputs=sa_output, fn=analyze_sentiment
        )

    with gr.Tab("Named Entity Recognition"):
        gr.Markdown("Extract people, organizations, and locations from text.")
        ner_input = gr.Textbox(
            label="Input text", lines=4,
            value="Apple CEO Tim Cook announced new products in Cupertino, California."
        )
        ner_output = gr.Markdown(label="Entities")
        ner_btn = gr.Button("Extract Entities", variant="primary")
        ner_btn.click(fn=extract_entities, inputs=ner_input, outputs=ner_output)

    with gr.Tab("Summarization"):
        gr.Markdown("Condense long text to a brief summary.")
        with gr.Row():
            sum_input = gr.Textbox(label="Article text", lines=10, scale=3)
            sum_output = gr.Textbox(label="Summary", lines=5, scale=2)
        max_len = gr.Slider(30, 200, value=100, step=10, label="Max length")
        sum_btn = gr.Button("Summarize", variant="primary")
        sum_btn.click(fn=summarize, inputs=[sum_input, max_len], outputs=sum_output)

demo.launch()
```

---

## Example 5: Chatbot with gr.ChatInterface

```python
import gradio as gr
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# For a real chatbot, load an instruction-tuned model
# Here we use gpt2 for demo purposes (replace with a better model)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
gen = pipeline("text-generation", model="gpt2", tokenizer=tokenizer,
               device=0 if torch.cuda.is_available() else -1)

def respond(message: str, history: list[list[str]]) -> str:
    """
    history: list of [user_message, assistant_message] pairs
    Returns: the assistant's next response (string)
    """
    # Build a simple conversation context
    context = ""
    for user_msg, assistant_msg in history[-3:]:  # Last 3 turns
        context += f"User: {user_msg}\nAssistant: {assistant_msg}\n"
    context += f"User: {message}\nAssistant:"

    output = gen(
        context,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
    )[0]['generated_text']

    # Extract only the new assistant response
    response = output[len(context):].split("User:")[0].strip()
    return response if response else "I'm not sure how to respond to that."

demo = gr.ChatInterface(
    fn=respond,
    title="AI Chat Demo",
    description="A simple chatbot demo using GPT-2. Replace with a better model for real use.",
    chatbot=gr.Chatbot(height=400, bubble_full_width=False),
    textbox=gr.Textbox(placeholder="Type your message here...", container=False),
    examples=["Tell me a fun fact.", "What is machine learning?"],
    retry_btn="Retry",
    undo_btn="Undo last",
    clear_btn="Clear conversation",
)

demo.launch()
```

---

## Example 6: Complete Space — app.py Ready for Deployment

```python
# app.py — Ready to push to Hugging Face Spaces
# requirements.txt: gradio>=4.0, transformers>=4.35, torch>=2.0

import gradio as gr
from transformers import pipeline
import torch
import os

# ── Model Loading ─────────────────────────────────────────────────
# Use environment variable or default — supports private models in Spaces
MODEL_ID = os.getenv("MODEL_ID", "distilbert-base-uncased-finetuned-sst-2-english")

print(f"Loading model: {MODEL_ID}")
classifier = pipeline(
    "text-classification",
    model=MODEL_ID,
    device=0 if torch.cuda.is_available() else -1,
)
print("Model loaded!")

# ── Inference Function ────────────────────────────────────────────
def predict(text: str, return_all_scores: bool = False):
    if not text.strip():
        return "Please enter some text."

    results = classifier(text, return_all_scores=return_all_scores)

    if return_all_scores:
        # Return dict for gr.Label (shows confidence bars for all classes)
        return {r['label']: r['score'] for r in results[0]}
    else:
        r = results[0]
        return f"{r['label']} ({r['score']:.1%})"

# ── UI ────────────────────────────────────────────────────────────
with gr.Blocks(
    title="Text Classifier",
    theme=gr.themes.Soft(),
    css=".gradio-container {max-width: 800px; margin: auto;}"
) as demo:
    gr.Markdown(f"""
    # Text Classifier
    Powered by `{MODEL_ID}` — classify text sentiment with confidence scores.
    """)

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Input text",
                placeholder="Enter any text to classify...",
                lines=4
            )
            all_scores = gr.Checkbox(label="Show all class scores", value=True)
            submit_btn = gr.Button("Classify", variant="primary", size="lg")

        with gr.Column(scale=1):
            output = gr.Label(label="Prediction", num_top_classes=3)

    submit_btn.click(
        fn=predict,
        inputs=[text_input, all_scores],
        outputs=output,
    )
    text_input.submit(  # Also trigger on Enter
        fn=predict,
        inputs=[text_input, all_scores],
        outputs=output,
    )

    gr.Examples(
        examples=[
            ["I absolutely love this product! Best purchase I've ever made.", True],
            ["This was a complete waste of money. Terrible quality.", True],
            ["The weather today is okay, nothing special.", True],
        ],
        inputs=[text_input, all_scores],
        outputs=output,
        fn=predict,
        cache_examples=True,
    )

    gr.Markdown("""
    ---
    **Model:** DistilBERT fine-tuned on SST-2 | **Task:** Sentiment Analysis
    """)

# ── Launch ────────────────────────────────────────────────────────
# Note: No share=True here — that's for local use only, not Spaces
if __name__ == "__main__":
    demo.launch()
```

**requirements.txt for this app:**
```
gradio>=4.7.0
transformers>=4.35.0
torch>=2.1.0
```

---

## Example 7: Real-Time Text Processing (onChange Events)

```python
import gradio as gr

def process_text(text):
    """Real-time text analysis as user types."""
    if not text:
        return 0, 0, 0, ""

    words = text.split()
    chars = len(text)
    sentences = text.count('.') + text.count('!') + text.count('?')
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)

    feedback = []
    if len(words) < 10:
        feedback.append("Too short — try adding more detail.")
    if avg_word_len > 8:
        feedback.append("Complex vocabulary detected.")
    if sentences == 0:
        feedback.append("No sentences detected — add punctuation.")
    if not feedback:
        feedback.append("Looks good!")

    return len(words), chars, sentences, " | ".join(feedback)

with gr.Blocks(title="Text Analyzer") as demo:
    gr.Markdown("# Live Text Analyzer — Updates as you type")

    text_input = gr.Textbox(
        label="Type your text here",
        lines=5,
        placeholder="Start typing and watch the stats update..."
    )

    with gr.Row():
        word_count = gr.Number(label="Words", interactive=False)
        char_count = gr.Number(label="Characters", interactive=False)
        sent_count = gr.Number(label="Sentences", interactive=False)

    feedback = gr.Textbox(label="Feedback", interactive=False)

    # Trigger on every keypress with .change()
    text_input.change(
        fn=process_text,
        inputs=text_input,
        outputs=[word_count, char_count, sent_count, feedback],
    )

demo.launch()
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Gradio and Spaces explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working Gradio apps (you are here) |

⬅️ **Prev:** [Inference Optimization](../06_Inference_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section README](../Readme.md)
