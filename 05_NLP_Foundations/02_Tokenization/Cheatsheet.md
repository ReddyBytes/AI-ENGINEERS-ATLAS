# Tokenization — Cheatsheet

**One-liner:** Tokenization splits raw text into the smallest units (tokens) a model can process — words, subwords, or characters.

---

## Key Terms

| Term | Definition |
|---|---|
| Token | The basic unit of text a model processes |
| Tokenizer | The tool/algorithm that performs tokenization |
| Vocabulary | The full set of tokens a model knows |
| OOV | Out-of-Vocabulary — a token the model has never seen |
| BPE | Byte Pair Encoding — merges frequent character pairs into subwords |
| WordPiece | Google's subword method used in BERT |
| SentencePiece | Language-agnostic tokenizer that treats text as raw bytes |
| Context window | Max number of tokens a model can process at once |

---

## Tokenization types

| Type | Split on | Pros | Cons |
|---|---|---|---|
| Word | Spaces/punctuation | Simple, readable | OOV problem |
| Subword (BPE) | Frequent byte pairs | No OOV, compact | Less readable |
| Character | Each character | No OOV | Very long sequences |
| Sentence | Sentences | For sentence-level tasks | Needs sentence boundary detection |

---

## Token count rule of thumb

- 1 English word ≈ 1.3 tokens (in GPT tokenizers)
- 100 tokens ≈ 75 words
- 1 page of text ≈ 500–700 tokens

---

## When to use what

| Scenario | Recommended tokenizer |
|---|---|
| Using GPT models | Built-in BPE tokenizer (tiktoken) |
| Using BERT | WordPiece tokenizer (via HuggingFace) |
| Multilingual tasks | SentencePiece |
| Simple rule-based NLP | NLTK word_tokenize |
| Research baseline | spaCy tokenizer |

---

## Golden Rules

1. Always use the same tokenizer that the model was pretrained with.
2. Token ≠ word — always count tokens, not words, for LLM context limits.
3. Subword tokenization is the modern default — it handles OOV gracefully.
4. Never tokenize your training and test data separately — fit once, transform both.
5. Special tokens like [CLS], [SEP], [PAD] count toward the token limit.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [01 Text Preprocessing](../01_Text_Preprocessing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md)
