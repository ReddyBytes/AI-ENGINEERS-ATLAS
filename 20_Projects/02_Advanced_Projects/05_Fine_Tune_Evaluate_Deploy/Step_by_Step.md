# Project 5: Step-by-Step Build Guide

## Overview

Build the full MLOps loop in six phases. Each phase is independently testable. Training requires GPU — if you don't have one locally, use Google Colab Pro+ or a cloud instance.

---

## Phase 0 — Environment Setup

### Step 1: Install dependencies

```bash
pip install transformers peft trl bitsandbytes datasets \
    fastapi uvicorn anthropic torch accelerate
```

### Step 2: Verify GPU availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB" if torch.cuda.is_available() else "")
```

Minimum VRAM requirements:
- Phi-2 (2.7B) with QLoRA: 8GB
- Mistral-7B with QLoRA: 14GB
- Mistral-7B without quantization: 28GB

### Step 3: Choose your task domain

Pick a specific instruction-following task with clear right/wrong answers:
- Clinical note summarization
- Code review comment generation
- Customer email tone adjustment
- Structured data extraction from text
- Legal clause simplification

**The task must be specific enough to measure improvement.** "Be a better assistant" is too vague to fine-tune or evaluate.

**Theory checkpoint:** Read `12_Production_AI/08_Fine_Tuning_in_Production/Theory.md` — specifically the "When to fine-tune vs. prompt engineer" section.

---

## Phase 1 — Dataset Preparation

### Step 4: Generate or curate 50+ training examples

Your dataset must follow the Alpaca format:
```json
{"instruction": "...", "input": "...", "output": "..."}
```

Strategies for getting data:
- **Option A:** Use Claude to generate synthetic examples (document this clearly)
- **Option B:** Curate from public datasets on HuggingFace Hub
- **Option C:** Collect from real task examples you have

For synthetic data generation:
```python
# Use Claude to generate 50 varied examples of your task
# Vary the difficulty, edge cases, and output styles
# Review each example manually — synthetic data quality matters enormously
```

### Step 5: Format for your model's chat template

Different models use different chat templates. For Phi-2:
```
### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}
```

For Mistral Instruct:
```
<s>[INST] {instruction}\n{input} [/INST] {output}</s>
```

TRL's SFTTrainer can apply templates automatically — read its documentation.

### Step 6: Create train/validation/test splits

```python
from datasets import load_dataset, DatasetDict

# 70/15/15 split
dataset = load_dataset("json", data_files="dataset.jsonl")
splits = dataset["train"].train_test_split(test_size=0.3, seed=42)
val_test = splits["test"].train_test_split(test_size=0.5, seed=42)
ds = DatasetDict({
    "train": splits["train"],
    "validation": val_test["train"],
    "test": val_test["test"],
})
```

Compute average token lengths for train and validation. If any example exceeds 512 tokens, truncate or split.

**Theory checkpoint:** Read `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md`.

---

## Phase 2 — QLoRA Fine-Tuning

### Step 7: Load base model with 4-bit quantization

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
)
```

### Step 8: Apply LoRA configuration

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,                    # Rank — higher = more capacity, more VRAM
    lora_alpha=32,          # Scaling factor; alpha/r = effective learning rate multiplier
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

### Step 9: Run SFTTrainer

```python
from trl import SFTTrainer
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./checkpoints",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_steps=50,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=ds["train"],
    eval_dataset=ds["validation"],
    dataset_text_field="formatted_text",  # Column with full prompt+response
    max_seq_length=512,
    tokenizer=tokenizer,
    args=training_args,
)
trainer.train()
```

Monitor: loss should decrease each epoch. If it doesn't, check your data format.

### Step 10: Save the adapter

```python
model.save_pretrained("./adapters/custom-v1")
tokenizer.save_pretrained("./adapters/custom-v1")
```

The adapter is ~20-40MB (not the full model). Load it with `PeftModel.from_pretrained(base_model, "./adapters/custom-v1")`.

**Theory checkpoint:** Read `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/When_to_Use.md`.

---

## Phase 3 — Before/After Evaluation

### Step 11: Load both base and fine-tuned models

```python
# Base model
base_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, ...)

# Fine-tuned model
from peft import PeftModel
ft_model = PeftModel.from_pretrained(base_model, "./adapters/custom-v1")
```

### Step 12: Generate outputs on test set

For each of the 10 test examples, generate outputs from both models using identical prompts and decoding settings (temperature=0.1 for reproducibility).

Log inputs, base model outputs, and fine-tuned model outputs to a file.

