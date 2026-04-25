"""
Fine-Tune, Evaluate, and Deploy — Project 15 SOLUTION
======================================================
Complete MLOps pipeline:
  train()  — QLoRA fine-tuning + LLM-as-judge before/after evaluation
  serve()  — FastAPI server with streaming, metrics, and observability

Usage:
    python solution.py train     # run fine-tuning + evaluation
    python solution.py serve     # start the API server on port 8000

For the API server only (no training):
    uvicorn solution:app --reload

Setup:
    pip install transformers peft trl bitsandbytes datasets fastapi uvicorn anthropic torch accelerate
"""

import os
import json
import time
import sys
import re
import threading
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import torch
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_NAME = "microsoft/phi-2"          # ← use for CPU/low-VRAM testing (2.7B params)
# MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"  # ← for 16GB+ VRAM
ADAPTER_DIR = "./adapters/custom-v1"    # ← saved LoRA adapter location
DATASET_PATH = "./dataset.jsonl"        # ← your 50+ training examples in Alpaca format


# ═══════════════════════════════════════════════════════════════════
# PART 1 — TRAINING PIPELINE
# ═══════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

@dataclass
class LoRAConfig:
    r: int = 8                 # ← rank: higher = more adapter capacity, more VRAM
    lora_alpha: int = 32       # ← scaling factor: effective scale = alpha/r = 4
    lora_dropout: float = 0.05
    target_modules: list = None
    bias: str = "none"

    def __post_init__(self):
        if self.target_modules is None:
            # Phi-2 attention + projection layers
            self.target_modules = ["q_proj", "v_proj", "k_proj", "dense"]
            # For Mistral use: ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


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
    Validates keys, computes statistics, warns on long examples.
    Creates 70/15/15 train/validation/test splits.
    Falls back to synthetic data if file not found (for testing).
    """
    from datasets import Dataset, DatasetDict

    if os.path.exists(path):
        # Load from JSONL — one JSON object per line
        examples = []
        with open(path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ex = json.loads(line)
                    examples.append(ex)
                except json.JSONDecodeError as e:
                    print(f"[Dataset] Warning: line {lineno} is invalid JSON: {e}")

        print(f"[Dataset] Loaded {len(examples)} examples from {path}")

        # Validate required keys
        required_keys = {"instruction", "input", "output"}
        for i, ex in enumerate(examples):
            missing = required_keys - set(ex.keys())
            if missing:
                raise ValueError(f"Example {i} missing required keys: {missing}")

        # Compute statistics
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
            lengths = [len(tokenizer.encode(format_example(ex))) for ex in examples]
            print(f"[Dataset] Token stats: avg={sum(lengths)/len(lengths):.0f}, "
                  f"max={max(lengths)}, min={min(lengths)}")
            overlong = sum(1 for l in lengths if l > TrainingConfig().max_seq_length)
            if overlong:
                print(f"[Dataset] Warning: {overlong} examples exceed max_seq_length "
                      f"({TrainingConfig().max_seq_length} tokens) — will be truncated")
        except Exception:
            pass  # ← statistics are optional; don't fail training if tokenizer unavailable

    else:
        print(f"[Dataset] {path} not found — using synthetic data for testing")
        print("[Dataset] To train on real data, create dataset.jsonl with 50+ examples")

        # 50 synthetic examples for email tone conversion task
        examples = _generate_synthetic_dataset()

    ds = Dataset.from_list(examples)
    splits = ds.train_test_split(test_size=0.3, seed=42)
    val_test = splits["test"].train_test_split(test_size=0.5, seed=42)   # ← split test into val + test

    dataset = DatasetDict({
        "train": splits["train"],
        "validation": val_test["train"],
        "test": val_test["test"],
    })
    print(f"[Dataset] Train: {len(dataset['train'])}, "
          f"Val: {len(dataset['validation'])}, Test: {len(dataset['test'])}")
    return dataset


def _generate_synthetic_dataset() -> list[dict]:
    """
    50 synthetic email tone conversion examples.
    In production: generate with Claude or use a real dataset.
    """
    informal_phrases = [
        ("hey can u send me the report asap its super urgent",
         "Could you please send me the report at your earliest convenience? The matter is quite urgent."),
        ("hi i need this done by eod today no exceptions",
         "I would appreciate it if this could be completed by end of day today. This is a firm deadline."),
        ("yo the meeting got moved can u make it tmrw at 2",
         "I wanted to let you know that the meeting has been rescheduled. Are you available tomorrow at 2:00 PM?"),
        ("thx so much for helping out really appreciate it",
         "Thank you very much for your assistance. I truly appreciate your support."),
        ("sorry 4 the late reply been super busy lately",
         "I apologize for the delayed response. I have been occupied with several commitments recently."),
        ("can we jump on a call to chat about the project",
         "Would you be available for a brief call to discuss the project details?"),
        ("heads up there's an issue with the server again",
         "I wanted to bring to your attention that we are experiencing another server issue."),
        ("fyi the client is not happy with the current version",
         "For your information, the client has expressed dissatisfaction with the current version."),
        ("dont forget the deadline is friday!!",
         "Please remember that the deadline is this Friday. Timely submission is important."),
        ("lmk if u need anything else",
         "Please do not hesitate to let me know if there is anything else I can assist you with."),
    ]

    examples = []
    for i in range(50):
        informal, formal = informal_phrases[i % len(informal_phrases)]
        # Add slight variation to avoid exact duplicates
        variation = f" (example {i+1})" if i >= len(informal_phrases) else ""
        examples.append({
            "instruction": "Convert this informal message to professional email tone.",
            "input": informal + variation,
            "output": formal,
        })

    return examples


def format_example(example: dict, template: str = "alpaca") -> str:
    """
    Format a single example using the Alpaca instruction template.
    SFTTrainer trains on the full sequence (prompt + response).
    The model learns: given this prompt, produce this response.
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
    elif template == "mistral":
        # Mistral chat template format: [INST] instruction\ninput [/INST] output </s>
        content = example["instruction"]
        if example.get("input"):
            content += f"\n{example['input']}"
        return f"<s>[INST] {content} [/INST] {example['output']}</s>"
    else:
        raise ValueError(f"Unknown template: {template}")


