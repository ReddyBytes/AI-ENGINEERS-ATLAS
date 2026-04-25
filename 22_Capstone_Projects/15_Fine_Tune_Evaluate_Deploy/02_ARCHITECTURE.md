# 02 Architecture — Fine-Tune, Evaluate, and Deploy

## Full MLOps Pipeline

```mermaid
flowchart TD
    DS[(Custom Dataset\n50+ examples\ninstruction/input/output)] --> PREP[Dataset Prep\nValidate + format\nTrain/val/test split]

    PREP --> BASE[Load Base Model\nmicrosoft/phi-2 or Mistral-7B\n4-bit BitsAndBytes]
    BASE --> LORA[Apply LoRA\nr=8, alpha=32\ntarget_modules q/v_proj]
    LORA --> TRAIN[SFTTrainer\n3 epochs\nGradient checkpointing]
    TRAIN --> ADAPTER[(LoRA Adapter\n~25MB saved\n./adapters/custom-v1)]

    ADAPTER --> EVAL[Evaluation\nBase vs Fine-tuned\non 10 test examples]
    BASE --> EVAL
    EVAL --> JUDGE[LLM-as-Judge\nClaude scores\nTask adherence 1-5]
    JUDGE --> REPORT[Eval Report\neval_results.json\nBefore/after comparison]

    ADAPTER --> SERVE[FastAPI Server\nuvicorn port 8000]
    BASE --> SERVE

    SERVE --> API1[POST /generate\nPrompt → response\n+ metadata]
    SERVE --> API2[GET /metrics\nAggregate stats]
    SERVE --> API3[GET /health\nServer status]

    API1 --> OBS[Observability Layer\nLatency tracking\nToken counting\nCost estimation]
    OBS --> LOGFILE[(request_log.jsonl\nAll request records)]

    style DS fill:#4A90D9,color:#fff
    style ADAPTER fill:#8E44AD,color:#fff
    style REPORT fill:#27AE60,color:#fff
    style SERVE fill:#16213e,color:#fff
    style LOGFILE fill:#E67E22,color:#fff
```

---

## Component Table

| Component | File | Input | Output | Key Config |
|---|---|---|---|---|
| Dataset Prep | `train.py` | `dataset.jsonl` | `DatasetDict` (train/val/test) | 70/15/15 split, 512 token max |
| Base Model Loader | `train.py` | Model name + BnB config | Quantized model + tokenizer | `load_in_4bit=True, nf4, bfloat16` |
| LoRA Application | `train.py` | Base model + LoRAConfig | PEFT-wrapped model | `r=8, alpha=32` |
| SFT Training | `train.py` | PEFT model + dataset | Updated weights in checkpoints | 3 epochs, lr=2e-4, batch=4 |
| Adapter Saver | `train.py` | Trained PEFT model | `./adapters/custom-v1/` directory | ~25MB adapter files |
| LLM Judge | `train.py` | Prompt + output + expected | Score dict (1-5) | Claude claude-sonnet-4-6 as evaluator |
| FastAPI App | `serve.py` | HTTP request | JSON response + metadata | Loads adapter at startup |
| Metrics Store | `serve.py` | Per-request records | Aggregate statistics | Thread-safe deque, max 10k records |
| Observability | `serve.py` | Response metadata | `request_log.jsonl` | Per-request JSONL logging |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `transformers` | Model loading, tokenization, generation |
| `peft` | LoRA adapter application and management |
| `trl` | SFTTrainer for supervised fine-tuning |
| `bitsandbytes` | 4-bit and 8-bit quantization |
| `datasets` | Dataset loading and processing |
| `fastapi` | REST API serving |
| `uvicorn` | ASGI server for FastAPI |
| `anthropic` | LLM-as-judge evaluation |
| `torch` | PyTorch (GPU) |

---

## LoRA Mechanics

```mermaid
flowchart LR
    IN[Input x] --> W[Frozen Weights W\n7B parameters\nnot updated]
    IN --> A[LoRA Matrix A\nr×d — random init]
    A --> B[LoRA Matrix B\nd×r — zero init]
    B --> DELTA["ΔW = B·A\n(low-rank update)"]
    W --> OUT
    DELTA -->|"scaled by α/r"| OUT[Output = Wx + ΔWx]
```

