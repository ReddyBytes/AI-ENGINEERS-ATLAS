# Word Embeddings — Interview Q&A

## Beginner

**Q1. What is a word embedding and why is it better than one-hot encoding?**

A word embedding is a dense vector of numbers that represents a word — typically 100 to 300 numbers. It's learned from text patterns, so words with similar meanings end up with similar vectors.

One-hot encoding gives each word a vector of zeros with a single 1 in its unique position. For a vocabulary of 50,000 words, "cat" is a 50,000-dimensional vector with a single 1. These vectors are sparse (mostly zeros), huge, and have no relationship to each other — "cat" and "dog" look equally distant as "cat" and "mountain".

Word embeddings are dense (all values meaningful), compact (100–300 dimensions), and semantic — "cat" and "dog" are close because they appear in similar contexts.

---

**Q2. What is the distributional hypothesis and why does it matter for embeddings?**

The distributional hypothesis states: words that appear in similar contexts have similar meanings.

If you read a million sentences, you'll notice that "cat" and "dog" both appear after "my", "the", "feed", "pet", and before "ran", "slept", "played". They share context. Word2Vec exploits this — it learns that words with similar surrounding words should have similar vectors.

This is why you don't need hand-labeled semantic relationships. The meaning emerges automatically from patterns in raw text.

---

**Q3. What is cosine similarity and why is it used for comparing word embeddings?**

Cosine similarity measures the angle between two vectors. It ranges from -1 to 1:

- 1 = same direction = very similar
- 0 = perpendicular = unrelated
- -1 = opposite directions = antonyms

We use cosine similarity (not Euclidean distance) because embeddings can have very different magnitudes — a word that appeared 1000 times in training has a larger-magnitude vector than one that appeared 50 times. Cosine similarity ignores magnitude and focuses on direction, which captures semantic relationship better.

---

## Intermediate

**Q4. How does Word2Vec's Skip-gram training work?**

Skip-gram takes a center word and trains the model to predict the surrounding words within a window.

For the sentence "The quick brown fox jumped", with window=2 and center word "fox":
- The model predicts: "quick", "brown", "jumped", "over"

The model is a simple neural network. The input is the one-hot encoding of the center word. The hidden layer weights become the embeddings. The output is a probability distribution over the vocabulary for each context position.

Training adjusts the weights so that context words get high probability given the center word. After millions of examples, the hidden layer weights (the embeddings) encode rich semantic relationships.

---

**Q5. What is the difference between Word2Vec, GloVe, and FastText?**

All three produce static word embeddings (one fixed vector per word), but they learn differently:

**Word2Vec** — learns from local context windows. For each word, it looks at neighboring words. Fast and effective but only captures local patterns.

**GloVe** — learns from global co-occurrence statistics. It builds a matrix of how often each pair of words appears together across the whole corpus, then factorizes it. Captures global structure better than Word2Vec.

**FastText** — represents each word as a sum of its character n-gram embeddings. "playing" = embeddings of "pla", "lay", "ayi", "yin", "ing", "play", "laying" etc. This means it can generate reasonable embeddings for words never seen in training (OOV). Best for morphologically rich languages or noisy text.

---

**Q6. What are contextual embeddings and how do they differ from static embeddings?**

Static embeddings (Word2Vec, GloVe) give every word exactly one fixed vector. "Bank" always gets the same vector whether you mean a financial institution or a river bank.

Contextual embeddings (ELMo, BERT) generate a different vector for each occurrence of a word depending on its context. "I went to the bank to deposit money" gives "bank" a finance-flavored vector. "The children played on the river bank" gives it a geography-flavored vector.

Contextual embeddings are dramatically more powerful for tasks like named entity recognition, question answering, and sentiment analysis where word meaning depends on context.

---

## Advanced

**Q7. How would you evaluate the quality of word embeddings?**

Two types of evaluation:

**Intrinsic evaluation — testing the embeddings directly:**
- Word similarity benchmarks (e.g., WordSim-353): compare embedding cosine similarity to human similarity ratings
- Word analogy tasks (e.g., Google Analogy Test Set): "king − man + woman = ?" and check if queen is top result
- Clustering: do semantically related words cluster together in the embedding space?

**Extrinsic evaluation — measuring performance on downstream tasks:**
- Use the embeddings in a text classification or NER model and measure accuracy
- Compare to random embeddings or TF-IDF as baselines

Intrinsic evaluation is fast but doesn't always predict downstream task performance. Extrinsic evaluation is more reliable but slower.

---

**Q8. How do you handle words not in a pretrained embedding vocabulary (OOV) when using Word2Vec?**

Several strategies:

1. **Use FastText** — handles OOV by computing vectors from character n-grams
2. **Map to [UNK]** — replace all OOV words with a special unknown token vector
3. **Average of subwords** — manually split the word and average the vectors of any recognizable parts
4. **Character-level models** — don't use word embeddings at all; use character-level representations
5. **Fine-tune on domain data** — extend the pretrained vocabulary by continuing training on domain text that contains your OOV words

In practice, FastText is the most practical solution for production systems that encounter new words regularly.

---

**Q9. What are the limitations of word embeddings and how did transformers address them?**

Key limitations:

1. **Static context** — one vector per word regardless of context (Word2Vec/GloVe)
2. **No sentence-level meaning** — embeddings are word-level, not sentence-level
3. **Biases from training data** — if "nurse" and "she" co-occur more than "nurse" and "he", the embedding reflects that bias
4. **Limited coverage** — words with few occurrences get poor embeddings

How transformers address these:

1. **Contextual representations** — BERT generates different embeddings for the same word in different contexts
2. **Sentence-level understanding** — the [CLS] token provides a sentence-level representation
3. **Richer training objectives** — masked language modeling forces the model to understand full sentence context
4. **Subword tokenization** — handles rare and OOV words natively

Word embeddings are still useful as lightweight features in resource-constrained settings, but transformers have largely superseded them for accuracy-critical tasks.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md)
