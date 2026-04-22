# Ollama — Local LLM Inference Cheatsheet

## Quick Start

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull and run a model
ollama pull llama3.2
ollama run llama3.2

# Start the API server (without interactive session)
ollama serve &

# List downloaded models
ollama list

# Show model details
ollama show llama3.2

# Remove a model
ollama rm llama3.2
```

---

## Model Size Guide

| Model | Params | Q4 Size | Min VRAM | Best For |
|---|---|---|---|---|
| **phi4-mini** | 3.8B | ~2.3 GB | 4 GB (CPU ok) | Fast chat, embedded |
| **llama3.2** | 3B | ~2.0 GB | 4 GB | General purpose |
| **mistral** | 7B | ~4.1 GB | 6 GB | Coding, instruction |
| **llama3.1** | 8B | ~4.9 GB | 8 GB | Strong general |
| **gemma2** | 9B | ~5.4 GB | 8 GB | Balanced quality |
| **llama3.1** | 70B | ~40 GB | 48 GB | Near-frontier quality |
| **deepseek-r1** | 7B distilled | ~4.7 GB | 8 GB | Reasoning tasks |
| **nomic-embed-text** | — | ~274 MB | CPU ok | Embeddings for RAG |

---

## Python Library

```python
import ollama

# Chat
response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Your prompt here"}]
)
print(response["message"]["content"])

# Streaming chat
for chunk in ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Your prompt"}],
    stream=True,
):
    print(chunk["message"]["content"], end="", flush=True)

# Generation (non-chat)
response = ollama.generate(model="llama3.2", prompt="Complete this: The sky is")
print(response["response"])

# Embeddings
result = ollama.embed(model="nomic-embed-text", input="Your text here")
embedding = result["embeddings"][0]   # list of floats

# List models
models = ollama.list()
```

---

## REST API

```python
import requests

BASE = "http://localhost:11434"

# Chat
resp = requests.post(f"{BASE}/api/chat", json={
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": False,
})
print(resp.json()["message"]["content"])

# Embed
resp = requests.post(f"{BASE}/api/embed", json={
    "model": "nomic-embed-text",
    "input": "text to embed",
})
embedding = resp.json()["embeddings"][0]

# List models
resp = requests.get(f"{BASE}/api/tags")
models = resp.json()["models"]
```

---

## OpenAI-Compatible Client (Drop-in Replacement)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",           # required but ignored by Ollama
)

response = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"},
    ],
    temperature=0.7,
    max_tokens=500,
)
print(response.choices[0].message.content)

# Embeddings via OpenAI-compatible endpoint
embedding = client.embeddings.create(
    model="nomic-embed-text",
    input="text to embed",
).data[0].embedding
```

---

## LangChain Integration

```python
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate

# LLM
llm = OllamaLLM(model="llama3.2", temperature=0.7)
response = llm.invoke("Explain gradient descent in 2 sentences")

# Embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectors = embeddings.embed_documents(["doc 1", "doc 2", "doc 3"])
query_vector = embeddings.embed_query("search query")

# Chain
prompt = ChatPromptTemplate.from_template("Answer the question: {question}")
chain = prompt | llm
print(chain.invoke({"question": "What is RAG?"}))
```

---

## Local RAG in 30 Lines

```python
import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "RAG (Retrieval-Augmented Generation) combines retrieval with LLM generation.",
    "Transformers use self-attention to model long-range dependencies.",
    "Gradient descent minimizes the loss by following the negative gradient.",
]

def embed(text):
    return ollama.embed(model="nomic-embed-text", input=text)["embeddings"][0]

# Index documents
doc_embeddings = np.array([embed(d) for d in docs])

def answer(question, top_k=1):
    q_emb = np.array([embed(question)])
    sims = cosine_similarity(q_emb, doc_embeddings)[0]
    top_idx = sims.argsort()[::-1][:top_k]
    context = "\n".join(docs[i] for i in top_idx)
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}]
    )
    return response["message"]["content"]

print(answer("What does RAG stand for?"))
```

---

## Ollama vs Cloud API Comparison

| Factor | Ollama (Local) | Cloud API (OpenAI/Anthropic) |
|---|---|---|
| **Data privacy** | Complete — data never leaves | Trust cloud provider |
| **Cost at scale** | Hardware + electricity only | Per-token pricing |
| **Setup time** | Minutes | Instant (just API key) |
| **Model quality** | Good (open source) | Best (frontier models) |
| **Latency** | Fast with GPU, slow on CPU | Consistent, low |
| **Offline use** | Yes | No |
| **Context window** | Typically 8K–128K | 200K+ (Claude, GPT-4) |
| **Multimodal** | Limited (Llava) | Strong (Claude 3, GPT-4V) |

---

## Quantization Reference

| Format | Quality | VRAM Multiplier vs F16 |
|---|---|---|
| F16 | Reference | 1.0× |
| Q8_0 | Excellent | ~0.5× |
| **Q4_K_M** | **Good (recommended)** | **~0.25×** |
| Q3_K_M | Acceptable | ~0.19× |
| Q2_K | Degraded | ~0.13× |

---

## Golden Rules

1. Check VRAM before pulling — `ollama show <model>` displays size requirements
2. Q4_K_M is the default and best balance of quality vs memory — don't override unless you have specific needs
3. Use `ollama serve` + the OpenAI-compatible client to reuse existing SDK code
4. For RAG, use `nomic-embed-text` or `mxbai-embed-large` as your local embedding model
5. On Apple Silicon, Ollama uses Metal acceleration automatically — no configuration needed
