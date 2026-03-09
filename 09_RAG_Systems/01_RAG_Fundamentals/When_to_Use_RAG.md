# When to Use RAG vs Other Approaches

A decision guide for choosing between RAG, fine-tuning, pure prompting, and retrieval-only.

---

## The Options

| Approach | What it does |
|----------|-------------|
| **Pure prompting** | LLM answers from training data + whatever you put in the prompt |
| **RAG** | Retrieve relevant docs at runtime, then generate from them |
| **Fine-tuning** | Train the model on your specific data to change its behavior |
| **Retrieval-only** | Return documents directly without LLM generation |

---

## Comparison Table

| Criterion | Pure Prompting | RAG | Fine-tuning | Retrieval-only |
|-----------|---------------|-----|-------------|----------------|
| **Setup time** | Minutes | Hours | Days–weeks | Hours |
| **Cost** | Very low | Low | High | Low |
| **Knowledge cutoff** | Limited to training data | Real-time (your docs) | Limited to training data | Real-time |
| **Private data** | No | Yes | Yes (but data in model) | Yes |
| **Source citation** | No | Yes | No | Yes |
| **Hallucination risk** | High | Low (if grounded) | Medium | None |
| **Behavior customization** | Medium (via prompt) | Low | High | N/A |
| **Scalable knowledge** | No | Yes (millions of docs) | No (training limit) | Yes |
| **Auditability** | Low | High | Low | High |

---

## Decision Flowchart

```
Start: What are you building?
│
├── Q1: Does the task need information beyond model training?
│   ├── No → Pure prompting may be enough
│   └── Yes → Continue
│
├── Q2: Is the knowledge in documents/databases you own?
│   ├── No (need real-time web) → Web search + agent
│   └── Yes → Continue
│
├── Q3: Does the knowledge change frequently?
│   ├── Yes → RAG (update docs, not model)
│   └── No → Continue
│
├── Q4: Do you need source citations?
│   ├── Yes → RAG
│   └── No → Continue
│
├── Q5: Do you need specific behavior/tone/task patterns?
│   ├── Yes → Fine-tuning (possibly + RAG)
│   └── No → RAG
```

---

## Scenario Guide

### Use Pure Prompting When:
- The knowledge is general and the model already knows it
- The corpus is small enough to fit in context (< 50K tokens)
- You need a quick answer without infrastructure
- The task is about reasoning, writing style, or formatting — not factual recall

**Example:** "Summarize this article I'm pasting below." — just put the article in the prompt.

---

### Use RAG When:
- You have a private knowledge base (company docs, support tickets, legal contracts)
- Knowledge updates frequently (weekly reports, news, policies)
- You need accurate, citable answers
- Your corpus is too large for the context window
- Users need to trust the source of information

**Examples:**
- "What is our current refund policy?" (company handbook)
- "What did this client say in last week's meeting?" (meeting notes)
- "What's in our product documentation about this feature?" (tech docs)

---

### Use Fine-tuning When:
- You need the model to learn a specific style, tone, or format it never does naturally
- You want to embed a specific task behavior (e.g., always output a specific JSON structure)
- You're making millions of calls and want to remove long system prompts (reduce token cost)
- RAG + prompting consistently fails on a task despite good retrieval

**Examples:**
- Train a model to always respond in a specific legal brief format
- Train on code examples to improve completion for a proprietary API
- Distill a large model's behavior into a smaller, cheaper model

---

### Use Retrieval-only When:
- You want to give users the raw source documents, not generated text
- The application is search, not Q&A (users want to find relevant docs, not get answers)
- You can't risk LLM hallucination at all

**Examples:**
- Legal discovery tool: find contracts containing specific clauses
- Internal search: surface relevant engineering runbooks for an incident
- E-commerce product search: return product listings

---

### RAG + Fine-tuning Together:
When you need both: the domain knowledge of RAG AND the behavioral consistency of fine-tuning.

**Example:** A medical AI that needs to:
- Retrieve specific patient records and clinical guidelines (RAG)
- Always structure responses in a specific clinical format and tone (fine-tuning)

---

## Cost Comparison

| Approach | One-time cost | Per-query cost |
|----------|---------------|---------------|
| Pure prompting | None | API tokens |
| RAG | Hours of setup + vector DB | API tokens + retrieval (~negligible) |
| Fine-tuning | $100–$10,000+ for training | API tokens (usually cheaper model) |
| RAG + Fine-tuning | Fine-tuning cost + setup | Cheapest per-query (smaller model) |

---

## The Bottom Line

**Default choice for knowledge-intensive Q&A tasks: RAG.**

It's fast to deploy, doesn't require training data, keeps knowledge updatable, enables source citation, and scales to millions of documents. Fine-tuning adds behavioral consistency on top when needed.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **When_to_Use_RAG.md** | ← you are here |

⬅️ **Prev:** [08 Streaming Responses](../../08_LLM_Applications/08_Streaming_Responses/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md)
