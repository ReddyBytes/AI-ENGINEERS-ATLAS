# Text Preprocessing — Code Example

## Full Python Preprocessing Pipeline

```python
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (run once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt_tab')

# ─────────────────────────────────────────
# Sample raw text
# ─────────────────────────────────────────
raw_texts = [
    "OMG I LOVE this product!!! 😍 It's sooo good #bestever",
    "Running in the park is BETTER than going to the gym!!!",
    "The studies show that children's books are highly beneficial.",
    "I don't like this at ALL... terrible experience.",
]

# ─────────────────────────────────────────
# Step 1: Lowercase
# ─────────────────────────────────────────
def to_lowercase(text):
    return text.lower()

# ─────────────────────────────────────────
# Step 2: Remove punctuation and special characters
# ─────────────────────────────────────────
def remove_punctuation(text):
    # Keep only letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─────────────────────────────────────────
# Step 3: Remove stopwords
# ─────────────────────────────────────────
STOPWORDS = set(stopwords.words('english'))

def remove_stopwords(tokens):
    return [token for token in tokens if token not in STOPWORDS]

# ─────────────────────────────────────────
# Step 4: Lemmatize
# ─────────────────────────────────────────
lemmatizer = WordNetLemmatizer()

def lemmatize(tokens):
    return [lemmatizer.lemmatize(token) for token in tokens]

# ─────────────────────────────────────────
# Full pipeline
# ─────────────────────────────────────────
def preprocess(text):
    # Step 1: lowercase
    text = to_lowercase(text)
    # Step 2: remove punctuation/special chars
    text = remove_punctuation(text)
    # Step 3: tokenize
    tokens = word_tokenize(text)
    # Step 4: remove stopwords
    tokens = remove_stopwords(tokens)
    # Step 5: lemmatize
    tokens = lemmatize(tokens)
    return tokens

# ─────────────────────────────────────────
# Run it
# ─────────────────────────────────────────
print("=" * 60)
for raw in raw_texts:
    clean = preprocess(raw)
    print(f"Raw:   {raw}")
    print(f"Clean: {clean}")
    print("-" * 60)
```

**Expected output:**

```
============================================================
Raw:   OMG I LOVE this product!!! 😍 It's sooo good #bestever
Clean: ['omg', 'love', 'product', 'sooo', 'good', 'bestever']
------------------------------------------------------------
Raw:   Running in the park is BETTER than going to the gym!!!
Clean: ['running', 'park', 'better', 'going', 'gym']
------------------------------------------------------------
Raw:   The studies show that children's books are highly beneficial.
Clean: ['study', 'show', 'child', 'book', 'highly', 'beneficial']
------------------------------------------------------------
Raw:   I don't like this at ALL... terrible experience.
Clean: ['like', 'terrible', 'experience']
------------------------------------------------------------
```

---

## Stemming comparison (bonus)

```python
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

words = ["running", "studies", "better", "children", "beneficial"]

print(f"{'Word':<15} {'Stemmed':<15} {'Lemmatized':<15}")
print("-" * 45)
for word in words:
    stemmed = stemmer.stem(word)
    lemmatized = lemmatizer.lemmatize(word)
    print(f"{word:<15} {stemmed:<15} {lemmatized:<15}")
```

**Output:**

```
Word            Stemmed         Lemmatized
---------------------------------------------
running         run             running
studies         studi           study
better          better          better
children        children        child
beneficial      benefici        beneficial
```

Notice: "studies" → "studi" from stemmer (not a real word), but "study" from lemmatizer (real word).

---

## Building a reusable pipeline with sklearn

```python
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

class TextCleaner(BaseEstimator, TransformerMixin):
    """Sklearn-compatible text preprocessing transformer."""

    def __init__(self, remove_stops=True, do_lemmatize=True):
        self.remove_stops = remove_stops
        self.do_lemmatize = do_lemmatize
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))

    def fit(self, X, y=None):
        return self  # nothing to fit

    def transform(self, X):
        return [self._clean(text) for text in X]

    def _clean(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = word_tokenize(text)
        if self.remove_stops:
            tokens = [t for t in tokens if t not in self.stopwords]
        if self.do_lemmatize:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        return ' '.join(tokens)  # return string for downstream vectorizer


# Usage
cleaner = TextCleaner(remove_stops=True, do_lemmatize=True)
result = cleaner.transform(raw_texts)
for r in result:
    print(r)
```

**Output:**

```
omg love product sooo good bestever
running park better going gym
study show child book highly beneficial
like terrible experience
```

This string output is ready to feed directly into `CountVectorizer` or `TfidfVectorizer`.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [12 Training Techniques](../../04_Neural_Networks_and_Deep_Learning/12_Training_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tokenization](../02_Tokenization/Theory.md)
