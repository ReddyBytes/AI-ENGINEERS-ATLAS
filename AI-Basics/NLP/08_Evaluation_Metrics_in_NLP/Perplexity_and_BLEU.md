# Perplexity and BLEU in NLP

Imagine you are building a **machine translation system** to translate English sentences into French. You want to know how well your model performs. Two commonly used metrics are **Perplexity** (for language models) and **BLEU** (for translation quality). They help **quantitatively evaluate the performance of NLP models**.

# What are Perplexity and BLEU?

These metrics measure **different aspects of NLP model performance**:

1. **Perplexity:**  
   - Measures **how well a language model predicts a sequence of words**.  
   - Lower perplexity indicates **better prediction and understanding of language patterns**.  
   - Formula:  
     \[
     \text{Perplexity} = 2^{-\frac{1}{N} \sum_{i=1}^{N} \log_2 P(w_i | w_1, \dots, w_{i-1})}
     \]  
   - Example: If a model predicts "the cat sat on the mat," perplexity measures how surprised the model is when each word appears.

2. **BLEU (Bilingual Evaluation Understudy):**  
   - Evaluates **quality of machine-generated text** by comparing it to **one or more reference texts**.  
   - Measures **overlap of n-grams** between predicted and reference sentences.  
   - Score ranges from **0 (no match) to 1 (perfect match)**, often expressed as a percentage.  
   - Formula (simplified):  
     \[
     \text{BLEU} = BP \cdot \exp \left( \sum_{n=1}^{N} w_n \log p_n \right)
     \]  
     - \(p_n\) = precision of n-grams  
     - BP = brevity penalty for short outputs  
   - Example:  
     Reference: "The cat sits on the mat."  
     Prediction: "The cat is sitting on the mat."  
     BLEU measures n-gram overlap, giving partial credit for similar words and order.

 

### How They Work in NLP

1. **Perplexity:**  
   - Used for **language modeling tasks**.  
   - Helps compare different models or configurations.  
   - Lower perplexity → model predicts sequences **more confidently and accurately**.  

2. **BLEU:**  
   - Used for **translation, summarization, and text generation tasks**.  
   - Measures **fidelity to reference output**, considering both word choice and sequence order.  
   - Often used alongside human evaluation for better assessment.

*Example:*  
- Language model predicts the next word in a sentence. If the model confidently predicts the correct word each time, perplexity is low.  
- Machine translation: Translating "I love AI" to French "J'aime l'IA" vs. model output "J'adore l'IA." BLEU gives partial credit for overlap.

 

### Why These Metrics Are Needed

- **Perplexity:** Helps gauge **model understanding of language patterns** before deploying in generation or translation tasks.  
- **BLEU:** Measures **output quality in translation or summarization**, enabling benchmarking against references.  
- Without these metrics:
  - Developers cannot **quantify performance** of language models.  
  - Comparing or improving models becomes **difficult**.

 

### Applications

- **Perplexity:**  
  - Language modeling (GPT, LSTM, Transformer-based LM)  
  - Predictive text or autocomplete systems  
  - Speech recognition  

- **BLEU:**  
  - Machine Translation (English → French, etc.)  
  - Text Summarization  
  - Code Generation Evaluation  
  - Dialogue Systems (comparing generated replies to reference responses)  

 

## Interview Q&A

**Q1. What is perplexity in NLP?**  
A: Perplexity measures how well a language model predicts a sequence of words. Lower perplexity indicates better language modeling.

**Q2. What is BLEU score and when is it used?**  
A: BLEU evaluates the quality of generated text (translation, summarization) by comparing n-gram overlap with reference outputs.

**Q3. Can perplexity and BLEU be used together?**  
A: Yes. Perplexity evaluates the model's prediction confidence, while BLEU evaluates output **quality against references**.

**Q4. Give an example of low perplexity but low BLEU.**  
A: A model may predict grammatically correct but **incorrectly translated words** → confident predictions (low perplexity) but poor reference matching (low BLEU).

**Q5. Why is BLEU not sufficient alone for evaluation?**  
A: BLEU does not capture **semantic meaning or paraphrasing** well; human evaluation may still be required.

 

## Key Takeaways

- **Perplexity:** Measures **language model confidence and prediction accuracy**. Lower is better.  
- **BLEU:** Measures **text quality and similarity to references**, widely used in translation and summarization.  
- Both metrics are **complementary**: perplexity for model understanding, BLEU for output quality.  
- Crucial for **benchmarking NLP models** and improving text generation, translation, and summarization systems.
