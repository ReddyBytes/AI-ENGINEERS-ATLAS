# Word Embeddings — Cheatsheet

**One-liner:** Word embeddings are dense numerical vectors that represent words based on the contexts they appear in — similar words end up with similar vectors.

---

## Key Terms

| Term | Definition |
|---|---|
| Word embedding | A dense vector representation of a word |
| Word2Vec | Algorithm that learns embeddings by predicting context (Google, 2013) |
| GloVe | Embeddings from global co-occurrence statistics (Stanford, 2014) |
| FastText | Subword-aware embeddings from Facebook (handles OOV) |
| CBOW | Word2Vec mode: predict center word from context |
| Skip-gram | Word2Vec mode: predict context from center word |
| Cosine similarity | Angle-based measure of how similar two vectors are (0–1) |
| Distributional hypothesis | Words with similar contexts have similar meanings |
| Embedding dimension | Size of the vector (typically 100–300 for word2vec) |

---

## Cosine similarity

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)

= 1  → identical direction (very similar)
= 0  → perpendicular (unrelated)
= -1 → opposite (antonyms)
```

---

## Vector arithmetic examples

```
king - man + woman ≈ queen
paris - france + italy ≈ rome
walking - walk + swim ≈ swimming
```

---

## Embedding types comparison

| Method | Context-aware? | Handles OOV? | Use case |
|---|---|---|---|
| Word2Vec | No (static) | No | Fast, general NLP |
| GloVe | No (static) | No | Good pretrained vectors |
| FastText | No (static) | Yes (subwords) | Morphologically rich languages |
| ELMo | Yes (contextual) | Partial | When context matters |
| BERT | Yes (deep) | Yes (subwords) | State-of-the-art tasks |

---

## When to use word embeddings vs BoW

| Use BoW/TF-IDF | Use Embeddings |
|---|---|
| Keyword matching tasks | Semantic similarity |
| Very small datasets | Sufficient data for learning |
| Need interpretability | Need meaning |
| Simple classification baseline | Complex language understanding |

---

## Quick gensim reference

```python
from gensim.models import Word2Vec, KeyedVectors

# Train from scratch
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)

# Similar words
model.wv.most_similar("king", topn=5)

# Vector arithmetic
result = model.wv.most_similar(
    positive=["king", "woman"], negative=["man"]
)

# Cosine similarity between two words
sim = model.wv.similarity("cat", "dog")

# Load pretrained (Google News Word2Vec)
wv = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True)
```

---

## Golden Rules

1. Pretrained embeddings (Word2Vec, GloVe) are almost always better than training from scratch on small datasets.
2. Use FastText if your domain has lots of morphological variation or rare words.
3. Static embeddings (Word2Vec, GloVe) give the same vector for "bank" regardless of context — use BERT if context matters.
4. Embedding dimension 100–300 is usually enough; bigger isn't always better.
5. Normalize vectors before doing cosine similarity comparisons.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md)