### Step 13: Run LLM-as-judge evaluation

Use Claude to score each `(prompt, output, expected_output)` triple on task-specific criteria:

```python
judge_prompt = f"""
You are evaluating responses for the task: [YOUR TASK DESCRIPTION]

Score this response 1-5 on:
- TASK_ADHERENCE: Does it follow the required format/style?
- COMPLETENESS: Does it address all required elements?
- QUALITY: Is it well-written for its purpose?

Question/Prompt: {prompt}
Expected Output (reference): {expected_output}
Model Response: {model_output}

Return JSON: {{"task_adherence": N, "completeness": N, "quality": N, "rationale": "..."}}
"""
```

### Step 14: Compare and report improvement

Calculate average scores for base vs. fine-tuned. The fine-tuned model should score significantly higher on task adherence — that's the primary signal.

**Theory checkpoint:** Read `18_AI_Evaluation/03_LLM_as_Judge/Theory.md` for calibration advice.

---

## Phase 4 — Quantization for Inference

### Step 15: Save a merged 4-bit model for serving

For production serving, merge the LoRA adapter into the base model and re-quantize:

```python
# Merge adapter into base model (creates full model weights)
merged_model = ft_model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("./models/custom-v1-merged")
```

Alternatively, load with 4-bit quantization at inference time — simpler but slightly slower on first load.

### Step 16: Benchmark inference latency

Before building the API, measure baseline latency:
```python
import time
start = time.perf_counter()
outputs = model.generate(inputs, max_new_tokens=100)
latency = (time.perf_counter() - start) * 1000
print(f"Latency: {latency:.0f}ms for {100} tokens")
print(f"Throughput: {100 / (latency/1000):.1f} tokens/sec")
```

Record these numbers — you'll compare against them in the observability phase.

**Theory checkpoint:** Read `14_Hugging_Face_Ecosystem/06_Inference_Optimization/Theory.md`.

---

## Phase 5 — FastAPI Serving

### Step 17: Build the FastAPI app

Create `serve.py` with:
- `POST /generate` — takes prompt, returns response with metadata
- `GET /health` — returns model status
- `GET /metrics` — returns aggregate stats (total requests, avg latency, total tokens)

### Step 18: Add streaming support

```python
from fastapi.responses import StreamingResponse

@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    async def stream_tokens():
        # Use model.generate() with a TextIteratorStreamer
        # Yield each token as it's generated
        ...
    return StreamingResponse(stream_tokens(), media_type="text/event-stream")
```

### Step 19: Add request logging middleware

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    # Log to a JSON file or in-memory store
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "path": request.url.path,
        "latency_ms": round(latency_ms, 2),
    }
    ...
    return response
```

---

## Phase 6 — Observability

### Step 20: Implement token counting and cost estimation

```python
def estimate_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """
    Estimate cost in USD.
    For self-hosted models: estimate compute cost based on
    GPU hourly rate and tokens/second throughput.
    """
    # Example: A100 GPU at $2/hr, 50 tokens/sec
    gpu_cost_per_hour = 2.0
    tokens_per_second = 50.0
    total_tokens = input_tokens + output_tokens
    time_seconds = total_tokens / tokens_per_second
    return (time_seconds / 3600) * gpu_cost_per_hour
```

### Step 21: Build the metrics dashboard endpoint

`GET /metrics` should return:
```json
{
    "total_requests": 147,
    "avg_latency_ms": 823,
    "p95_latency_ms": 1204,
    "total_input_tokens": 18432,
    "total_output_tokens": 22910,
    "total_cost_usd": 0.00234,
    "error_rate": 0.007
}
```

### Step 22: Test the complete pipeline

1. Start the server: `uvicorn serve:app --reload`
2. Send 10 test requests
3. Check `/metrics` shows correct aggregates
4. Verify latency numbers match your Phase 4 benchmark

**Theory checkpoint:** Read `12_Production_AI/05_Observability/Theory.md` and `Tools_Guide.md`.

---

## Testing Checklist

- [ ] Dataset has 50+ examples with correct format for chosen model
- [ ] Train/validation/test splits created and documented
- [ ] Training loss decreases across 3 epochs
- [ ] Adapter saved and loadable (`PeftModel.from_pretrained`)
- [ ] Base model and fine-tuned model both generate outputs on test set
- [ ] LLM judge shows improvement of at least 0.5 points on primary metric
- [ ] FastAPI server starts and responds to `/health`
- [ ] `POST /generate` returns response with latency_ms, token counts
- [ ] `GET /metrics` returns aggregate statistics
- [ ] Latency per request logged to file
