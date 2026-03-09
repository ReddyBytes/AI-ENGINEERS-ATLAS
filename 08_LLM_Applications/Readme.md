# 08 — LLM Applications

This section covers how to build real things with large language models. Not just chat — actual tools, pipelines, and systems.

## What you'll learn

By the end of this section, you'll know how to:

- Write prompts that actually work (not just "hey ChatGPT")
- Give LLMs tools so they can take actions in the world
- Get structured data out of an LLM instead of random prose
- Turn text into vectors for similarity search
- Store and search millions of documents semantically
- Build memory into your AI applications
- Stream responses for a better user experience

## Topics

| # | Topic | What it covers |
|---|-------|----------------|
| 01 | [Prompt Engineering](./01_Prompt_Engineering/) | Zero-shot, few-shot, CoT, role prompting, output formatting |
| 02 | [Tool Calling](./02_Tool_Calling/) | Function calling, the tool loop, parallel calls |
| 03 | [Structured Outputs](./03_Structured_Outputs/) | JSON mode, Pydantic, reliable parsing |
| 04 | [Embeddings](./04_Embeddings/) | Text → vectors, similarity, embedding models |
| 05 | [Vector Databases](./05_Vector_Databases/) | Chroma, Pinecone, Weaviate, HNSW indexing |
| 06 | [Semantic Search](./06_Semantic_Search/) | Embedding-based search, hybrid search, re-ranking |
| 07 | [Memory Systems](./07_Memory_Systems/) | In-context, vector, episodic, summarization |
| 08 | [Streaming Responses](./08_Streaming_Responses/) | SSE, token streaming, UX benefits |

## Prerequisites

You should have finished:
- **07_Large_Language_Models** — know what an LLM is and how it works
- **05_NLP_Foundations** — understand tokenization and embeddings at a high level

## How to use this section

Work through topics 01 → 08 in order. Each one builds on the last. Topics 04 + 05 + 06 are tightly linked — do them together.

The code examples use the **Anthropic Claude API** and **OpenAI API**. Get API keys before starting topic 01.

---

> "The difference between a good AI application and a bad one is usually the quality of the prompts and the structure around the model — not the model itself."
