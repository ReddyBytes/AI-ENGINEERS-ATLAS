# ROUGE and METEOR in NLP

Imagine you are evaluating a **text summarization system** that condenses long articles into concise summaries. You want to know **how closely the generated summaries match human-written ones**. Metrics like **ROUGE** and **METEOR** help quantify this similarity, going beyond simple word overlap to assess **content coverage, meaning, and readability**.

# What are ROUGE and METEOR?

Both ROUGE and METEOR are **evaluation metrics for NLP tasks**, primarily used in **summarization, translation, and generation tasks**. They compare **machine-generated text** with **reference (human) text** to measure quality.

 

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

- **Purpose:** Measures overlap between generated and reference text.  
- **Types:**
  1. **ROUGE-N:** Measures n-gram overlap (e.g., ROUGE-1 for unigrams, ROUGE-2 for bigrams).  
  2. **ROUGE-L:** Measures longest common subsequence (LCS) between generated and reference text.  
  3. **ROUGE-S:** Measures overlap of skip-bigrams (non-consecutive word pairs).  
- **Metrics Reported:** Precision, Recall, F1-score.
- **Example:**  
  - Reference: "The cat sat on the mat."  
  - Generated: "The cat is sitting on the mat."  
  - ROUGE-1 counts overlapping unigrams: "The, cat, on, the, mat" → calculates recall, precision, and F1.

 

### METEOR (Metric for Evaluation of Translation with Explicit ORdering)

- **Purpose:** Designed to **improve over BLEU** by considering **synonyms, stemming, and word order**.  
- **Key Features:**  
  - Matches **exact words, stems, and synonyms**.  
  - Penalizes fragmented matches to reward coherent sentences.  
- **Formula (Simplified):**  
  - Precision = matched words / generated words  
  - Recall = matched words / reference words  
  - F-score = harmonic mean of precision and recall, adjusted with a **fragmentation penalty**.  
- **Example:**  
  - Reference: "He is very happy today."  
  - Generated: "Today he feels extremely happy."  
  - METEOR rewards synonym matches (happy ↔ extremely happy) and considers order for penalty.

 

### How They Work in NLP

1. **Input:** Generated text and reference text(s).  
2. **Tokenization & Normalization:** Convert to comparable units (words, stems).  
3. **Matching:** Compute overlaps, consider synonyms/stems (METEOR), or sequences (ROUGE).  
4. **Scoring:** Generate metrics (Precision, Recall, F1, or final score).  
5. **Comparison:** Evaluate multiple models, tasks, or hyperparameter configurations.

*Example:*  
- Summarization: ROUGE-L detects the **longest shared sequence** between generated and reference summary.  
- Translation: METEOR accounts for **synonyms** and penalizes disordered word sequences.

 

### Why ROUGE and METEOR are Needed

- Simple metrics like BLEU may **ignore synonyms and semantic similarity**.  
- ROUGE captures **coverage and sequence overlap**, while METEOR accounts for **meaning, synonyms, and order**.  
- Without these metrics:
  - Developers cannot **reliably compare model outputs**.  
  - Summaries or translations may appear syntactically correct but **miss key content or meaning**.

 

### Applications

- **Text Summarization:** Compare system-generated summaries to human references.  
- **Machine Translation:** Evaluate translation quality.  
- **Paraphrase Generation:** Check semantic similarity between generated and reference sentences.  
- **Dialogue Systems:** Assess naturalness and correctness of generated responses.  
- **Question Answering / Knowledge Generation:** Evaluate factual and semantic correctness.

 

## Interview Q&A

**Q1. What is ROUGE, and when is it used?**  
A: ROUGE measures **n-gram or subsequence overlap** between generated and reference text, commonly used in summarization and translation.

**Q2. What is METEOR, and how is it different from BLEU?**  
A: METEOR considers **stems, synonyms, and word order**, improving semantic evaluation over BLEU, which relies on exact n-gram matches.

**Q3. Which ROUGE variants are most commonly used?**  
A: ROUGE-1 (unigrams), ROUGE-2 (bigrams), ROUGE-L (longest common subsequence).

**Q4. Why combine ROUGE and METEOR for evaluation?**  
A: ROUGE captures **coverage and sequence overlap**, while METEOR captures **semantic similarity and ordering**, providing a more comprehensive evaluation.

**Q5. Give an example of a task where METEOR is preferred over ROUGE.**  
A: Machine translation, where **synonyms and sentence structure variations** are common.

 

## Key Takeaways

- **ROUGE:** Focuses on **n-gram and sequence overlap**, emphasizing coverage.  
- **METEOR:** Incorporates **semantic similarity, stems, synonyms, and word order**.  
- Both metrics are essential for **evaluating summarization, translation, and generation tasks**.  
- Using multiple metrics ensures **robust assessment of model quality and meaning preservation**.
