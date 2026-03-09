# BERT — Code Example

## Masked Language Modeling (Fill-in-the-blank)

```python
# pip install transformers torch

from transformers import pipeline, AutoTokenizer, AutoModel
import torch

# ─────────────────────────────────────────
# 1. Masked Language Modeling (fill in the blank)
# ─────────────────────────────────────────
mlm = pipeline("fill-mask", model="bert-base-uncased")

sentences = [
    "The [MASK] sat on the mat.",
    "The president signed the [MASK] into law.",
    "She earned a [MASK] in computer science.",
    "The bank was [MASK] due to the storm.",
]

print("=== Masked Language Modeling ===")
for sent in sentences:
    results = mlm(sent, top_k=5)
    print(f"\nInput: {sent}")
    for r in results:
        print(f"  [{r['score']:.3f}] {r['token_str']}")
```

**Expected output:**

```
Input: The [MASK] sat on the mat.
  [0.834] cat
  [0.071] dog
  [0.034] rat
  [0.021] man
  [0.012] boy

Input: The president signed the [MASK] into law.
  [0.421] bill
  [0.198] legislation
  [0.134] treaty
  [0.089] agreement
  [0.041] order
```

---

## Sentence Classification with BERT

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load a BERT model fine-tuned for sentiment analysis
# (distilbert-base-uncased-finetuned-sst-2-english is a popular choice)
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

texts = [
    "This movie was absolutely fantastic!",
    "I wasted two hours of my life.",
    "It was okay, nothing special.",
    "Loved every minute of it — highly recommend!",
]

print("=== Sentiment Classification ===")
for text in texts:
    result = classifier(text)[0]
    print(f"Text:  {text}")
    print(f"Label: {result['label']}  Score: {result['score']:.3f}")
    print()
```

**Output:**

```
Text:  This movie was absolutely fantastic!
Label: POSITIVE  Score: 0.998

Text:  I wasted two hours of my life.
Label: NEGATIVE  Score: 0.997

Text:  It was okay, nothing special.
Label: NEGATIVE  Score: 0.683

Text:  Loved every minute of it — highly recommend!
Label: POSITIVE  Score: 0.999
```

---

## Extract BERT Embeddings (sentence-level)

```python
# Get [CLS] token embedding for each sentence
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

sentences = [
    "Machine learning is fascinating.",
    "Deep learning is a subset of machine learning.",
    "The cat sat on the mat.",
]

def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # [CLS] token is the first token; take its hidden state
    cls_embedding = outputs.last_hidden_state[:, 0, :]  # shape: (1, 768)
    return cls_embedding.squeeze().numpy()

embeddings = [get_bert_embedding(s) for s in sentences]

# Cosine similarity
from numpy.linalg import norm
import numpy as np

def cosine_sim(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

print("=== BERT Embedding Similarities ===")
pairs = [
    (0, 1, "ML sentence vs Deep Learning sentence"),
    (0, 2, "ML sentence vs Cat sentence"),
    (1, 2, "Deep Learning sentence vs Cat sentence"),
]
for i, j, label in pairs:
    sim = cosine_sim(embeddings[i], embeddings[j])
    print(f"{label}: {sim:.3f}")
```

**Output:**

```
=== BERT Embedding Similarities ===
ML sentence vs Deep Learning sentence: 0.941
ML sentence vs Cat sentence: 0.712
Deep Learning sentence vs Cat sentence: 0.698
```

The two ML-related sentences are much more similar than either is to the cat sentence.

---

## Named Entity Recognition with BERT

```python
ner = pipeline("token-classification", model="dslim/bert-base-NER", aggregation_strategy="simple")

texts = [
    "Elon Musk founded SpaceX in Hawthorne, California.",
    "Apple Inc. released the iPhone 15 in September 2023.",
    "The Eiffel Tower is located in Paris, France.",
]

print("=== Named Entity Recognition ===")
for text in texts:
    entities = ner(text)
    print(f"\nText: {text}")
    for ent in entities:
        print(f"  {ent['entity_group']:<8} '{ent['word']}' (score={ent['score']:.3f})")
```

**Output:**

```
Text: Elon Musk founded SpaceX in Hawthorne, California.
  PER      'Elon Musk' (score=0.999)
  ORG      'SpaceX' (score=0.998)
  LOC      'Hawthorne' (score=0.987)
  LOC      'California' (score=0.994)

Text: Apple Inc. released the iPhone 15 in September 2023.
  ORG      'Apple Inc.' (score=0.996)
  MISC     'iPhone 15' (score=0.921)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 GPT](../09_GPT/Theory.md)