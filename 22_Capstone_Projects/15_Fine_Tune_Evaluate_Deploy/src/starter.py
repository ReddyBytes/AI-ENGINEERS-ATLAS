"""
Fine-Tune, Evaluate, and Deploy — Starter Code
This file is the entry point. The full project uses two logical modules:

  train()  — QLoRA fine-tuning pipeline + LLM-as-judge evaluation
  serve()  — FastAPI server with observability (run separately)

Usage:
    python src/starter.py train     # run fine-tuning + evaluation
    python src/starter.py serve     # start the API server on port 8000

For the API server only (no training), run:
    uvicorn src.starter:app --reload
"""

import os
import json
import time
import sys
import threading
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import torch
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_NAME = "microsoft/phi-2"          # ← use for CPU/low-VRAM testing
# MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"  # ← for 16GB+ VRAM
ADAPTER_DIR = "./adapters/custom-v1"    # ← saved LoRA adapter location
DATASET_PATH = "./dataset.jsonl"        # ← your 50+ training examples


# ═══════════════════════════════════════════════════════════════════
# PART 1 — TRAINING PIPELINE (train.py)
# ═══════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

@dataclass
class LoRAConfig:
    r: int = 8                 # ← rank: higher = more capacity, more VRAM
    lora_alpha: int = 32       # ← scaling: effective scale = alpha/r = 4
    lora_dropout: float = 0.05
    target_modules: list = None
    bias: str = "none"

    def __post_init__(self):
        if self.target_modules is None:
            # Phi-2 attention + dense layers
            self.target_modules = ["q_proj", "v_proj", "k_proj", "dense"]
            # Mistral: ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


@dataclass
class TrainingConfig:
    output_dir: str = "./checkpoints"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4   # ← effective batch = 4 * 4 = 16
    warmup_steps: int = 50
    learning_rate: float = 2e-4
    max_seq_length: int = 512
    logging_steps: int = 10
    save_strategy: str = "epoch"
    evaluation_strategy: str = "epoch"


# ─────────────────────────────────────────────
# Dataset Utilities
# ─────────────────────────────────────────────

def load_and_validate_dataset(path: str):
    """
    Load dataset from JSONL and validate format.

    TODO: Implement full validation.
    Steps:
      1. Load from JSONL file (one JSON object per line)
      2. Verify each example has keys: "instruction", "input", "output"
      3. Print statistics: count, avg token lengths, max token length
      4. Warn if any example exceeds max_seq_length (512)
      5. Create 70/15/15 train/validation/test splits
      6. Return DatasetDict
    """
    from datasets import Dataset, DatasetDict

    # Placeholder: tiny synthetic dataset for testing without real data
    # Replace this by loading from DATASET_PATH
    synthetic_examples = [
        {
            "instruction": "Summarize this text in one sentence.",
            "input": "Large language models are trained on vast amounts of text data and can perform a wide variety of natural language tasks.",
            "output": "LLMs are trained on large text corpora and are capable of diverse NLP tasks.",
        },
        {
            "instruction": "Convert this informal message to professional email tone.",
            "input": "hey can u send me the report asap its super urgent",
            "output": "Could you please send me the report at your earliest convenience? It is quite urgent.",
        },
        # TODO: Add at least 48 more examples of your specific task
        # Options:
        #   A) Generate with Claude (document clearly in comments)
        #   B) Curate from HuggingFace Hub public datasets
        #   C) Collect from real task examples you have
    ]

    ds = Dataset.from_list(synthetic_examples)
    splits = ds.train_test_split(test_size=0.3, seed=42)
    val_test = splits["test"].train_test_split(test_size=0.5, seed=42)

    dataset = DatasetDict({
        "train": splits["train"],
        "validation": val_test["train"],
        "test": val_test["test"],
    })
    print(f"[Dataset] Train: {len(dataset['train'])}, "
          f"Val: {len(dataset['validation'])}, Test: {len(dataset['test'])}")
    return dataset


def format_example(example: dict, template: str = "alpaca") -> str:
    """
    Format a single example using the model's chat template.

    SFTTrainer trains on the full sequence (prompt + response).
    The model learns to generate the response given the prompt.

    TODO: Add Mistral template as an elif branch:
        <s>[INST] {instruction}\n{input} [/INST] {output}</s>
    """
    if template == "alpaca":
        if example.get("input"):
            return (
                f"### Instruction:\n{example['instruction']}\n\n"
                f"### Input:\n{example['input']}\n\n"
                f"### Response:\n{example['output']}"
            )
        else:
            return (
                f"### Instruction:\n{example['instruction']}\n\n"
                f"### Response:\n{example['output']}"
            )
    else:
        raise ValueError(f"Unknown template: {template}")


# ─────────────────────────────────────────────
# Model Loading
# ─────────────────────────────────────────────