# ─────────────────────────────────────────────
# Model Loading
# ─────────────────────────────────────────────

def load_base_model_4bit(model_name: str):
    """
    Load model with 4-bit quantization for QLoRA training.
    GPU path: BitsAndBytesConfig with nf4 quantization + bfloat16 compute dtype.
    CPU path: standard load without quantization (slow, for testing/development only).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[Model] Loading {model_name}...")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token   # ← required for batched training

    if not torch.cuda.is_available():
        print("[Model] No GPU detected — loading in CPU mode (slow, for testing only)")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float32,
        )
        return model, tokenizer

    # 4-bit quantized load (QLoRA): loads weights in nf4, computes in bfloat16
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,         # ← second quantization saves ~0.4 bits/param
        bnb_4bit_quant_type="nf4",              # ← NormalFloat4 — best for normally distributed weights
        bnb_4bit_compute_dtype=torch.bfloat16,  # ← compute in bfloat16, store in 4-bit
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",                      # ← auto-distribute across GPUs
        trust_remote_code=True,
    )
    footprint_gb = model.get_memory_footprint() / 1e9
    print(f"[Model] Loaded. Memory footprint: {footprint_gb:.2f} GB")
    return model, tokenizer


# ─────────────────────────────────────────────
# LoRA Application
# ─────────────────────────────────────────────

def apply_lora(model, config: LoRAConfig):
    """
    Apply LoRA adapters to the loaded model.
    prepare_model_for_kbit_training enables gradient checkpointing and handles
    the 4-bit <-> float32 conversion boundary during backprop.
    """
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    if torch.cuda.is_available():
        # Required for QLoRA: enables gradient checkpointing on quantized model
        model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=config.r,
        lora_alpha=config.lora_alpha,
        target_modules=config.target_modules,
        lora_dropout=config.lora_dropout,
        bias=config.bias,
        task_type="CAUSAL_LM",               # ← specifies this is for autoregressive LM
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()       # ← should print ~0.1-0.5% trainable params
    return model


# ─────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────

def run_training(model, tokenizer, dataset, config: TrainingConfig) -> None:
    """
    Run SFT (Supervised Fine-Tuning) with TRL's SFTTrainer.
    SFTTrainer trains on the full formatted_text string (prompt + response).
    The adapter weights are saved to ADAPTER_DIR after training.
    """
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print("\n[Training] Preparing dataset with Alpaca formatting...")
    train_ds = dataset["train"].map(
        lambda ex: {"formatted_text": format_example(ex)},
        remove_columns=dataset["train"].column_names,   # ← drop raw columns, keep only formatted
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
        fp16=torch.cuda.is_available(),     # ← mixed precision only on GPU
        logging_steps=config.logging_steps,
        evaluation_strategy=config.evaluation_strategy,
        save_strategy=config.save_strategy,
        load_best_model_at_end=True,        # ← keep the checkpoint with best eval loss
        report_to="none",                   # ← disable wandb/mlflow; use "wandb" to enable
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        dataset_text_field="formatted_text",   # ← column containing the full formatted string
        max_seq_length=config.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("\n[Training] Starting training...")
    trainer.train()

    print(f"\n[Training] Saving LoRA adapter to {ADAPTER_DIR}")
    os.makedirs(ADAPTER_DIR, exist_ok=True)
    trainer.model.save_pretrained(ADAPTER_DIR)   # ← saves only adapter weights (~20-40MB)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print("[Training] Done.")


# ─────────────────────────────────────────────
# Inference Utilities
# ─────────────────────────────────────────────

def generate_response(model, tokenizer, prompt: str, max_new_tokens: int = 150) -> tuple[str, float]:
    """
    Generate a response and return (text, latency_ms).
    Decodes only the new tokens (not the input prompt) by slicing outputs.
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    input_len = inputs["input_ids"].shape[1]   # ← needed to slice off the prompt later

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

    new_tokens = outputs[0][input_len:]   # ← slice to exclude input tokens from decode
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return response.strip(), latency_ms


