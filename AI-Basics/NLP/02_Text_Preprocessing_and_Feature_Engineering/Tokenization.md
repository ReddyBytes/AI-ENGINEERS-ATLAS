# Tokenization

Imagine you are reading a news article and want to summarize it. You naturally break the sentences into **words or meaningful phrases** to understand the content. For instance, “The quick brown fox jumps over the lazy dog” is split into individual words to capture the meaning. Similarly, computers cannot understand raw sentences unless we **divide them into smaller units called tokens**. This is why we need **Tokenization** — to split text into meaningful pieces that machines can process effectively.

# What is Tokenization?

Tokenization is the process of **splitting text into smaller units (tokens)** such as words, subwords, or characters. These tokens serve as the fundamental input for NLP models.  

### Types of Tokenization:

1. **Word Tokenization**
   - Splits text into individual words based on spaces or punctuation.  
   - Example: “I love NLP” → [“I”, “love”, “NLP”]  
   - Used in traditional NLP tasks like sentiment analysis and text classification.

2. **Subword Tokenization**
   - Breaks words into smaller units to handle rare or unseen words.  
   - Example: “unhappiness” → [“un”, “happi”, “ness”]  
   - Widely used in modern transformers like BERT and GPT.

3. **Character Tokenization**
   - Splits text into single characters.  
   - Example: “cat” → [“c”, “a”, “t”]  
   - Useful for languages without clear word boundaries, misspellings, or NLP tasks like spelling correction.

4. **Sentence Tokenization**
   - Splits text into sentences for tasks like summarization or machine translation.  
   - Example: “I love NLP. It is powerful.” → [“I love NLP.”, “It is powerful.”]

 

## Why do we need Tokenization?

- Computers cannot process raw sentences directly; **structured tokens are required**.  
- Proper tokenization ensures **accurate representation of words and context**.  
- Without tokenization:
  - Models may **misinterpret words or phrases**.  
  - Important semantic or syntactic information could be lost.  
  - NLP tasks like translation, summarization, and sentiment analysis **fail or produce poor results**.

*Example*: Without tokenization, “New York” might be treated as two unrelated words, losing context.

 

## Interview Q&A

**Q1. What is tokenization in NLP?**  
A: Tokenization is the process of splitting text into smaller units called tokens (words, subwords, characters, or sentences) for machine processing.

**Q2. Why is subword tokenization important in modern NLP models?**  
A: It handles **rare or out-of-vocabulary words**, allowing models like BERT or GPT to process unseen words efficiently.

**Q3. How can tokenization affect model performance?**  
A: Poor tokenization can **break context, inflate vocabulary, or create ambiguous tokens**, which reduces accuracy and efficiency.

**Q4. What is the difference between word and character tokenization?**  
A: Word tokenization splits text into words, whereas character tokenization splits it into individual characters. Character tokenization is helpful for languages without spaces or for handling typos.

 

## Key Takeaways

- Tokenization is the **first step in NLP pipelines**, converting raw text into manageable units.  
- Tokens can be **words, subwords, characters, or sentences** depending on the task.  
- Proper tokenization is critical for **accurate representation, context preservation, and downstream model performance**.  
- The choice of tokenization technique depends on **language, task complexity, and model requirements**.