def load_base_model_4bit(model_name: str):
    """
    Load model with 4-bit quantization for training (QLoRA).

    GPU path: BitsAndBytesConfig with nf4 quantization + bfloat16 compute.
    CPU path: standard load without quantization (for testing only, slow).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[Model] Loading {model_name}...")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token   # ← required for batch training

    if not torch.cuda.is_available():
        print("[Model] No GPU detected — loading in CPU mode (slow, for testing only)")
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        return model, tokenizer

    # 4-bit quantized load for GPU (QLoRA)
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,    # ← double quantization saves ~0.4 bits/param
        bnb_4bit_quant_type="nf4",         # ← NormalFloat4 — best for normally distributed weights
        bnb_4bit_compute_dtype=torch.bfloat16,  # ← compute in bfloat16, store in 4-bit
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",                 # ← automatically distribute across GPUs
        trust_remote_code=True,
    )
    print(f"[Model] Loaded. Memory: {model.get_memory_footprint() / 1e9:.2f} GB")
    return model, tokenizer


# ─────────────────────────────────────────────
# LoRA Application
# ─────────────────────────────────────────────

def apply_lora(model, config: LoRAConfig):
    """
    Apply LoRA adapters to the model.

    prepare_model_for_kbit_training: enables gradient checkpointing,
    handles the 4-bit <-> float32 conversion for gradient computation.
    """
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if torch.cuda.is_available():
        model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=config.r,
        lora_alpha=config.lora_alpha,
        target_modules=config.target_modules,
        lora_dropout=config.lora_dropout,
        bias=config.bias,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()   # ← should be ~0.1-0.5% of total params
    return model


# ─────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────

def run_training(model, tokenizer, dataset, config: TrainingConfig) -> None:
    """
    Run SFT training with TRL's SFTTrainer.

    TODO: The core setup is implemented. Review and run it.
    The main thing to verify: the "formatted_text" column contains
    the full prompt+response string (format_example output).
    SFTTrainer trains on this full sequence — not just the response.
    """
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print("\n[Training] Preparing dataset...")
    train_ds = dataset["train"].map(
        lambda ex: {"formatted_text": format_example(ex)},
        remove_columns=dataset["train"].column_names,
    )
    val_ds = dataset["validation"].map(
        lambda ex: {"formatted_text": format_example(ex)},
        remove_columns=dataset["validation"].column_names,
    )

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        warmup_steps=config.warmup_steps,
        learning_rate=config.learning_rate,
        fp16=torch.cuda.is_available(),   # ← mixed precision only on GPU
        logging_steps=config.logging_steps,
        evaluation_strategy=config.evaluation_strategy,
        save_strategy=config.save_strategy,
        load_best_model_at_end=True,
        report_to="none",   # ← disable wandb/mlflow unless you want it
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        dataset_text_field="formatted_text",
        max_seq_length=config.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("\n[Training] Starting training...")
    trainer.train()

    print(f"\n[Training] Saving adapter to {ADAPTER_DIR}")
    trainer.model.save_pretrained(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print("[Training] Done.")


# ─────────────────────────────────────────────
# Inference Utilities
# ─────────────────────────────────────────────

def generate_response(model, tokenizer, prompt: str, max_new_tokens: int = 150) -> tuple[str, float]:
    """Generate a response and return (text, latency_ms)."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    start = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    latency_ms = (time.perf_counter() - start) * 1000

    # Decode only the new tokens (not the input prompt)
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return response.strip(), latency_ms


# ─────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────

