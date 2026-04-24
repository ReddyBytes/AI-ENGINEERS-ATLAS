# Ollama — Local LLM Inference Interview Q&A

---

## Beginner

**Q1: What is Ollama and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

Ollama is an open-source tool that makes it trivial to run large language models locally on your own hardware. Before Ollama, running a local LLM required manually downloading multi-gigabyte model weights, configuring CUDA drivers, compiling llama.cpp, and writing custom inference code. Ollama wraps all of this into a single command: `ollama run llama3.2`. It downloads the model, handles hardware detection (GPU or CPU), and starts a local REST server at `localhost:11434`. The primary problems it solves are data privacy (healthcare, finance, and legal organizations cannot send sensitive data to external APIs), offline operation (air-gapped environments, edge devices), and cost elimination for high-volume use cases.

</details>

---

<br>

**Q2: What is model quantization and why does it matter for local inference?**

<details>
<summary>💡 Show Answer</summary>

Model quantization reduces the precision of model weights from 32-bit or 16-bit floating point numbers to lower-bit integers (typically 4-bit or 8-bit). A 7B parameter model stored in 16-bit floats requires approximately 14 GB of memory. The same model in 4-bit integers requires only ~3.5 GB. This 4x reduction makes the difference between requiring a $10,000 data center GPU and running on a $400 consumer graphics card. Ollama uses the GGUF format which stores quantized weights. The quality tradeoff from Q4 quantization is minimal — in most benchmarks, a Q4_K_M model performs within 1–3% of the full-precision version. Q4_K_M is the recommended default and what `ollama pull` downloads automatically.

</details>

---

<br>

**Q3: How is the Ollama API related to the OpenAI API?**

<details>
<summary>💡 Show Answer</summary>

Ollama exposes an OpenAI-compatible REST API at `http://localhost:11434/v1`. The endpoint paths (`/v1/chat/completions`, `/v1/embeddings`), request format (messages array with role/content), and response format are identical to OpenAI's API. This means you can use the official OpenAI Python SDK with Ollama by changing only two things: `base_url="http://localhost:11434/v1"` and `api_key="ollama"` (any string, since Ollama has no authentication). All existing OpenAI SDK code — prompting, streaming, temperature, max_tokens — works unchanged. This compatibility also means Ollama works as a drop-in backend for frameworks like LangChain and LlamaIndex.

</details>

---

## Intermediate

**Q4: What are the hardware requirements for running a 7B vs 70B model with Ollama?**

<details>
<summary>💡 Show Answer</summary>

For a 7B model at Q4 quantization (~4–5 GB): a consumer GPU with 6–8 GB VRAM (NVIDIA RTX 3060 or better) delivers fast generation. Without a GPU, it runs on CPU + RAM but 10–20x slower. For a 70B model at Q4 (~40 GB): you need either a high-end single GPU (NVIDIA A100 80GB), dual consumer GPUs (2× RTX 4090 = 48GB combined), or Apple Silicon with unified memory (M2 Ultra, M3 Max, or M4 Pro with 48GB+ RAM). Apple Silicon is uniquely suited for local LLMs because it uses unified memory — the GPU and CPU share the same memory pool, so a Mac Studio with 192GB RAM can theoretically run a 70B model with headroom. Ollama detects all of this automatically and splits layers across available hardware.

</details>

---

<br>

**Q5: How would you build a fully local RAG system using Ollama?**

<details>
<summary>💡 Show Answer</summary>

A local RAG system with Ollama requires three components: (1) **Embedding model** — pull `nomic-embed-text` or `mxbai-embed-large`, both are purpose-built embedding models available through Ollama that run entirely locally; (2) **Vector store** — use a local vector database (ChromaDB with `client = chromadb.Client()` creates an in-memory instance, or `PersistentClient` for disk) or simply numpy cosine similarity for small collections; (3) **Generation model** — any Ollama model (llama3.2, mistral, etc.) for the final generation step. The pipeline: embed all documents at ingest time, store vectors + text chunks, at query time embed the user question, find top-k similar chunks, inject them into the model's context, generate an answer. No data leaves your machine at any point — this is the fully privacy-preserving RAG architecture.

</details>

---

<br>

**Q6: When would you choose a local Ollama model over the OpenAI or Anthropic API?**

<details>
<summary>💡 Show Answer</summary>

Choose Ollama when: (1) **Data privacy is non-negotiable** — HIPAA, GDPR, financial compliance, or classified information; (2) **Offline operation is required** — air-gapped environments, factory floors, planes, ships; (3) **High-volume cost optimization** — at millions of API calls per month, amortized GPU hardware costs less than per-token pricing; (4) **Low latency on a LAN** — no network round-trip for locally embedded applications. Choose cloud APIs when: (1) **Maximum capability is needed** — no local model matches Claude Opus or GPT-4 on complex reasoning; (2) **Large context windows matter** — cloud models offer 200K tokens vs typical 8–32K for local models; (3) **Rapid prototyping** — no hardware to procure, works in minutes with an API key; (4) **Multimodal quality matters** — cloud vision models significantly outperform local vision models like Llava.

</details>

---

## Advanced

**Q7: What is GGUF format and how does K-quant work in practice?**

<details>
<summary>💡 Show Answer</summary>

GGUF (GPT-Generated Unified Format) is a binary file format that stores all model data — weights, tokenizer vocabulary, hyperparameters, and metadata — in a single file. It replaced the earlier GGML format. The "K" in Q4_K_M refers to k-means quantization: instead of uniformly quantizing all weights, it groups weights into blocks and computes a shared scale factor per block using k-means clustering. This reduces quantization error compared to naive uniform quantization. The "M" suffix means "medium" — a specific setting for block size and mixed precision. K-quant models also use higher precision (F16) for the most sensitive layers (attention key/query projections and layer norms), while quantizing the larger weight matrices more aggressively. The result: Q4_K_M models often score within 1% of F16 on benchmarks while using 4x less memory.

</details>

---

<br>

**Q8: How would you deploy Ollama in a production enterprise environment?**

<details>
<summary>💡 Show Answer</summary>

Enterprise deployment requires several steps beyond the single-workstation setup: (1) **Service management** — run Ollama as a systemd service on Linux (`systemctl enable ollama`) for automatic startup and process management; (2) **Network exposure** — by default Ollama binds to localhost. Set `OLLAMA_HOST=0.0.0.0:11434` to expose on the network, then add a reverse proxy (nginx/Caddy) for TLS termination and access control; (3) **Authentication** — Ollama has no built-in auth; use nginx `auth_basic` or an API gateway (Kong, Traefik) to enforce API keys; (4) **GPU allocation** — for multi-GPU servers, set `CUDA_VISIBLE_DEVICES` to assign specific GPUs to specific Ollama instances; (5) **Load balancing** — run multiple Ollama instances, each owning a GPU, behind a load balancer for horizontal scaling; (6) **Model management** — use Ollama's model library or build a custom Modelfile-based registry for organization-specific fine-tuned models; (7) **Monitoring** — scrape Ollama metrics (request rate, generation latency, queue depth) via its Prometheus-compatible endpoint.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Using LLM APIs](../09_Using_LLM_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Reasoning Models](../11_Reasoning_Models/Theory.md)
