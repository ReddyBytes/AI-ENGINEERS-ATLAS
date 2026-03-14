# Complete Pipeline Guide — Transformers Library

Every task in the `pipeline()` function, explained with a working example and the key parameters you need to know.

---

## How to Use This Guide

```python
from transformers import pipeline

# Basic pattern for every pipeline:
pipe = pipeline(task, model="model-id", device=0)  # device=0 for GPU
result = pipe(input_data, **task_specific_params)
```

Set `device=0` to use your first GPU, `device=-1` (default) for CPU.

---

## 1. Text Classification / Sentiment Analysis

**Use for:** Binary or multi-class text labeling — sentiment, spam detection, topic classification, toxicity detection.

```python
clf = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Single input
print(clf("This hotel was absolutely fantastic!"))
# → [{'label': 'POSITIVE', 'score': 0.9998}]

# Batch input
results = clf(["Great!", "Terrible!", "Okay..."])
# → [{'label': 'POSITIVE', ...}, {'label': 'NEGATIVE', ...}, {'label': 'POSITIVE', ...}]

# Get ALL class probabilities (not just the top one)
print(clf("Great!", return_all_scores=True))
# → [[{'label': 'NEGATIVE', 'score': 0.0002}, {'label': 'POSITIVE', 'score': 0.9998}]]
```

**Recommended models:**
- `distilbert-base-uncased-finetuned-sst-2-english` — fast, good for English sentiment
- `cardiffnlp/twitter-roberta-base-sentiment-latest` — trained on Twitter
- `j-hartmann/emotion-english-distilroberta-base` — 7 emotions (joy, sadness, etc.)

---

## 2. Token Classification (Named Entity Recognition)

**Use for:** Identifying and labeling spans of text — names, locations, organizations, dates, medical terms.

```python
ner = pipeline(
    "token-classification",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple"  # Merge B-/I- tags into complete entities
)

result = ner("Marie Curie was born in Warsaw, Poland in 1867.")
for entity in result:
    print(f"{entity['entity_group']:6s} | {entity['word']:15s} | {entity['score']:.2%}")
# PER    | Marie Curie    | 99.91%
# LOC    | Warsaw         | 99.87%
# LOC    | Poland         | 99.82%

# aggregation_strategy options:
# "none"     → raw per-token labels (B-PER, I-PER, etc.)
# "simple"   → merge consecutive same-type tokens
# "first"    → use score of first token for merged entity
# "average"  → average scores of all tokens in entity
# "max"      → use max score of tokens in entity
```

**Recommended models:**
- `dbmdz/bert-large-cased-finetuned-conll03-english` — general NER (PER, ORG, LOC, MISC)
- `d4data/biomedical-ner-all` — biomedical entities
- `Jean-Baptiste/roberta-large-ner-english` — high accuracy general NER

---

## 3. Question Answering (Extractive)

**Use for:** Finding an answer span within a provided context document. The model does NOT generate new text — it highlights the answer within the context.

```python
qa = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Must provide both question and context
result = qa(
    question="What is the capital of France?",
    context="France is a country in Western Europe. Its capital city is Paris, "
            "which is also the largest city in the country."
)

print(f"Answer: {result['answer']}")        # → Paris
print(f"Score: {result['score']:.2%}")      # → confidence
print(f"Start: {result['start']}, End: {result['end']}")  # character positions

# Batch: list of question/context dicts
batch = [
    {"question": "Where is Paris?", "context": "Paris is located in northern France."},
    {"question": "Who invented Python?", "context": "Python was created by Guido van Rossum."},
]
results = qa(batch)
for r in results:
    print(r['answer'])
```

**Recommended models:**
- `deepset/roberta-base-squad2` — general extractive QA
- `deepset/deberta-v3-base-squad2` — higher accuracy, slower
- `distilbert-base-cased-distilled-squad` — fast, lightweight

---

## 4. Summarization