def llm_judge_score(prompt: str, model_output: str, expected: str, task_description: str) -> dict:
    """
    Use Claude as judge to score a model output.

    TODO: Implement LLM judge scoring.
    Steps:
      1. Build a judge prompt with:
           - Task description
           - The original prompt
           - Expected/reference output
           - Model's actual output
      2. Score on 3 criteria: TASK_ADHERENCE, COMPLETENESS, QUALITY (each 1-5)
      3. Return JSON scores + rationale + average

    Use max_tokens=150 — scores are concise.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # TODO: Replace placeholder with actual judge call
    return {
        "task_adherence": 3,
        "completeness": 3,
        "quality": 3,
        "rationale": "[Not implemented — complete the llm_judge_score TODO]",
        "average": 3.0,
    }


def run_evaluation(base_model, ft_model, tokenizer, dataset, task_description: str) -> dict:
    """Compare base vs. fine-tuned model on the test set."""
    test_examples = list(dataset["test"])
    print(f"\n[Eval] Evaluating {len(test_examples)} test examples...")

    base_scores = []
    ft_scores = []
    comparisons = []

    for i, example in enumerate(test_examples):
        # Build prompt without the expected response
        prompt = format_example({**example, "output": ""}).split("### Response:")[0] + "### Response:"

        base_output, base_latency = generate_response(base_model, tokenizer, prompt)
        ft_output, ft_latency = generate_response(ft_model, tokenizer, prompt)

        base_score = llm_judge_score(prompt, base_output, example["output"], task_description)
        ft_score = llm_judge_score(prompt, ft_output, example["output"], task_description)

        base_scores.append(base_score["average"])
        ft_scores.append(ft_score["average"])

        comparisons.append({
            "example_id": i,
            "prompt": example["instruction"][:100],
            "base_output": base_output[:200],
            "ft_output": ft_output[:200],
            "base_score": base_score,
            "ft_score": ft_score,
        })
        print(f"  [{i+1}/{len(test_examples)}] Base: {base_score['average']:.1f}, "
              f"FT: {ft_score['average']:.1f}")

    avg_base = sum(base_scores) / len(base_scores)
    avg_ft = sum(ft_scores) / len(ft_scores)
    improvement = avg_ft - avg_base

    print(f"\n[Eval] Base model average:    {avg_base:.2f}/5")
    print(f"[Eval] Fine-tuned average:    {avg_ft:.2f}/5")
    print(f"[Eval] Improvement:           {improvement:+.2f} points ({improvement/avg_base*100:+.1f}%)")

    results = {
        "timestamp": datetime.now().isoformat(),
        "model_name": MODEL_NAME,
        "adapter_dir": ADAPTER_DIR,
        "base_avg_score": avg_base,
        "ft_avg_score": avg_ft,
        "improvement": improvement,
        "comparisons": comparisons,
    }
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[Eval] Results saved to eval_results.json")
    return results


def train_main():
    """Run the full training + evaluation pipeline."""
    print("=== Phase 1: Dataset ===")
    dataset = load_and_validate_dataset(DATASET_PATH)

    print("\n=== Phase 2: Training ===")
    lora_cfg = LoRAConfig()
    train_cfg = TrainingConfig()

    base_model, tokenizer = load_base_model_4bit(MODEL_NAME)
    peft_model = apply_lora(base_model, lora_cfg)
    run_training(peft_model, tokenizer, dataset, train_cfg)

    print("\n=== Phase 3: Evaluation ===")
    base_for_eval, _ = load_base_model_4bit(MODEL_NAME)
    from peft import PeftModel
    ft_for_eval = PeftModel.from_pretrained(base_for_eval, ADAPTER_DIR)
    ft_for_eval.eval()

    # TODO: Replace with your actual task description
    task_description = (
        "The model should [DESCRIBE YOUR TASK HERE]. "
        "Good outputs should [DESCRIBE QUALITY CRITERIA]."
    )

    results = run_evaluation(base_for_eval, ft_for_eval, tokenizer, dataset, task_description)
    print(f"\nFine-tuning improved average score by {results['improvement']:+.2f} points.")


# ═══════════════════════════════════════════════════════════════════
# PART 2 — API SERVER (serve.py)
# ═══════════════════════════════════════════════════════════════════

LOG_FILE = "request_log.jsonl"
GPU_COST_PER_HOUR_USD = 2.0   # ← A100 ~$2/hr
TOKENS_PER_SECOND = 50.0      # ← approximate throughput
USE_ADAPTER = os.path.exists(ADAPTER_DIR)


# ─────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────

try:
    from pydantic import BaseModel as PydanticBase

    class GenerateRequest(PydanticBase):
        prompt: str
        max_new_tokens: int = 150
        temperature: float = 0.1
        stream: bool = False

    class GenerateResponse(PydanticBase):
        response: str
        input_tokens: int
        output_tokens: int
        latency_ms: float
        cost_usd: float
        model_version: str
        timestamp: str

except ImportError:
    GenerateRequest = None
    GenerateResponse = None


# ─────────────────────────────────────────────
# Observability Store
# ─────────────────────────────────────────────

@dataclass
class RequestRecord:
    timestamp: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool
    error: Optional[str] = None


class MetricsStore:
    """Thread-safe in-memory metrics store with JSONL persistence."""

    def __init__(self):
        self._lock = threading.Lock()
        self._records: deque = deque(maxlen=10000)   # ← keep last 10k requests

    def record(self, rec: RequestRecord) -> None:
        with self._lock:
            self._records.append(rec)
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(asdict(rec)) + "\n")

    def get_summary(self) -> dict:
        """
        TODO: Implement full metrics aggregation.
        Return:
          {
            "total_requests": N,
            "success_rate": 0.xx,
            "avg_latency_ms": N,
            "p50_latency_ms": N,
            "p95_latency_ms": N,
            "total_input_tokens": N,
            "total_output_tokens": N,
            "total_cost_usd": N,
          }

        For percentiles: sort latencies, index at 50th/95th percentile positions.
        """
        with self._lock:
            records = list(self._records)

        if not records:
            return {"total_requests": 0}

        total = len(records)
        successful = [r for r in records if r.success]
        latencies = sorted(r.latency_ms for r in successful) if successful else [0]

        return {
            "total_requests": total,
            "success_rate": len(successful) / total if total > 0 else 0,
            "avg_latency_ms": sum(latencies) / len(latencies),
            "p50_latency_ms": latencies[int(len(latencies) * 0.50)],
            "p95_latency_ms": latencies[int(len(latencies) * 0.95)],
            "total_input_tokens": sum(r.input_tokens for r in records),
            "total_output_tokens": sum(r.output_tokens for r in records),
            "total_cost_usd": round(sum(r.cost_usd for r in records), 6),
        }


metrics_store = MetricsStore()


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate compute cost in USD for self-hosted inference."""
    total_tokens = input_tokens + output_tokens
    time_seconds = total_tokens / TOKENS_PER_SECOND
    return (time_seconds / 3600) * GPU_COST_PER_HOUR_USD


