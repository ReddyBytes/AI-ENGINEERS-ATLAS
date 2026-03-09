# Text Preprocessing — Cheatsheet

**One-liner:** Text preprocessing is the pipeline that cleans and standardizes raw text before feeding it to a model.

---

## Key Terms

| Term | Definition |
|---|---|
| Preprocessing | The full pipeline of cleaning text before modeling |
| Lowercasing | Converting all characters to lowercase |
| Stopwords | Common words with little meaning ("the", "is", "a") |
| Tokenization | Splitting text into individual units (words, subwords) |
| Stemming | Chopping word endings to get a crude root form |
| Lemmatization | Using a dictionary to find the true base form of a word |
| Corpus | A collection of text documents used for training |
| Noise | Parts of text that don't help the model (URLs, special chars) |

---

## When to use / not use

| Step | Use when | Skip when |
|---|---|---|
| Lowercasing | Classification, search, embeddings | Proper nouns matter (NER) |
| Remove punctuation | Bag of words, topic modeling | Sentiment (! counts), translation |
| Remove stopwords | Topic modeling, TF-IDF | Translation, summarization |
| Stemming | Speed matters, rough prototypes | Need real words in output |
| Lemmatization | Accuracy matters, chatbots, search | Very large scale, speed critical |

---

## Stemming vs Lemmatization

| | Stemming | Lemmatization |
|---|---|---|
| Output | May be non-word ("studi") | Always valid word ("study") |
| Speed | Fast | Slower |
| Needs POS tag? | No | Sometimes yes |
| Library | NLTK PorterStemmer | NLTK WordNetLemmatizer, spaCy |

---

## Full pipeline at a glance

```
Raw text
  → lowercase
  → remove punctuation & special chars
  → remove stopwords
  → tokenize
  → stem OR lemmatize
  → clean token list
```

---

## Golden Rules

1. Preprocessing decisions change your results — always experiment.
2. Never preprocess away information your model needs.
3. Lemmatization > Stemming when accuracy matters.
4. Stopword lists are not one-size-fits-all — customize them.
5. Always apply the same preprocessing to training data AND test/production data.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [12 Training Techniques](../../04_Neural_Networks_and_Deep_Learning/12_Training_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tokenization](../02_Tokenization/Theory.md)