**Use for:** Condensing long documents into shorter summaries. Uses encoder-decoder models (BART, T5, PEGASUS).

```python
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """
NASA's Perseverance rover has been exploring Mars since February 2021 as part of the
Mars 2020 mission. The rover is equipped with a suite of scientific instruments to
search for signs of ancient microbial life and to collect rock and regolith samples
for potential return to Earth. Perseverance has already identified several interesting
geological features and collected 23 rock core samples. Its companion, the Ingenuity
helicopter, completed over 70 flights, demonstrating powered flight on another planet
for the first time in history.
"""

summary = summarizer(
    article,
    max_length=80,       # Max tokens in output
    min_length=20,       # Min tokens in output
    do_sample=False,     # False = deterministic (greedy/beam)
    num_beams=4          # Beam search width (higher = better quality, slower)
)
print(summary[0]['summary_text'])

# For very long documents that exceed model's max_length:
# Use truncation=True (cuts input) or split into chunks
summary_truncated = summarizer(article, max_length=80, truncation=True)
```

**Recommended models:**
- `facebook/bart-large-cnn` — trained on CNN/Daily Mail, good for news
- `google/pegasus-xsum` — extreme summarization (very short outputs)
- `philschmid/bart-large-cnn-samsum` — dialogue/chat summarization

---

## 5. Translation

**Use for:** Converting text from one language to another. Helsinki-NLP's OPUS-MT models cover 1000+ language pairs.

```python
# Language pair format: Helsinki-NLP/opus-mt-{source}-{target}
translator_en_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
translator_en_de = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de")

text = "Artificial intelligence will reshape the global economy."

print(translator_en_fr(text)[0]['translation_text'])
# → "L'intelligence artificielle va remodeler l'économie mondiale."

print(translator_en_de(text)[0]['translation_text'])
# → "Künstliche Intelligenz wird die Weltwirtschaft umgestalten."

# For many languages with one model, use M2M100 (multilingual)
multilingual = pipeline("translation", model="facebook/m2m100_418M")
multilingual.tokenizer.src_lang = "en"
result = multilingual("Hello world", forced_bos_token_id=multilingual.tokenizer.get_lang_id("zh"))
# Translates English → Chinese
```

**Common language codes:** `en`, `fr`, `de`, `es`, `it`, `pt`, `ru`, `zh`, `ja`, `ko`, `ar`

---

## 6. Text Generation (Causal / Decoder-only)

**Use for:** Generating text continuations — creative writing, code completion, chat responses, autocomplete.

```python
from transformers import pipeline
import torch

generator = pipeline("text-generation", model="gpt2")  # or "gpt2-medium", "gpt2-large"

# Basic generation
outputs = generator(
    "The secret to happiness is",
    max_new_tokens=50,
    num_return_sequences=2,
    do_sample=True,
    temperature=0.9,     # < 1.0 = more focused, > 1.0 = more random
    top_k=50,            # Only sample from top 50 tokens
    top_p=0.95,          # Nucleus sampling: top 95% probability mass
    repetition_penalty=1.1
)

for i, output in enumerate(outputs):
    print(f"[{i+1}] {output['generated_text']}\n")

# Instruction-following (use instruction-tuned models):
instruct = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-beta",
                    torch_dtype=torch.bfloat16, device_map="auto")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain transformers in 2 sentences."}
]
response = instruct(messages, max_new_tokens=200)
print(response[0]['generated_text'][-1]['content'])
```

---

## 7. Fill Mask

**Use for:** Predicting missing words in a sentence. Useful for probing model knowledge and for data augmentation.

```python
fill = pipeline("fill-mask", model="bert-base-uncased")

# [MASK] is BERT's mask token
results = fill("Paris is the [MASK] of France.")

for r in results[:3]:
    print(f"'{r['token_str']}' — score: {r['score']:.2%}")
    print(f"  Full sentence: {r['sequence']}\n")
# 'capital' — score: 98.72%
# 'heart' — score: 0.41%
# 'center' — score: 0.29%

# RoBERTa uses <mask> instead of [MASK]
fill_roberta = pipeline("fill-mask", model="roberta-base")
results = fill_roberta("The <mask> jumped over the fence.")
```

