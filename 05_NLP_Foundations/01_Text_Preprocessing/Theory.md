# Text Preprocessing

You're baking a cake. Before mixing anything, you wash the vegetables, peel off the skin, and chop them to the right size. You can't throw a muddy carrot straight into the batter. Raw text is exactly like that muddy carrot — messy, inconsistent, and full of stuff a model doesn't need.

👉 This is why we need **Text Preprocessing** — to clean raw text into a form models can actually learn from.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[The full preprocessing pipeline](#the-full-preprocessing-pipeline) · [Stemming vs Lemmatization](#5-stemming-vs-lemmatization) · [Step by step](#step-by-step)

**Should Learn** — important for real projects and interviews:
[Do you always need all steps](#do-you-always-need-all-steps) · [Quick comparison: Stemming vs Lemmatization](#quick-comparison-stemming-vs-lemmatization)

**Good to Know** — useful in specific situations, not needed daily:
[The problem with raw text](#the-problem-with-raw-text)

---

## The problem with raw text

Three tweets, same meaning, completely different to a model:

```
"OMG I LOVE this product!!! 😍😍 sooo good #bestever"
"i love this product"
"I LOVE THIS PRODUCT."
```

Preprocessing makes them consistent.

---

## The full preprocessing pipeline

```mermaid
flowchart TD
    A[Raw Text] --> B[Lowercase]
    B --> C[Remove Punctuation]
    C --> D[Remove Stopwords]
    D --> E[Tokenize]
    E --> F[Stem or Lemmatize]
    F --> G[Clean Tokens]
```

---

## Step by step

### 1. Lowercasing
```
"I Love NLP" → "i love nlp"
```

### 2. Remove punctuation
```
"Hello, world!" → "Hello world"
```

### 3. Remove stopwords

Very common words carrying little meaning ("the", "is", "a", "and") are removed to reduce noise and shrink vocabulary.
```
"the cat sat on the mat" → "cat sat mat"
```

### 4. Tokenization

Split text into individual tokens. Covered in depth in Topic 02.
```
"clean text here" → ["clean", "text", "here"]
```

### 5. Stemming vs Lemmatization

Both reduce words to root form but work differently.

**Stemming** — chops off word endings. Fast but crude:
```
"running" → "run"
"studies" → "studi"   ← not a real word
```

**Lemmatization** — uses a dictionary to find the actual base form. Slower but accurate:
```
"studies" → "study"
"better"  → "good"    ← knows it's an adjective
```

**Which to use?** Lemmatization for accuracy. Stemming for quick prototypes or speed.

---

## Do you always need all steps?

| Task | Skip what? |
|---|---|
| Sentiment analysis | Maybe keep punctuation (! matters) |
| Topic classification | Remove stopwords aggressively |
| Machine translation | Don't remove anything — structure matters |
| Search | Light preprocessing — preserve intent |

---

## Quick comparison: Stemming vs Lemmatization

| Feature | Stemming | Lemmatization |
|---|---|---|
| Speed | Fast | Slower |
| Output | May not be real word | Always real word |
| Uses dictionary? | No | Yes |
| Example | "studies" → "studi" | "studies" → "study" |
| Best for | Quick tasks | Accuracy-critical tasks |

---

✅ **What you just learned:** Text preprocessing is the cleaning pipeline that turns messy raw text into consistent tokens a model can work with.

🔨 **Build this now:** Take 5 random tweets or product reviews. Run them through the full pipeline manually — lowercase, strip punctuation, remove stopwords, lemmatize. Compare before and after.

➡️ **Next step:** Tokenization → `05_NLP_Foundations/02_Tokenization/Theory.md`


---

## 📝 Practice Questions

- 📝 [Q30 · text-preprocessing](../../ai_practice_questions_100.md#q30--normal--text-preprocessing)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [12 Training Techniques](../../04_Neural_Networks_and_Deep_Learning/12_Training_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tokenization](../02_Tokenization/Theory.md)
