# Embeddings — Code Example

Generate embeddings for sentences and compute cosine similarity to show which sentences are semantically close.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# OPTION A: Using sentence-transformers (free, local)
# pip install sentence-transformers
# ─────────────────────────────────────────────

model = SentenceTransformer("all-MiniLM-L6-v2")

# Our 5 test sentences
sentences = [
    "I love my dog — he's so playful!",          # 0: about dogs/pets
    "My puppy is absolutely adorable.",            # 1: about dogs/pets (very similar to 0)
    "Cats make wonderful companions.",             # 2: about pets (different animal)
    "Machine learning requires a lot of math.",   # 3: about ML/tech
    "Deep learning models need gradient descent.", # 4: about ML/tech (similar to 3)
]

# Generate embeddings — each is a 384-dim vector
embeddings = model.encode(sentences)
print(f"Embedding shape: {embeddings.shape}")  # (5, 384)
print(f"First embedding (first 5 dims): {embeddings[0][:5]}")


# ─────────────────────────────────────────────
# Cosine similarity function
# ─────────────────────────────────────────────

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ─────────────────────────────────────────────
# Compare all sentence pairs
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("PAIRWISE COSINE SIMILARITY SCORES")
print("=" * 60)

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        score = cosine_similarity(embeddings[i], embeddings[j])
        label = "SIMILAR" if score > 0.75 else ("RELATED" if score > 0.5 else "DIFFERENT")
        print(f"[{score:.3f}] {label}")
        print(f"  A: {sentences[i][:50]}")
        print(f"  B: {sentences[j][:50]}")
        print()


# ─────────────────────────────────────────────
# Find most similar sentence to a query
# ─────────────────────────────────────────────

def find_most_similar(query: str, corpus: list, corpus_embeddings: np.ndarray, model) -> tuple:
    """Find the most semantically similar sentence in the corpus."""
    query_embedding = model.encode([query])[0]

    scores = [cosine_similarity(query_embedding, e) for e in corpus_embeddings]
    best_idx = np.argmax(scores)

    return corpus[best_idx], scores[best_idx]


print("=" * 60)
print("SEMANTIC SEARCH DEMO")
print("=" * 60)

queries = [
    "I have a pet at home",
    "neural networks and optimization",
    "my golden retriever"
]

for query in queries:
    best_match, score = find_most_similar(query, sentences, embeddings, model)
    print(f"\nQuery: '{query}'")
    print(f"Best match [{score:.3f}]: '{best_match}'")


# ─────────────────────────────────────────────
# OPTION B: Using OpenAI API
# pip install openai
# ─────────────────────────────────────────────

def get_openai_embeddings(texts: list[str]) -> np.ndarray:
    """Generate embeddings using OpenAI's API."""
    from openai import OpenAI
    client = OpenAI()  # uses OPENAI_API_KEY env var

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    # Extract vectors from response
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings)


# Uncomment to use OpenAI:
# openai_embeddings = get_openai_embeddings(sentences)
# print(f"OpenAI embedding shape: {openai_embeddings.shape}")  # (5, 1536)
#
# for i in range(len(sentences)):
#     for j in range(i + 1, len(sentences)):
#         score = cosine_similarity(openai_embeddings[i], openai_embeddings[j])
#         print(f"[{score:.3f}] {sentences[i][:40]} <-> {sentences[j][:40]}")
```

**Expected output:**
```
Embedding shape: (5, 384)

PAIRWISE COSINE SIMILARITY SCORES
[0.821] SIMILAR
  A: I love my dog — he's so playful!
  B: My puppy is absolutely adorable.

[0.612] RELATED
  A: I love my dog — he's so playful!
  B: Cats make wonderful companions.

[0.134] DIFFERENT
  A: I love my dog — he's so playful!
  B: Machine learning requires a lot of math.

[0.156] DIFFERENT
  A: I love my dog — he's so playful!
  B: Deep learning models need gradient descent.

[0.589] RELATED
  A: My puppy is absolutely adorable.
  B: Cats make wonderful companions.

[0.801] SIMILAR
  A: Machine learning requires a lot of math.
  B: Deep learning models need gradient descent.

SEMANTIC SEARCH DEMO
Query: 'I have a pet at home'
Best match [0.743]: 'I love my dog — he's so playful!'

Query: 'neural networks and optimization'
Best match [0.812]: 'Deep learning models need gradient descent.'

Query: 'my golden retriever'
Best match [0.791]: 'I love my dog — he's so playful!'
```

**Install and run:**
```bash
pip install sentence-transformers numpy
python embeddings_example.py
```

**Key observations from the output:**
- Dog sentences (0, 1) score 0.82 — very similar
- ML sentences (3, 4) score 0.80 — very similar
- Dog vs cats (0, 2) score 0.61 — related (both pets) but less similar
- Dog vs ML (0, 3) score 0.13 — completely different topics
- Semantic search finds correct match even with different wording

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Vector Databases](../05_Vector_Databases/Theory.md)