# ─────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────

def llm_judge_score(prompt: str, model_output: str, expected: str, task_description: str) -> dict:
    """
    Use Claude as an independent judge to score a model output.
    Scores TASK_ADHERENCE, COMPLETENESS, QUALITY each 1-5 with rationale.
    Returns dict with individual scores, rationale, and average.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    judge_prompt = (
        f"You are evaluating a model's performance on this task:\n{task_description}\n\n"
        f"Score the model's response on 3 criteria (1–5 each):\n"
        f"- TASK_ADHERENCE: Does it follow the required format/style?\n"
        f"  1=completely wrong format  3=partial  5=perfect format\n"
        f"- COMPLETENESS: Does it address all required elements?\n"
        f"  1=missing most elements  3=partial  5=all elements present\n"
        f"- QUALITY: Is it well-written and natural for its purpose?\n"
        f"  1=poorly written  3=acceptable  5=excellent\n\n"
        f"Original prompt: {prompt[:300]}\n"
        f"Reference output: {expected[:300]}\n"
        f"Model response: {model_output[:300]}\n\n"
        f"Return ONLY valid JSON:\n"
        f'{{"task_adherence": N, "completeness": N, "quality": N, "rationale": "one sentence"}}'
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,    # ← concise JSON response
        messages=[{"role": "user", "content": judge_prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"```[a-z]*\n?", "", raw).strip()

    try:
        scores = json.loads(raw)
    except json.JSONDecodeError:
        scores = {"task_adherence": 3, "completeness": 3, "quality": 3,
                  "rationale": "JSON parse error — defaulted to mid-range"}

    # Compute average across the three criteria
    ta = int(scores.get("task_adherence", 3))
    comp = int(scores.get("completeness", 3))
    qual = int(scores.get("quality", 3))
    scores["task_adherence"] = ta
    scores["completeness"] = comp
    scores["quality"] = qual
    scores["average"] = round((ta + comp + qual) / 3, 2)

    return scores


def run_evaluation(base_model, ft_model, tokenizer, dataset, task_description: str) -> dict:
    """
    Compare base vs. fine-tuned model on the test set using LLM-as-judge.
    Generates outputs from both models, scores them independently, and
    reports the improvement from fine-tuning.
    """
    test_examples = list(dataset["test"])
    print(f"\n[Eval] Evaluating {len(test_examples)} test examples...")
    print(f"[Eval] Task: {task_description[:100]}...")

    base_scores = []
    ft_scores = []
    comparisons = []

    for i, example in enumerate(test_examples):
        # Build prompt WITHOUT the expected response (test the model's generation)
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
            "base_latency_ms": round(base_latency, 1),
            "ft_latency_ms": round(ft_latency, 1),
        })
        print(f"  [{i+1}/{len(test_examples)}] Base: {base_score['average']:.1f}, "
              f"FT: {ft_score['average']:.1f}  "
              f"({base_latency:.0f}ms vs {ft_latency:.0f}ms)")

    avg_base = sum(base_scores) / len(base_scores) if base_scores else 0
    avg_ft = sum(ft_scores) / len(ft_scores) if ft_scores else 0
    improvement = avg_ft - avg_base
    pct_improvement = (improvement / avg_base * 100) if avg_base > 0 else 0

    print(f"\n[Eval] Base model average:    {avg_base:.2f}/5")
    print(f"[Eval] Fine-tuned average:    {avg_ft:.2f}/5")
    print(f"[Eval] Improvement:           {improvement:+.2f} points ({pct_improvement:+.1f}%)")

    results = {
        "timestamp": datetime.now().isoformat(),
        "model_name": MODEL_NAME,
        "adapter_dir": ADAPTER_DIR,
        "base_avg_score": avg_base,
        "ft_avg_score": avg_ft,
        "improvement": improvement,
        "pct_improvement": pct_improvement,
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

    print("\n=== Phase 3: Before/After Evaluation ===")
    # Load fresh base model for fair comparison (before fine-tuning)
    base_for_eval, _ = load_base_model_4bit(MODEL_NAME)

    # Load fine-tuned model: base + adapter
    from peft import PeftModel
    ft_for_eval = PeftModel.from_pretrained(base_for_eval, ADAPTER_DIR)
    ft_for_eval.eval()

    task_description = (
        "The model converts informal, casual customer messages to professional email tone. "
        "Good outputs preserve all information from the original message while using "
        "formal grammar, complete sentences, and professional vocabulary."
    )

    results = run_evaluation(base_for_eval, ft_for_eval, tokenizer, dataset, task_description)
    print(f"\nFine-tuning improved average score by {results['improvement']:+.2f} points "
          f"({results['pct_improvement']:+.1f}%).")


# ═══════════════════════════════════════════════════════════════════
# PART 2 — API SERVER
# ═══════════════════════════════════════════════════════════════════

LOG_FILE = "request_log.jsonl"
GPU_COST_PER_HOUR_USD = 2.0   # ← A100 ~$2/hr on Lambda Labs / RunPod
TOKENS_PER_SECOND = 50.0      # ← approximate throughput for Phi-2
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
        self._records: deque = deque(maxlen=10000)   # ← keep last 10k requests in memory

    def record(self, rec: RequestRecord) -> None:
        """Record a request — thread-safe append to memory + file."""
        with self._lock:
            self._records.append(rec)
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(asdict(rec)) + "\n")  # ← one record per line for easy tailing

    def get_summary(self) -> dict:
        """
        Aggregate all recorded requests into summary statistics.
        Percentiles are computed from sorted latency list.
        Returns empty summary if no requests recorded yet.
        """
        with self._lock:
            records = list(self._records)

        if not records:
            return {"total_requests": 0}

        total = len(records)
        successful = [r for r in records if r.success]
        # Sort latencies ascending for percentile indexing
        latencies = sorted(r.latency_ms for r in successful) if successful else [0]
        n = len(latencies)

        return {
            "total_requests": total,
            "success_rate": round(len(successful) / total, 4) if total > 0 else 0,
            "avg_latency_ms": round(sum(latencies) / n, 1),
            "p50_latency_ms": latencies[int(n * 0.50)],          # ← 50th percentile
            "p95_latency_ms": latencies[min(int(n * 0.95), n-1)],  # ← 95th percentile (cap at max index)
            "total_input_tokens": sum(r.input_tokens for r in records),
            "total_output_tokens": sum(r.output_tokens for r in records),
            "total_cost_usd": round(sum(r.cost_usd for r in records), 6),
            "requests_last_hour": sum(
                1 for r in records
                if (datetime.now() - datetime.fromisoformat(r.timestamp)).seconds < 3600  # ← last 60 min
            ),
        }


metrics_store = MetricsStore()


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate compute cost in USD for self-hosted GPU inference."""
    total_tokens = input_tokens + output_tokens
    time_seconds = total_tokens / TOKENS_PER_SECOND       # ← time to generate all tokens
    return (time_seconds / 3600) * GPU_COST_PER_HOUR_USD  # ← prorated hourly GPU cost


