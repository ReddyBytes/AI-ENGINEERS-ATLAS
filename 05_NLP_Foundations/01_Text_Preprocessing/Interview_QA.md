# Text Preprocessing — Interview Q&A

## Beginner

**Q1. What is text preprocessing and why is it needed?**

Text preprocessing is the set of steps you apply to raw text to clean and standardize it before feeding it to a model. Raw text is messy — it has inconsistent capitalization, punctuation, irrelevant words, and varied forms of the same word. Models learn better from clean, consistent input. Without preprocessing, the same word appearing as "Run", "run", and "running" looks like three different things.

---

**Q2. What is the difference between stemming and lemmatization?**

Both reduce words to a base form, but they work differently.

Stemming just chops off word endings using simple rules. It's fast but can produce non-words — "studies" becomes "studi".

Lemmatization uses a dictionary and understands grammar. It returns real base forms — "studies" becomes "study", "better" becomes "good". Lemmatization is more accurate but slower.

Use stemming when speed matters and accuracy is secondary. Use lemmatization for anything where precision counts.

---

**Q3. What are stopwords? Should you always remove them?**

Stopwords are very common words that appear in almost every sentence and carry little meaning on their own: "the", "a", "is", "of", "and". Removing them reduces noise and shrinks vocabulary size.

But you should not always remove them. For machine translation or summarization, word order and grammar matter — stopwords are part of that structure. For sentiment analysis, "not" is technically a stopword but is critical for meaning ("not good" vs "good"). Always think about whether a word matters for your specific task.

---

## Intermediate

**Q4. How does preprocessing affect model performance in classification tasks?**

Preprocessing directly affects what vocabulary the model sees and how consistently it appears. Good preprocessing can improve accuracy by reducing noise and making training patterns clearer. Poor preprocessing can hurt performance — for example, removing stopwords in a task where word order matters, or applying stemming that destroys meaningful distinctions between words.

A common pitfall is data leakage: applying preprocessing differently to training vs test data. The same pipeline must be applied consistently to both.

---

**Q5. How would you build a preprocessing pipeline for a production NLP system?**

A production pipeline should be modular, consistent, and reproducible. Key design choices:

- Wrap each step as a function or sklearn transformer so it can be pipelined
- Fit any stateful steps (like a stopword list or vocab) on training data only
- Apply exactly the same steps in inference as in training
- Log what preprocessing was applied so it's reproducible
- Handle edge cases: empty strings, None values, non-English characters

Using sklearn's `Pipeline` class or spaCy's processing pipeline makes this clean and testable.

---

**Q6. What preprocessing steps would you skip for a neural network vs a traditional ML model?**

Traditional ML models (like Naive Bayes or SVM with TF-IDF) benefit from aggressive preprocessing: remove stopwords, stem/lemmatize, lowercase. They work on hand-crafted features.

Neural networks — especially pretrained transformers like BERT — often do their own internal tokenization and have learned to handle casing and punctuation. For BERT, you typically just use the model's built-in tokenizer with minimal manual preprocessing. Stripping too much can actually hurt performance because the model was pretrained on relatively raw text.

---

## Advanced

**Q7. How does preprocessing interact with out-of-vocabulary (OOV) issues?**

OOV words are words in test data that the model never saw during training. Aggressive preprocessing like stemming can reduce OOV by collapsing word variants to a common root — "running", "ran", "runs" all become "run", which is likely in the vocabulary. However, stemming can also create non-words that aren't in any vocabulary. Lemmatization is better for OOV reduction because it maps to real dictionary words.

In subword tokenization (used by BERT, GPT), OOV is largely solved by splitting unknown words into known subword pieces. Preprocessing is less critical there.

---

**Q8. What are the trade-offs of removing punctuation from text?**

Removing punctuation reduces vocabulary size and noise for bag-of-words models. But it can destroy information in certain tasks:

- Sentiment: "Wow!!!" vs "Wow." carry different intensities
- Sarcasm detection: punctuation is a strong cue
- Code analysis: punctuation is syntax
- Question classification: "?" identifies questions

For most classification tasks on general text, removing punctuation helps. For fine-grained sentiment or dialogue understanding, preserve it or encode it separately.

---

**Q9. How would you handle preprocessing for a multilingual NLP system?**

Multilingual preprocessing is harder because rules differ across languages. Key challenges:

- Tokenization: Chinese and Japanese don't use spaces between words
- Stopwords: every language has its own list
- Stemming/lemmatization: language-specific algorithms needed
- Encoding: always use UTF-8 consistently

Solutions include using language-detection libraries first, then routing to language-specific preprocessing pipelines. For neural models, multilingual tokenizers like the one in mBERT or XLM-R handle much of this automatically using subword tokenization across 100+ languages.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [12 Training Techniques](../../04_Neural_Networks_and_Deep_Learning/12_Training_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tokenization](../02_Tokenization/Theory.md)