def load_model_for_serving():
    """Load model at server startup."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[Server] Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, quantization_config=bnb_config,
            device_map="auto", trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True)

    if USE_ADAPTER:
        from peft import PeftModel
        print(f"[Server] Loading adapter from {ADAPTER_DIR}")
        model = PeftModel.from_pretrained(model, ADAPTER_DIR)

    model.eval()
    version = f"{MODEL_NAME}{'_ft' if USE_ADAPTER else '_base'}"
    print(f"[Server] Model ready: {version}")
    return model, tokenizer, version


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse

    app = FastAPI(
        title="Fine-Tuned Model API",
        description="Serving fine-tuned model with observability",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    # Global model state (loaded at startup)
    _model = None
    _tokenizer = None
    _model_version = "not_loaded"

    @app.on_event("startup")
    async def startup_event():
        global _model, _tokenizer, _model_version
        _model, _tokenizer, _model_version = load_model_for_serving()

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "model": _model_version,
            "gpu_available": torch.cuda.is_available(),
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/metrics")
    async def get_metrics():
        return metrics_store.get_summary()

    @app.post("/generate")
    async def generate(request: GenerateRequest):
        """
        TODO: The core implementation is below — review and complete it.
        Ensure the metrics_store.record() call happens in BOTH
        the success path and the except block.
        """
        if _model is None:
            raise HTTPException(status_code=503, detail="Model not ready")

        start = time.perf_counter()
        try:
            inputs = _tokenizer(request.prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            input_tokens = inputs["input_ids"].shape[1]

            with torch.no_grad():
                outputs = _model.generate(
                    **inputs,
                    max_new_tokens=request.max_new_tokens,
                    temperature=request.temperature,
                    do_sample=request.temperature > 0,
                    pad_token_id=_tokenizer.eos_token_id,
                )

            latency_ms = (time.perf_counter() - start) * 1000
            new_tokens = outputs[0][input_tokens:]   # ← only new tokens
            response_text = _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            output_tokens = len(new_tokens)
            cost = estimate_cost(input_tokens, output_tokens)

            metrics_store.record(RequestRecord(
                timestamp=datetime.now().isoformat(),
                latency_ms=round(latency_ms, 2),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                success=True,
            ))

            return {
                "response": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(cost, 8),
                "model_version": _model_version,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            metrics_store.record(RequestRecord(
                timestamp=datetime.now().isoformat(),
                latency_ms=round(latency_ms, 2),
                input_tokens=0, output_tokens=0, cost_usd=0,
                success=False, error=str(e),
            ))
            raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    @app.post("/generate/stream")
    async def generate_stream(request: GenerateRequest):
        """
        TODO: Implement streaming generation.
        Steps:
          1. Use TextIteratorStreamer with a background Thread
          2. Start model.generate() in the thread with streamer=streamer
          3. Yield tokens via StreamingResponse as SSE: "data: {token}\n\n"

        Hint:
            from transformers import TextIteratorStreamer
            from threading import Thread
            streamer = TextIteratorStreamer(_tokenizer, skip_prompt=True)
            thread = Thread(target=_model.generate, kwargs={..., "streamer": streamer})
            thread.start()
            for token in streamer:
                yield f"data: {token}\n\n"
        """
        raise HTTPException(status_code=501, detail="Streaming not yet implemented")

except ImportError:
    app = None
    print("[Server] FastAPI not installed. Run: pip install fastapi uvicorn")


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "train"

    if mode == "train":
        train_main()
    elif mode == "serve":
        try:
            import uvicorn
            uvicorn.run("src.starter:app", host="0.0.0.0", port=8000, reload=False)
        except ImportError:
            print("Install uvicorn: pip install uvicorn")
    else:
        print(f"Unknown mode: {mode}. Use 'train' or 'serve'.")
        sys.exit(1)