def load_model_for_serving():
    """Load model (with optional LoRA adapter) at server startup."""
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
        print(f"[Server] Loading LoRA adapter from {ADAPTER_DIR}")
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
        description="Serving fine-tuned Phi-2 / Mistral with observability",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    # Global model state — loaded once at startup to avoid per-request loading overhead
    _model = None
    _tokenizer = None
    _model_version = "not_loaded"

    @app.on_event("startup")
    async def startup_event():
        global _model, _tokenizer, _model_version
        _model, _tokenizer, _model_version = load_model_for_serving()

    @app.get("/health")
    async def health():
        """Health check endpoint — returns model version and GPU status."""
        return {
            "status": "healthy",
            "model": _model_version,
            "gpu_available": torch.cuda.is_available(),
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/metrics")
    async def get_metrics():
        """Return aggregated request metrics."""
        return metrics_store.get_summary()

    @app.post("/generate")
    async def generate(request: GenerateRequest):
        """
        Generate text from the fine-tuned model.
        Tracks latency, token counts, and estimated cost.
        Records metrics in BOTH the success and error paths.
        """
        if _model is None:
            raise HTTPException(status_code=503, detail="Model not ready — server is still loading")

        start = time.perf_counter()
        try:
            inputs = _tokenizer(request.prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            input_tokens = inputs["input_ids"].shape[1]   # ← count input tokens before generation

            with torch.no_grad():
                outputs = _model.generate(
                    **inputs,
                    max_new_tokens=request.max_new_tokens,
                    temperature=request.temperature,
                    do_sample=request.temperature > 0,    # ← greedy decoding if temperature=0
                    pad_token_id=_tokenizer.eos_token_id,
                )

            latency_ms = (time.perf_counter() - start) * 1000
            new_tokens = outputs[0][input_tokens:]         # ← slice to get only generated tokens
            response_text = _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            output_tokens = len(new_tokens)
            cost = estimate_cost(input_tokens, output_tokens)

            # Record success
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
            # Record failure — always record so error rate is visible in metrics
            metrics_store.record(RequestRecord(
                timestamp=datetime.now().isoformat(),
                latency_ms=round(latency_ms, 2),
                input_tokens=0, output_tokens=0, cost_usd=0.0,
                success=False, error=str(e),
            ))
            raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    @app.post("/generate/stream")
    async def generate_stream(request: GenerateRequest):
        """
        Streaming generation via Server-Sent Events (SSE).
        Uses TextIteratorStreamer with a background thread so the model.generate()
        call doesn't block the async event loop.
        Each token is yielded as "data: {token}\\n\\n" following the SSE spec.
        """
        if _model is None:
            raise HTTPException(status_code=503, detail="Model not ready")

        from transformers import TextIteratorStreamer
        from threading import Thread

        inputs = _tokenizer(request.prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # skip_prompt=True means the streamer yields only new tokens, not the input
        streamer = TextIteratorStreamer(_tokenizer, skip_prompt=True, skip_special_tokens=True)

        # Run model.generate() in a background thread so streaming doesn't block
        generate_kwargs = {
            **inputs,
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "do_sample": request.temperature > 0,
            "pad_token_id": _tokenizer.eos_token_id,
            "streamer": streamer,   # ← inject streamer to receive tokens as they are generated
        }
        thread = Thread(target=_model.generate, kwargs=generate_kwargs)
        thread.start()

        def token_generator():
            for token in streamer:           # ← yields each token as it's generated
                yield f"data: {token}\n\n"  # ← SSE format: "data: {content}\n\n"
            yield "data: [DONE]\n\n"         # ← SSE termination signal

        return StreamingResponse(token_generator(), media_type="text/event-stream")

    @app.get("/examples")
    async def get_examples():
        """Return example prompts for testing the generate endpoint."""
        return {
            "examples": [
                {
                    "description": "Convert informal to professional",
                    "prompt": (
                        "### Instruction:\nConvert this informal message to professional email tone.\n\n"
                        "### Input:\nhey can u send me the report asap its super urgent\n\n"
                        "### Response:\n"
                    ),
                },
                {
                    "description": "Summarize text",
                    "prompt": (
                        "### Instruction:\nSummarize this text in one sentence.\n\n"
                        "### Input:\nLarge language models are trained on vast amounts of text and can perform diverse NLP tasks.\n\n"
                        "### Response:\n"
                    ),
                },
            ]
        }

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
            print("[Server] Starting on http://0.0.0.0:8000")
            print("[Server] Endpoints: GET /health, GET /metrics, POST /generate, POST /generate/stream")
            uvicorn.run("solution:app", host="0.0.0.0", port=8000, reload=False)
        except ImportError:
            print("Install uvicorn: pip install uvicorn")
    elif mode == "demo":
        # Quick demo: load model and run one inference without full training pipeline
        print("\n=== DEMO MODE: Loading model for inference ===")
        model, tokenizer = load_base_model_4bit(MODEL_NAME)
        model.eval()

        demo_prompt = (
            "### Instruction:\nConvert this informal message to professional email tone.\n\n"
            "### Input:\nhey can u send me the report asap its super urgent\n\n"
            "### Response:\n"
        )
        print(f"\nPrompt:\n{demo_prompt}")
        response, latency = generate_response(model, tokenizer, demo_prompt)
        print(f"\nGenerated:\n{response}")
        print(f"\nLatency: {latency:.0f}ms")
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python solution.py [train|serve|demo]")
        sys.exit(1)
