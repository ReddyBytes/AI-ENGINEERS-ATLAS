# 09 — RAG Systems

RAG stands for Retrieval-Augmented Generation. It's the technique that lets an LLM answer questions about your private data, recent events, or any information that wasn't in its training data.

## The Core Idea

Instead of fine-tuning a model or hoping it already knows the answer, you:
1. Retrieve the relevant information from your own data store
2. Give that information to the LLM as context
3. Let the LLM generate an answer grounded in that context

The result: accurate, up-to-date, source-cited answers from any knowledge base.

## What you'll learn

By the end of this section, you can build a complete RAG pipeline from scratch:

- Ingest documents in any format (PDF, web, CSV)
- Split them into searchable chunks
- Embed and index them in a vector database
- Retrieve the right context for any question
- Assemble it into a prompt and generate a grounded answer
- Evaluate how well your RAG system performs
- Build and troubleshoot a real PDF Q&A application

## Topics

| # | Topic | What it covers |
|---|-------|----------------|
| 01 | [RAG Fundamentals](./01_RAG_Fundamentals/) | What RAG is, why it exists, RAG vs fine-tuning |
| 02 | [Document Ingestion](./02_Document_Ingestion/) | Loading PDFs, web pages, CSVs, databases |
| 03 | [Chunking Strategies](./03_Chunking_Strategies/) | Fixed-size, recursive, semantic chunking |
| 04 | [Embedding and Indexing](./04_Embedding_and_Indexing/) | Embed chunks, store in vector DB |
| 05 | [Retrieval Pipeline](./05_Retrieval_Pipeline/) | Query → top-K chunks → return context |
| 06 | [Context Assembly](./06_Context_Assembly/) | Build the prompt with retrieved context |
| 07 | [Advanced RAG Techniques](./07_Advanced_RAG_Techniques/) | Hybrid search, reranking, query transformation |
| 08 | [RAG Evaluation](./08_RAG_Evaluation/) | RAGAS metrics, faithfulness, relevancy |
| 09 | [Build a RAG App](./09_Build_a_RAG_App/) | End-to-end PDF Q&A project |

## Prerequisites

Finish these first:
- **08_LLM_Applications/04_Embeddings** — know what embeddings are
- **08_LLM_Applications/05_Vector_Databases** — know how to use ChromaDB

## Full Pipeline Map

See [Full_Pipeline_Overview.md](./Full_Pipeline_Overview.md) for a single-page view of the entire system.

---

> "RAG is the most practical AI technique you can learn. It turns a generic language model into an expert on any knowledge base — in hours, not months."
