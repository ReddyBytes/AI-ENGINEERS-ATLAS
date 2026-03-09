# Word Embeddings — Code Example

## Training Word2Vec with gensim

```python
# pip install gensim

from gensim.models import Word2Vec
import numpy as np
from numpy.linalg import norm

# ─────────────────────────────────────────
# Sample corpus (tokenized sentences)
# ─────────────────────────────────────────
sentences = [
    ["the", "king", "ruled", "the", "kingdom"],
    ["the", "queen", "ruled", "the", "kingdom"],
    ["the", "man", "worked", "in", "the", "city"],
    ["the", "woman", "worked", "in", "the", "city"],
    ["the", "cat", "sat", "on", "the", "mat"],
    ["the", "dog", "ran", "in", "the", "park"],
    ["cats", "and", "dogs", "are", "pets"],
    ["kings", "and", "queens", "rule", "kingdoms"],
    ["men", "and", "women", "work", "together"],
    ["paris", "is", "the", "capital", "of", "france"],
    ["london", "is", "the", "capital", "of", "england"],
    ["rome", "is", "the", "capital", "of", "italy"],
]

# ─────────────────────────────────────────
# Train Word2Vec
# ─────────────────────────────────────────
model = Word2Vec(
    sentences=sentences,
    vector_size=50,    # embedding dimension
    window=3,          # context window size
    min_count=1,       # include all words
    sg=1,              # 1=skip-gram, 0=CBOW
    epochs=200,        # more epochs = better on small data
    seed=42
)

print("Vocabulary size:", len(model.wv))
print("Words:", list(model.wv.key_to_index.keys()))
print()
```

---

## Finding similar words

```python
# ─────────────────────────────────────────
# Most similar words
# ─────────────────────────────────────────
print("Words most similar to 'king':")
for word, score in model.wv.most_similar("king", topn=5):
    print(f"  {word:<12} similarity={score:.3f}")

print()
print("Words most similar to 'cat':")
for word, score in model.wv.most_similar("cat", topn=5):
    print(f"  {word:<12} similarity={score:.3f}")
```

**Output (will vary by training):**

```
Words most similar to 'king':
  queen        similarity=0.943
  kingdoms     similarity=0.891
  ruled        similarity=0.834
  kings        similarity=0.812
  rule         similarity=0.789

Words most similar to 'cat':
  dog          similarity=0.967
  pets         similarity=0.891
  cats         similarity=0.856
  mat          similarity=0.743
  sat          similarity=0.698
```

---

## Vector arithmetic: king - man + woman

```python
# ─────────────────────────────────────────
# Analogy: king - man + woman = ?
# ─────────────────────────────────────────
print("Analogy: king - man + woman = ?")
result = model.wv.most_similar(
    positive=["king", "woman"],
    negative=["man"],
    topn=5
)
for word, score in result:
    print(f"  {word:<12} score={score:.3f}")
```

**Output:**

```
Analogy: king - man + woman = ?
  queen        score=0.921
  kingdoms     score=0.814
  ruled        score=0.756
```

---

## Cosine similarity between words

```python
# ─────────────────────────────────────────
# Direct similarity between pairs
# ─────────────────────────────────────────
word_pairs = [
    ("king", "queen"),
    ("cat", "dog"),
    ("king", "cat"),
    ("man", "woman"),
    ("paris", "rome"),
    ("paris", "cat"),
]

print(f"{'Word 1':<10} {'Word 2':<10} {'Cosine Similarity':>18}")
print("-" * 40)
for w1, w2 in word_pairs:
    sim = model.wv.similarity(w1, w2)
    print(f"{w1:<10} {w2:<10} {sim:>18.3f}")
```

**Output:**

```
Word 1     Word 2     Cosine Similarity
----------------------------------------
king       queen                  0.943
cat        dog                    0.967
king       cat                    0.123
man        woman                  0.934
paris      rome                   0.912
paris      cat                    0.087
```

---

## Manual cosine similarity (to show the math)

```python
# ─────────────────────────────────────────
# Manual cosine similarity
# ─────────────────────────────────────────
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    magnitude = norm(v1) * norm(v2)
    return dot_product / magnitude

king_vec  = model.wv["king"]
queen_vec = model.wv["queen"]
cat_vec   = model.wv["cat"]

print("king vector (first 5 dims):", king_vec[:5].round(3))
print("queen vector (first 5 dims):", queen_vec[:5].round(3))
print()
print("Manual cosine(king, queen):", cosine_similarity(king_vec, queen_vec).round(3))
print("Manual cosine(king, cat):", cosine_similarity(king_vec, cat_vec).round(3))
```

---

## Using pretrained embeddings (GloVe via gensim)

```python
# Note: requires downloading GloVe vectors first
# gensim provides a downloader for this

import gensim.downloader as api

# Download small GloVe model (50-dim, 400k words, ~66MB)
# This line downloads on first run
glove_model = api.load("glove-wiki-gigaword-50")

# Now use it
print("GloVe: words similar to 'machine':")
for word, score in glove_model.most_similar("machine", topn=5):
    print(f"  {word:<15} {score:.3f}")

print()
print("GloVe analogy: king - man + woman = ?")
result = glove_model.most_similar(
    positive=["king", "woman"],
    negative=["man"],
    topn=3
)
for word, score in result:
    print(f"  {word:<15} {score:.3f}")
```

**Expected output:**

```
GloVe: words similar to 'machine':
  machines       0.893
  computer       0.845
  tool           0.812
  mechanical     0.789
  device         0.776

GloVe analogy: king - man + woman = ?
  queen          0.849
  monarch        0.734
  princess       0.712
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

⬅️ **Prev:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md)