| Hyperparameter | Meaning | Typical Range | Effect |
|---|---|---|---|
| `r` (rank) | Dimension of adapter bottleneck | 4–64 | Higher r = more capacity, more VRAM/params |
| `lora_alpha` | Scaling factor; effective scale = α/r | 16–64 | Higher = stronger adaptation |
| `target_modules` | Which weight matrices to adapt | `q_proj, v_proj` minimum | More modules = more params but better adaptation |
| `lora_dropout` | Dropout on adapter outputs | 0.0–0.1 | Regularization; helps with small datasets |

---

## QLoRA Memory Stack

```mermaid
flowchart TB
    subgraph GPU Memory
        W4["Base Weights (4-bit NF4)\nMistral-7B: ~4GB\nPhi-2: ~1.4GB"]
        G16["Gradients (bfloat16)\nOnly for LoRA params\n~50MB"]
        A["LoRA Adapters (float32)\nA and B matrices\n~25MB"]
        KV["KV Cache\nBatch dependent\n~2GB at bs=4"]
    end
    W4 ~~~ G16
    G16 ~~~ A
    A ~~~ KV
```

| Model | Base (float16) | QLoRA 4-bit | Min VRAM (training) |
|---|---|---|---|
| Phi-2 (2.7B) | 5.4 GB | 1.6 GB | 8 GB |
| Mistral-7B | 14 GB | 4 GB | 14 GB |
| Llama-3-8B | 16 GB | 4.5 GB | 16 GB |

---

## Evaluation Framework

```mermaid
flowchart TD
    TEST[(Test Set\n10 examples)] --> BASE_GEN[Base Model\nGenerates outputs]
    TEST --> FT_GEN[Fine-tuned Model\nGenerates outputs]
    BASE_GEN --> JUDGE[LLM Judge\nClaude claude-sonnet-4-6]
    FT_GEN --> JUDGE
    TEST --> JUDGE
    JUDGE --> SCORES[Per-example scores\nTask Adherence 1-5\nCompleteness 1-5\nQuality 1-5]
    SCORES --> COMPARE[Comparison Report\nBase avg vs FT avg\nImprovement %]
```

---

## API Server Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI
    participant M as MetricsStore
    participant LM as Language Model

    C->>F: POST /generate {prompt, max_tokens}
    F->>F: Tokenize → input_tokens count
    F->>LM: model.generate(...)
    LM-->>F: token IDs
    F->>F: Decode → response text
    F->>F: Count output tokens
    F->>F: Estimate cost
    F->>M: record(latency, tokens, cost)
    M->>M: Append to deque + log file
    F-->>C: {response, latency_ms, tokens, cost_usd}

    C->>F: GET /metrics
    F->>M: get_summary()
    M-->>F: {avg_latency, p95, total_tokens, ...}
    F-->>C: Metrics JSON
```

---

## Observability Data Model

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO-8601 string | When the request was processed |
| `latency_ms` | float | End-to-end request latency |
| `input_tokens` | int | Tokens in the prompt |
| `output_tokens` | int | Tokens generated |
| `cost_usd` | float | Estimated compute cost |
| `success` | bool | Whether generation succeeded |
| `error` | str or None | Error message if failed |

Derived metrics: `p95_latency`, `tokens_per_second`, `cost_per_1k_tokens`

---

## File Structure

```
15_Fine_Tune_Evaluate_Deploy/
├── 01_MISSION.md
├── 02_ARCHITECTURE.md
├── 03_GUIDE.md
├── 04_RECAP.md
├── src/
│   └── starter.py          # train.py + serve.py combined entry point
├── dataset.jsonl           # Your 50+ training examples
├── eval_results.json       # Auto-generated evaluation report
├── request_log.jsonl       # Auto-generated per-request logs
├── checkpoints/            # Training checkpoints (auto-created)
└── adapters/
    └── custom-v1/          # Saved LoRA adapter
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| **02_ARCHITECTURE.md** | you are here |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
