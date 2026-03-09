# Tokenization — Code Example

## NLTK word_tokenize vs HuggingFace tokenizer

```python
# pip install nltk transformers

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from transformers import AutoTokenizer

sentences = [
    "The unbelievable transformation surprised everyone.",
    "ChatGPT is an AI model built by OpenAI.",
    "I don't like tokenization problems!",
    "Supercalifragilisticexpialidocious is a long word.",
]

# ─────────────────────────────────────────
# NLTK word tokenizer
# ─────────────────────────────────────────
print("=" * 60)
print("NLTK word_tokenize")
print("=" * 60)

for sent in sentences:
    tokens = word_tokenize(sent)
    print(f"Input:  {sent}")
    print(f"Tokens: {tokens}")
    print(f"Count:  {len(tokens)}")
    print("-" * 60)
```

**NLTK output:**

```
Input:  The unbelievable transformation surprised everyone.
Tokens: ['The', 'unbelievable', 'transformation', 'surprised', 'everyone', '.']
Count:  6

Input:  ChatGPT is an AI model built by OpenAI.
Tokens: ['ChatGPT', 'is', 'an', 'AI', 'model', 'built', 'by', 'OpenAI', '.']
Count:  9
```

---

## HuggingFace subword tokenizer (GPT-2 BPE)

```python
# Load GPT-2 tokenizer (BPE)
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")

print("=" * 60)
print("GPT-2 Tokenizer (BPE / Subword)")
print("=" * 60)

for sent in sentences:
    # encode returns token IDs
    token_ids = gpt2_tokenizer.encode(sent)
    # convert IDs back to readable tokens
    tokens = gpt2_tokenizer.convert_ids_to_tokens(token_ids)
    print(f"Input:  {sent}")
    print(f"Tokens: {tokens}")
    print(f"Count:  {len(tokens)}")
    print("-" * 60)
```

**GPT-2 output:**

```
Input:  The unbelievable transformation surprised everyone.
Tokens: ['The', 'Ġun', 'believ', 'able', 'Ġtransformation', 'Ġsurprised', 'Ġeveryone', '.']
Count:  8

Input:  ChatGPT is an AI model built by OpenAI.
Tokens: ['Chat', 'G', 'PT', 'Ġis', 'Ġan', 'ĠAI', 'Ġmodel', 'Ġbuilt', 'Ġby', 'ĠOpen', 'AI', '.']
Count:  12
```

Note: `Ġ` is GPT-2's way of marking a space before a token.

---

## BERT tokenizer (WordPiece)

```python
# Load BERT tokenizer (WordPiece)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

print("=" * 60)
print("BERT Tokenizer (WordPiece / Subword)")
print("=" * 60)

for sent in sentences:
    tokens = bert_tokenizer.tokenize(sent)
    print(f"Input:  {sent}")
    print(f"Tokens: {tokens}")
    print(f"Count:  {len(tokens)}")
    print("-" * 60)
```

**BERT output:**

```
Input:  The unbelievable transformation surprised everyone.
Tokens: ['the', 'un', '##believable', 'transformation', 'surprised', 'everyone', '.']
Count:  7

Input:  Supercalifragilisticexpialidocious is a long word.
Tokens: ['super', '##cal', '##ifrag', '##ilistic', '##exp', '##ial', '##ido', '##cious', 'is', 'a', 'long', 'word', '.']
Count:  13
```

Note: `##` in BERT means "this is a continuation of the previous token, not the start of a new word".

---

## Side-by-side comparison

```python
# Compare token counts across tokenizers
print(f"{'Sentence':<45} {'NLTK':>6} {'GPT-2':>6} {'BERT':>6}")
print("-" * 65)

for sent in sentences:
    nltk_count = len(word_tokenize(sent))
    gpt2_count = len(gpt2_tokenizer.encode(sent))
    bert_count = len(bert_tokenizer.tokenize(sent))
    # Truncate sentence for display
    display = sent[:42] + "..." if len(sent) > 42 else sent
    print(f"{display:<45} {nltk_count:>6} {gpt2_count:>6} {bert_count:>6}")
```

**Output:**

```
Sentence                                       NLTK  GPT-2   BERT
-----------------------------------------------------------------
The unbelievable transformation surprised...      6      8      7
ChatGPT is an AI model built by OpenAI.           9     12      9
I don't like tokenization problems!               7      8      7
Supercalifragilisticexpialidocious is a lo...     5     14     13
```

---

## Key insight: subword handles unknown words

```python
# Test OOV handling
oov_words = ["ChatGPT", "blockchain", "unbelievableness", "zoomcall"]

print(f"{'Word':<25} {'GPT-2 tokens':<35} {'BERT tokens'}")
print("-" * 80)

for word in oov_words:
    gpt2_tokens = gpt2_tokenizer.tokenize(word)
    bert_tokens = bert_tokenizer.tokenize(word)
    print(f"{word:<25} {str(gpt2_tokens):<35} {str(bert_tokens)}")
```

**Output:**

```
Word                      GPT-2 tokens                        BERT tokens
--------------------------------------------------------------------------------
ChatGPT                   ['Chat', 'G', 'PT']                 ['chat', '##gp', '##t']
blockchain                ['block', 'chain']                  ['blockchain']
unbelievableness          ['un', 'believ', 'able', 'ness']    ['un', '##believable', '##ness']
zoomcall                  ['zoom', 'call']                    ['zoom', '##call']
```

None of these returned [UNK]. Subword tokenization handles all of them gracefully.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [01 Text Preprocessing](../01_Text_Preprocessing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md)
