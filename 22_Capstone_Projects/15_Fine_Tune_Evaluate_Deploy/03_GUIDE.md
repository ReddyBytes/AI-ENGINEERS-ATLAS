# 03 Guide — Fine-Tune, Evaluate, and Deploy

## Overview

Build the full MLOps loop in six phases. Each phase is independently testable. Training requires GPU — if you do not have one locally, use Google Colab Pro+ or a cloud instance.

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
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

Minimum VRAM: Phi-2 with QLoRA requires 8GB; Mistral-7B with QLoRA requires 14GB.

### Step 3: Choose your task domain

Pick a specific instruction-following task with clear right/wrong answers:
- Clinical note summarization
- Code review comment generation
- Customer email tone adjustment
- Structured data extraction from text
- Legal clause simplification

The task must be specific enough to measure improvement. "Be a better assistant" is too vague to fine-tune or evaluate.

<details><summary>💡 Hint</summary>

Good fine-tuning tasks have these properties:
1. The base model consistently fails in a specific, measurable way
2. There is a clear format or style the output must follow
3. You can generate synthetic training examples quickly
4. A judge can rate outputs 1–5 on task adherence

</details>

---

## Phase 1 — Dataset Preparation

### Step 4: Generate or curate 50+ training examples

Your dataset must follow the Alpaca format:
```json
{"instruction": "...", "input": "...", "output": "..."}
```

Use Claude to generate synthetic examples if you do not have real data. Vary the difficulty, edge cases, and output styles. Review each example manually — synthetic data quality matters enormously.

<details><summary>💡 Hint</summary>

Prompt Claude like this:
```
Generate 10 training examples for a model that converts informal customer emails to professional tone.
Each example: {"instruction": "Rewrite this email professionally.", "input": "<informal email>", "output": "<professional version>"}
Vary: length (1 sentence to 3 paragraphs), urgency level, technical complexity.
Return as JSON array.
```

Generate in batches of 10, then deduplicate and review.

</details>

### Step 5: Format for your model's chat template

The `format_example()` function in the starter code implements the Alpaca template for Phi-2. For Mistral, add:
```python
elif template == "mistral":
    return f"<s>[INST] {example['instruction']}\n{example['input']} [/INST] {example['output']}</s>"
```

### Step 6: Create train/validation/test splits

The starter code's `load_and_validate_dataset()` function has a 70/15/15 split. Implement the full validation:
1. Check all examples have `instruction`, `input`, `output` keys
2. Compute average token lengths
3. Warn if any example exceeds 512 tokens
4. Return a `DatasetDict` with all three splits

<details><summary>✅ Answer</summary>

```python
def load_and_validate_dataset(path: str):
    from datasets import Dataset, DatasetDict
    import json

    # Load from JSONL
    examples = []
    with open(path) as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    # Validate
    required_keys = {"instruction", "input", "output"}
    for i, ex in enumerate(examples):
        if not required_keys.issubset(ex.keys()):
            raise ValueError(f"Example {i} missing keys: {required_keys - set(ex.keys())}")

    ds = Dataset.from_list(examples)
    splits = ds.train_test_split(test_size=0.3, seed=42)
    val_test = splits["test"].train_test_split(test_size=0.5, seed=42)
    return DatasetDict({
        "train": splits["train"],
        "validation": val_test["train"],
        "test": val_test["test"],
    })
```

</details>

---

## Phase 2 — QLoRA Fine-Tuning

### Step 7: Load base model with 4-bit quantization

The `load_base_model_4bit()` function in the starter code is mostly complete. The GPU path loads the `BitsAndBytesConfig` with `load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16`. Review it and ensure it matches your model.

<details><summary>💡 Hint</summary>

`device_map="auto"` tells HuggingFace to automatically split the model across available GPUs. `trust_remote_code=True` is required for Phi-2. After loading, call `model.get_memory_footprint()` to verify you are actually using 4-bit (should be ~1.6GB for Phi-2, ~4GB for Mistral-7B).

</details>

### Step 8: Apply LoRA configuration

The `apply_lora()` function is pre-implemented in the starter code. Understand what each parameter does before running training:

| Parameter | Effect | Start here |
|---|---|---|
| `r=8` | Rank of adapter matrices | Increase to 16 if task is complex |
| `lora_alpha=32` | Scale = alpha/r = 4 | Keep ratio at 4x rank |
| `target_modules` | Which layers to adapt | q_proj + v_proj is minimum |
| `lora_dropout=0.05` | Regularization | 0.05–0.10 for small datasets |

### Step 9: Run SFTTrainer

The `run_training()` function is pre-implemented. Training will take 20–60 minutes depending on your GPU and dataset size. Monitor the loss — it should decrease each epoch. If it does not, check your data format.

<details><summary>💡 Hint</summary>

Common issues during training:
- `CUDA out of memory`: Reduce `per_device_train_batch_size` to 2, increase `gradient_accumulation_steps` to 8
- Loss not decreasing: Check that your `formatted_text` column actually contains the full prompt + response
- Very high initial loss: Your tokenizer's `pad_token` might not be set — `tokenizer.pad_token = tokenizer.eos_token`

</details>

### Step 10: Save the adapter

```python
model.save_pretrained("./adapters/custom-v1")
tokenizer.save_pretrained("./adapters/custom-v1")
```

