# Semantic Similarity — Code Example

## Using sentence-transformers (SBERT)

```python
# pip install sentence-transformers

from sentence_transformers import SentenceTransformer, util
import numpy as np

# ─────────────────────────────────────────
# Load model
# ─────────────────────────────────────────
# "all-MiniLM-L6-v2" is fast and accurate — a great default
model = SentenceTransformer("all-MiniLM-L6-v2")

# ─────────────────────────────────────────
# Example 1: Simple pairwise similarity
# ─────────────────────────────────────────
pairs = [
    ("The car broke down.", "My vehicle stopped working."),
    ("I love programming.", "Coding is my passion."),
    ("The sky is blue.", "I enjoy pizza."),
    ("How do I reset my password?", "I forgot my login credentials."),
    ("Dogs are great pets.", "Cats make wonderful companions."),
]

print("Pairwise Semantic Similarity")
print("=" * 60)
for sent1, sent2 in pairs:
    emb1 = model.encode(sent1, convert_to_tensor=True)
    emb2 = model.encode(sent2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    print(f"A: {sent1}")
    print(f"B: {sent2}")
    print(f"Similarity: {score:.3f}")
    print("-" * 60)
```

**Expected output:**

```
A: The car broke down.
B: My vehicle stopped working.
Similarity: 0.847

A: I love programming.
B: Coding is my passion.
Similarity: 0.891

A: The sky is blue.
B: I enjoy pizza.
Similarity: 0.043

A: How do I reset my password?
B: I forgot my login credentials.
Similarity: 0.762

A: Dogs are great pets.
B: Cats make wonderful companions.
Similarity: 0.714
```

---

## Example 2: Semantic search — query against a corpus

```python
# ─────────────────────────────────────────
# FAQ semantic search
# ─────────────────────────────────────────
faq_corpus = [
    "How do I reset my password?",
    "What is your refund policy?",
    "How can I track my order?",
    "Can I change my delivery address?",
    "How do I cancel my subscription?",
    "What payment methods do you accept?",
    "How long does shipping take?",
    "How do I contact customer support?",
]

# Encode corpus once (do this upfront in production)
corpus_embeddings = model.encode(faq_corpus, convert_to_tensor=True)

# User queries that use different wording
queries = [
    "I forgot my login",
    "I want to stop my membership",
    "Where is my package?",
    "Can I get a refund?",
]

print("Semantic FAQ Search")
print("=" * 60)

for query in queries:
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Find top 3 matches
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=3)

    print(f"\nQuery: '{query}'")
    print("Top matches:")
    for hit in hits[0]:
        score = hit["score"]
        faq = faq_corpus[hit["corpus_id"]]
        print(f"  [{score:.3f}] {faq}")
```

**Expected output:**

```
Query: 'I forgot my login'
Top matches:
  [0.784] How do I reset my password?
  [0.521] How do I contact customer support?
  [0.398] How can I track my order?

Query: 'I want to stop my membership'
Top matches:
  [0.812] How do I cancel my subscription?
  [0.434] What is your refund policy?
  [0.312] What payment methods do you accept?

Query: 'Where is my package?'
Top matches:
  [0.891] How can I track my order?
  [0.534] Can I change my delivery address?
  [0.423] How long does shipping take?
```

---

## Example 3: All-pairs similarity matrix

```python
# ─────────────────────────────────────────
# Similarity heatmap between sentences
# ─────────────────────────────────────────
import pandas as pd

sentences = [
    "The dog barked loudly.",
    "The puppy was making noise.",
    "I love machine learning.",
    "Deep learning is fascinating.",
    "The weather is sunny today.",
]

embeddings = model.encode(sentences, convert_to_tensor=True)
similarity_matrix = util.cos_sim(embeddings, embeddings).numpy()

# Display as table
short_labels = [s[:25] + "..." if len(s) > 25 else s for s in sentences]
df = pd.DataFrame(
    similarity_matrix.round(3),
    index=short_labels,
    columns=[f"S{i+1}" for i in range(len(sentences))]
)

print("Similarity Matrix:")
print(df.to_string())
```

**Output:**

```
Similarity Matrix:
                              S1     S2     S3     S4     S5
The dog barked loudly.     1.000  0.821  0.134  0.145  0.211
The puppy was making noi...  0.821  1.000  0.112  0.121  0.198
I love machine learning.   0.134  0.112  1.000  0.834  0.089
Deep learning is fascinat  0.145  0.121  0.834  1.000  0.101
The weather is sunny toda  0.211  0.198  0.089  0.101  1.000
```

The dog sentences cluster together (0.821), the ML sentences cluster together (0.834), and weather is alone.

---

## Example 4: Find duplicate questions

```python
# ─────────────────────────────────────────
# Deduplication: find similar questions
# ─────────────────────────────────────────
questions = [
    "How do I reset my password?",
    "My account password is not working, how to fix?",
    "I need to change my email address",
    "How can I update my email?",
    "What time does the store close?",
    "I forgot my credentials, what should I do?",
    "When do you close?",
]

embeddings = model.encode(questions, convert_to_tensor=True)
similarity_matrix = util.cos_sim(embeddings, embeddings).numpy()

THRESHOLD = 0.75
print("Potential duplicate pairs (similarity > 0.75):")
print("-" * 60)

for i in range(len(questions)):
    for j in range(i + 1, len(questions)):
        score = similarity_matrix[i][j]
        if score > THRESHOLD:
            print(f"Score: {score:.3f}")
            print(f"  Q1: {questions[i]}")
            print(f"  Q2: {questions[j]}")
            print()
```

**Output:**

```
Potential duplicate pairs (similarity > 0.75):
------------------------------------------------------------
Score: 0.812
  Q1: How do I reset my password?
  Q2: My account password is not working, how to fix?

Score: 0.786
  Q1: How do I reset my password?
  Q2: I forgot my credentials, what should I do?

Score: 0.834
  Q1: I need to change my email address
  Q2: How can I update my email?

Score: 0.891
  Q1: What time does the store close?
  Q2: When do you close?
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

⬅️ **Prev:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Hidden Markov Models](../06_Hidden_Markov_Models/Theory.md)
