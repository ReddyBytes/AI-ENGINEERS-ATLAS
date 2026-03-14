# Transformers Library — Code Examples

## Setup

```python
# pip install transformers torch accelerate

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoModelForQuestionAnswering,
    AutoModelForTokenClassification,
)
import torch
```

---

## Example 1: Text Classification (Sentiment Analysis)

```python
from transformers import pipeline

# Quick pipeline — uses a default model
# For production, always specify model=
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Single text
result = classifier("I absolutely love this product!")
print(result)
# → [{'label': 'POSITIVE', 'score': 0.9998}]

# Batch of texts — much faster than one at a time
texts = [
    "This restaurant was incredible.",
    "The service was terrible and food was cold.",
    "It was okay, nothing special.",
]
results = classifier(texts)
for text, res in zip(texts, results):
    print(f"{res['label']:8s} ({res['score']:.2%}): {text[:50]}")
```

---

## Example 2: Named Entity Recognition (NER)

```python
from transformers import pipeline

# aggregation_strategy merges B-/I- tokens into complete entities
ner = pipeline(
    "token-classification",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple"
)

text = "Elon Musk founded SpaceX in Hawthorne, California in 2002."
entities = ner(text)

for ent in entities:
    print(f"[{ent['entity_group']}] '{ent['word']}' (score: {ent['score']:.2%})")

# Output:
# [PER] 'Elon Musk' (score: 99.85%)
# [ORG] 'SpaceX' (score: 99.42%)
# [LOC] 'Hawthorne' (score: 99.71%)
# [LOC] 'California' (score: 99.68%)
```

---

## Example 3: Extractive Question Answering

```python
from transformers import pipeline

qa = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2"
)

context = """
Hugging Face is a French-American company founded in 2016 in New York City.
It is known for the Transformers library, which provides thousands of pretrained
models for NLP, vision, audio, and multimodal tasks. The company hosts the
Hugging Face Hub, a platform for sharing and discovering AI models and datasets.
"""

questions = [
    "Where was Hugging Face founded?",
    "What is Hugging Face known for?",
    "When was the company founded?",
]

for question in questions:
    answer = qa(question=question, context=context)
    print(f"Q: {question}")
    print(f"A: {answer['answer']} (score: {answer['score']:.2%})\n")
```

---

## Example 4: Summarization

```python
from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

long_text = """
The James Webb Space Telescope (JWST) is a space telescope designed primarily to conduct
infrared astronomy. As the largest optical telescope in space, its high resolution and
sensitivity allow it to view objects too old, distant, or faint for the Hubble Space
Telescope. This enables investigations across many fields of astronomy and cosmology,
such as observation of the first stars and the formation of the first galaxies, and
detailed atmospheric characterization of potentially habitable exoplanets. The JWST was
launched on 25 December 2021 on an Ariane 5 rocket from Kourou, French Guiana, and
arrived at the Sun–Earth L2 Lagrange point in January 2022. The first JWST deep field
was released to the public on 11 July 2022 by US President Joe Biden.
"""

summary = summarizer(
    long_text,
    max_length=100,   # Maximum tokens in summary
    min_length=30,    # Minimum tokens in summary
    do_sample=False   # Deterministic output
)

print("Original length:", len(long_text.split()), "words")
print("Summary length:", len(summary[0]['summary_text'].split()), "words")
print("\nSummary:")
print(summary[0]['summary_text'])
```

---

## Example 5: Translation

```python
from transformers import pipeline

# Translate English to French
translator = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-en-fr"
)

english_texts = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is transforming every industry.",
    "How do you do?",
]

french_texts = translator(english_texts)
for en, fr in zip(english_texts, french_texts):
    print(f"EN: {en}")
    print(f"FR: {fr['translation_text']}\n")

# Multi-language: use opus-mt-LANG-LANG format
# English → German: Helsinki-NLP/opus-mt-en-de
# English → Spanish: Helsinki-NLP/opus-mt-en-es
# English → Chinese: Helsinki-NLP/opus-mt-en-zh
```

---

## Example 6: Text Generation (GPT-style)

```python
from transformers import pipeline
import torch

generator = pipeline(
    "text-generation",
    model="gpt2",
    device=0 if torch.cuda.is_available() else -1  # 0=first GPU, -1=CPU
)

prompt = "The future of artificial intelligence is"

outputs = generator(
    prompt,
    max_new_tokens=80,     # How many NEW tokens to generate
    num_return_sequences=3, # Generate 3 different completions
    do_sample=True,         # Enable sampling (for variety)
    temperature=0.8,        # Controls randomness (lower = more focused)
    top_p=0.9,             # Nucleus sampling (keeps top 90% probability mass)
    repetition_penalty=1.2  # Penalize repeating the same phrases
)

for i, output in enumerate(outputs, 1):
    print(f"--- Completion {i} ---")
    print(output['generated_text'])
    print()
```

---

## Example 7: Zero-Shot Classification (No Fine-Tuning Needed)

```python
from transformers import pipeline

# Classify text into categories the model was never explicitly trained on
zero_shot = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

text = "The new iPhone 15 features a titanium frame and USB-C charging."

# You define the categories — no fine-tuning required!
candidate_labels = ["technology", "sports", "politics", "entertainment", "finance"]

result = zero_shot(text, candidate_labels=candidate_labels)

print(f"Text: {text}\n")
print("Category scores:")
for label, score in zip(result['labels'], result['scores']):
    bar = "█" * int(score * 30)
    print(f"  {label:15s} {score:.2%} {bar}")
```

---

## Example 8: Using AutoClasses for Full Control

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

model_id = "distilbert-base-uncased-finetuned-sst-2-english"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)
model.eval()  # Important: disable dropout for inference

def classify_batch(texts: list[str], batch_size: int = 16) -> list[dict]:
    """Process texts in batches for efficiency."""
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Tokenize the batch
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        # Run inference
        with torch.no_grad():
            logits = model(**inputs).logits

        # Convert to probabilities
        probabilities = F.softmax(logits, dim=-1)

        for prob in probabilities:
            predicted_id = prob.argmax().item()
            results.append({
                "label": model.config.id2label[predicted_id],
                "score": prob[predicted_id].item(),
                "all_scores": {
                    model.config.id2label[j]: prob[j].item()
                    for j in range(len(prob))
                }
            })

    return results


# Test with a batch
texts = [
    "This is the best movie I've seen all year!",
    "Absolutely terrible experience. Never again.",
    "It was fine, I suppose.",
]

for text, result in zip(texts, classify_batch(texts)):
    print(f"{result['label']:8s} ({result['score']:.1%}): {text}")
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full library explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working pipeline code (you are here) |
| [📄 Pipeline_Guide.md](./Pipeline_Guide.md) | Complete guide to all pipeline types |

⬅️ **Prev:** [Hub and Model Cards](../01_Hub_and_Model_Cards/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Datasets Library](../03_Datasets_Library/Theory.md)