The adapter is ~20–40MB. Load it later with `PeftModel.from_pretrained(base_model, "./adapters/custom-v1")`.

---

## Phase 3 — Before/After Evaluation

### Step 11: Load both base and fine-tuned models

```python
base_model, tokenizer = load_base_model_4bit(MODEL_NAME)
from peft import PeftModel
ft_model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
ft_model.eval()
```

### Step 12: Implement the LLM judge

The `llm_judge_score()` function needs to call Claude and return scores specific to your task.

<details><summary>💡 Hint</summary>

Your judge criteria should match your task. For email tone adjustment:
- `TASK_ADHERENCE`: Is the output professional in tone?
- `COMPLETENESS`: Does it preserve all information from the original?
- `QUALITY`: Is it well-written and natural-sounding?

Include the expected output as a reference. The judge should explain why in 1–2 sentences.

</details>

<details><summary>✅ Answer</summary>

```python
def llm_judge_score(prompt, model_output, expected, task_description):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    judge_prompt = f"""You are evaluating: {task_description}

Score this response 1-5 on:
- TASK_ADHERENCE: Does it follow the required format/style?
- COMPLETENESS: Does it address all required elements?
- QUALITY: Is it well-written for its purpose?

Prompt: {prompt}
Expected Output (reference): {expected}
Model Response: {model_output}

Return JSON: {{"task_adherence": N, "completeness": N, "quality": N, "rationale": "..."}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=150,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    try:
        scores = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        scores = {"task_adherence": 3, "completeness": 3, "quality": 3, "rationale": "parse error"}
    scores["average"] = sum([scores["task_adherence"], scores["completeness"], scores["quality"]]) / 3
    return scores
```

</details>

### Step 13: Compare and report improvement

The `run_evaluation()` function in the starter code handles the comparison loop. Your fine-tuned model should score significantly higher on task adherence — that is the primary signal. Aim for at least +0.5 points improvement.

---

## Phase 4 — Quantization for Inference

### Step 14: Benchmark inference latency

Before building the API, measure baseline latency:
```python
import time
start = time.perf_counter()
outputs = model.generate(inputs, max_new_tokens=100)
latency = (time.perf_counter() - start) * 1000
print(f"Latency: {latency:.0f}ms for 100 tokens")
```

Record these numbers — you will compare against them in the observability phase.

### Step 15: Optionally merge the adapter

For faster inference, merge the LoRA adapter into the base model:
```python
merged_model = ft_model.merge_and_unload()
merged_model.save_pretrained("./models/custom-v1-merged")
```

This removes the adapter overhead at inference time. The merged model is the full model size but runs slightly faster.

---

## Phase 5 — FastAPI Serving

### Step 16: Implement the generate endpoint

The `/generate` endpoint in `serve.py` is mostly complete. The key steps are:
1. Tokenize the prompt and count input tokens
2. Call `model.generate()`
3. Count output tokens (only the new ones, not the input)
4. Estimate cost
5. Record to `metrics_store`
6. Return `GenerateResponse`

<details><summary>💡 Hint</summary>

To count only new tokens: `new_tokens = outputs[0][input_tokens:]` where `input_tokens = inputs["input_ids"].shape[1]`.

The starter code shows this pattern already. Your main job is to ensure the `metrics_store.record()` call happens in both the success and error paths.

</details>

### Step 17: Implement streaming

```python
from transformers import TextIteratorStreamer
from threading import Thread

streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)
thread = Thread(target=model.generate, kwargs={**inputs, "streamer": streamer})
thread.start()
for token in streamer:
    yield f"data: {token}\n\n"
```

### Step 18: Add request logging middleware

Log each request's path and latency. The `MetricsStore.record()` method already appends to `request_log.jsonl` — you just need to ensure every request calls it.

---

## Phase 6 — Observability

### Step 19: Implement metrics aggregation

The `MetricsStore.get_summary()` skeleton in the starter code already handles most of the computation. Verify the percentile calculation:

```python
p50 = latencies[int(len(latencies) * 0.50)]
p95 = latencies[int(len(latencies) * 0.95)]
```

<details><summary>💡 Hint</summary>

Add `requests_last_hour` by filtering records where `timestamp > (now - 1 hour)`. Parse the ISO-8601 timestamp string with `datetime.fromisoformat(r.timestamp)`.

</details>

### Step 20: Test the complete pipeline

1. Start the server: `uvicorn serve:app --reload`
2. Send 10 test requests to `POST /generate`
3. Check `GET /metrics` shows correct aggregates
4. Verify latency numbers match your Phase 4 benchmark

---

## Testing Checklist

- [ ] Dataset has 50+ examples with correct format for chosen model
- [ ] Train/validation/test splits created and documented
- [ ] Training loss decreases across 3 epochs
- [ ] Adapter saved and loadable via `PeftModel.from_pretrained`
- [ ] Base model and fine-tuned model both generate outputs on test set
- [ ] LLM judge shows improvement of at least 0.5 points on primary metric
- [ ] FastAPI server starts and responds to `/health`
- [ ] `POST /generate` returns response with latency_ms, token counts
- [ ] `GET /metrics` returns aggregate statistics
- [ ] Latency per request logged to `request_log.jsonl`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| **03_GUIDE.md** | you are here |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