---

## 8. Zero-Shot Classification

**Use for:** Classifying text into categories without any fine-tuning. You define the labels at inference time.

```python
clf = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "Apple just announced the M4 chip with unprecedented neural engine performance."

# You completely control the categories — no training needed
result = clf(
    text,
    candidate_labels=["technology", "sports", "politics", "cooking", "finance"],
    multi_label=False   # True = multiple labels can be positive
)

print("Label Rankings:")
for label, score in zip(result['labels'], result['scores']):
    print(f"  {label:15s}: {score:.2%}")
# technology    : 94.32%
# finance       :  2.11%
# politics      :  1.87%
```

---

## 9. Automatic Speech Recognition (ASR)

**Use for:** Converting audio to text. Whisper is the dominant model — supports 99 languages.

```python
from transformers import pipeline
import torch

asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",  # Options: tiny, base, small, medium, large-v3
    device=0 if torch.cuda.is_available() else -1
)

# From a local audio file (supports mp3, wav, flac, etc.)
result = asr("path/to/audio.mp3")
print(result['text'])

# With timestamps (useful for subtitles)
result_with_timestamps = asr(
    "path/to/audio.mp3",
    return_timestamps=True
)
for chunk in result_with_timestamps['chunks']:
    start, end = chunk['timestamp']
    print(f"[{start:.1f}s → {end:.1f}s] {chunk['text']}")

# Force a specific language (skip language detection):
result_forced = asr("audio.mp3", generate_kwargs={"language": "french"})
```

---

## 10. Image Classification

**Use for:** Identifying what's in an image. Vision models trained on ImageNet or specialized datasets.

```python
from transformers import pipeline
from PIL import Image
import requests

img_clf = pipeline("image-classification", model="google/vit-base-patch16-224")

# From URL
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Cute_dog.jpg/640px-Cute_dog.jpg"
results = img_clf(image_url)

print("Predictions:")
for r in results[:3]:
    print(f"  {r['label']:30s}: {r['score']:.2%}")

# From local file
local_results = img_clf(Image.open("my_photo.jpg"))

# From numpy array or torch tensor also supported
```

---

## 11. Image-to-Text (Image Captioning)

**Use for:** Generating text descriptions of images.

```python
from transformers import pipeline

captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

caption = captioner("https://example.com/cat.jpg")
print(caption[0]['generated_text'])
# → "a cat sitting on a wooden table next to a window"

# For visual question answering, use a VQA model:
vqa = pipeline("visual-question-answering", model="dandelin/vilt-b32-finetuned-vqa")
result = vqa(image="cat.jpg", question="What color is the cat?")
print(result[0]['answer'])
```

---

## Pipeline Performance Tips

```python
# 1. Use GPU: device=0 (first GPU) or device_map="auto" for multi-GPU
pipe = pipeline("text-classification", model="...", device=0)

# 2. Batch processing — much faster than one-at-a-time
results = pipe(list_of_1000_texts, batch_size=64)

# 3. Half precision for GPU (saves memory, speeds up)
from transformers import pipeline
import torch
pipe = pipeline("text-generation", model="gpt2",
                torch_dtype=torch.float16, device=0)

# 4. Truncate long inputs instead of erroring
pipe = pipeline("summarization", model="facebook/bart-large-cnn", truncation=True)
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Library overview and AutoClass system |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Key pipeline examples |
| 📄 **Pipeline_Guide.md** | All pipeline types in detail (you are here) |

⬅️ **Prev:** [Hub and Model Cards](../01_Hub_and_Model_Cards/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Datasets Library](../03_Datasets_Library/Theory.md)
