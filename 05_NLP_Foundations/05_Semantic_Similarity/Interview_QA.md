# Semantic Similarity — Interview Q&A

## Beginner

**Q1. What is semantic similarity and how is it different from string matching?**

<details>
<summary>💡 Show Answer</summary>

String matching compares the characters or words in two texts. "car" and "vehicle" share zero characters, so they'd score as completely different.

Semantic similarity compares meaning. "The car broke down" and "My vehicle stopped working" mean the same thing. A semantic similarity model gives them a high score (close to 1.0) because it understands that car and vehicle are synonyms and that "broke down" and "stopped working" describe the same event.

Semantic similarity is used in search engines, recommendation systems, FAQ matching, and anywhere you need to find texts that mean the same thing even when the words differ.

</details>

---

**Q2. What is a sentence embedding?**

<details>
<summary>💡 Show Answer</summary>

A sentence embedding is a single vector (a list of numbers) that captures the meaning of an entire sentence. Two sentences with similar meanings will produce vectors that point in similar directions.

A tool like SBERT takes any sentence and outputs a 384-dimensional or 768-dimensional vector. You can then use cosine similarity between vectors to get a similarity score between 0 and 1.

The key difference from word embeddings: word embeddings give one vector per word. Sentence embeddings give one vector per sentence, capturing the overall meaning.

</details>

---

**Q3. What is cosine similarity? Why is it used instead of Euclidean distance?**

<details>
<summary>💡 Show Answer</summary>

Cosine similarity measures the angle between two vectors. A small angle (vectors pointing in the same direction) means high similarity. A 90-degree angle means no relationship.

We use cosine similarity instead of Euclidean distance because sentence vectors can have very different lengths (magnitudes) depending on sentence length and model internals. Two sentences meaning the same thing might have vectors of different lengths. Cosine similarity ignores magnitude — it only cares about direction. That makes it more robust for comparing text meanings.

</details>

---

## Intermediate

**Q4. What is SBERT and how does it differ from vanilla BERT for similarity tasks?**

<details>
<summary>💡 Show Answer</summary>

BERT was designed for classification and token-level tasks. If you use vanilla BERT to compare two sentences, you have to pass them together (as one input) and use the [CLS] token or pooling. This means to compare N sentences against each other, you need N² forward passes — too slow for large-scale retrieval.

SBERT (Sentence BERT) fine-tunes BERT using a siamese or triplet network architecture on sentence pair tasks. This produces sentence embeddings that can be computed independently for each sentence. You encode each sentence once, store the embeddings, and compare with fast cosine similarity. This reduces comparison time from N² to just N.

SBERT is more accurate for semantic similarity than simple BERT pooling.

</details>

---

**Q5. How would you build a semantic search system using sentence embeddings?**

<details>
<summary>💡 Show Answer</summary>

1. **Preprocessing:** collect your document corpus (FAQ answers, product descriptions, etc.)
2. **Encode corpus:** compute SBERT embeddings for every document once. Store them.
3. **Query time:** when a user submits a query, encode it with the same model.
4. **Retrieve:** compute cosine similarity between the query vector and all stored document vectors.
5. **Return:** the top-k most similar documents.

For large corpora, step 4 would be too slow with brute-force. Use a vector database (FAISS, Pinecone, Weaviate) that indexes embeddings for fast approximate nearest neighbor search.

This is exactly the retrieval step in RAG (Retrieval-Augmented Generation) systems.

</details>

---

**Q6. What is the difference between a bi-encoder and a cross-encoder?**

<details>
<summary>💡 Show Answer</summary>

**Bi-encoder:** encodes each sentence independently into a vector. Similarity is then computed by comparing vectors (cosine similarity). Fast — you can precompute all embeddings. SBERT is a bi-encoder. Good for large-scale retrieval.

**Cross-encoder:** takes both sentences as a single input and directly outputs a similarity score. The model sees the interaction between sentences during encoding. Much more accurate, especially for subtle semantic differences. But slow — you can't precompute. Can't scale to millions of comparisons.

Best practice in production: use a bi-encoder for fast first-pass retrieval (get top 100 candidates), then use a cross-encoder to re-rank those 100 candidates accurately.

</details>

---

## Advanced

**Q7. How do you evaluate a semantic similarity system in production?**

<details>
<summary>💡 Show Answer</summary>

Evaluation strategies:

**Offline evaluation:**
- Use benchmark datasets (STS-Benchmark, SICK) where human annotators rated sentence pairs with similarity scores from 0 to 5
- Measure Pearson or Spearman correlation between model scores and human ratings
- Measure precision@k for retrieval tasks: of the top k results returned, how many are actually relevant?

**Online evaluation:**
- A/B test: show a fraction of users the new semantic search vs old keyword search
- Click-through rate, dwell time, user satisfaction ratings

**Label-specific:**
- For deduplication: precision and recall on known duplicate pairs
- For intent classification: accuracy on test set

</details>

---

**Q8. How would you handle multilingual semantic similarity?**

<details>
<summary>💡 Show Answer</summary>

Use a multilingual sentence transformer. Models like `paraphrase-multilingual-mpnet-base-v2` from sentence-transformers can encode sentences from 50+ languages into the same vector space.

This means "How do I reset my password?" in English and "Wie kann ich mein Passwort zurücksetzen?" in German will get very similar embeddings — you can retrieve across languages.

For production: test that the model handles your specific language pairs well, as performance varies by language. Consider using language-specific models for high-priority languages and falling back to multilingual for the rest.

</details>

---

**Q9. What are the failure modes of semantic similarity systems and how do you address them?**

<details>
<summary>💡 Show Answer</summary>

Common failure modes:

1. **Semantic drift:** "I want to cancel my subscription" and "I want to subscribe" have many shared words but opposite intents. SBERT might score them higher than expected because of shared vocabulary.
   - Fix: train on in-domain data with fine-tuned negatives

2. **Domain mismatch:** a model trained on general web text may not work well on medical or legal text.
   - Fix: fine-tune on domain-specific sentence pairs

3. **Short queries:** short queries like "password help" are ambiguous in vector space.
   - Fix: expand queries with relevant context before encoding

4. **Similarity without relevance:** two sentences can be semantically similar but not useful for your task.
   - Fix: frame the task correctly — for FAQ matching, train on (question, answer) pairs, not (question, question) pairs

5. **Threshold instability:** the right threshold for "similar enough" varies by topic.
   - Fix: set thresholds per topic cluster, not globally

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Hidden Markov Models](../06_Hidden_Markov_Models/Theory.md)
