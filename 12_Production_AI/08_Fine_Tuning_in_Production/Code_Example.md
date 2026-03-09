# Code Example — Fine-Tuning in Production

Complete examples for the OpenAI fine-tuning API and HuggingFace PEFT (LoRA).

---

## Part 1: OpenAI Fine-Tuning API

The simplest production fine-tuning path: upload data, start a job, use the model.

### Step 1: Prepare Training Data

```python
"""
Prepare and validate training data for OpenAI fine-tuning.
Output format: JSONL with messages array.
"""
import json
import tiktoken

def create_training_example(system_prompt: str, user_input: str, assistant_output: str) -> dict:
    """Create a single fine-tuning training example."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_output}
        ]
    }

def validate_training_file(examples: list, max_tokens: int = 4096) -> dict:
    """
    Validate training examples before uploading.
    Returns validation report.
    """
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    issues = []
    token_counts = []

    for i, ex in enumerate(examples):
        # Check structure
        if "messages" not in ex:
            issues.append(f"Example {i}: missing 'messages' key")
            continue

        messages = ex["messages"]

        # Check roles
        roles = [m.get("role") for m in messages]
        if roles[-1] != "assistant":
            issues.append(f"Example {i}: last message must be from 'assistant', got {roles[-1]}")

        # Count tokens
        full_text = " ".join(m.get("content", "") for m in messages)
        token_count = len(enc.encode(full_text))
        token_counts.append(token_count)

        if token_count > max_tokens:
            issues.append(f"Example {i}: {token_count} tokens exceeds max {max_tokens}")

    return {
        "total_examples": len(examples),
        "issues": issues,
        "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
        "max_tokens": max(token_counts) if token_counts else 0,
        "estimated_cost": len(examples) * sum(token_counts) / len(token_counts) * 0.000008  # ~$0.008/1K tokens
    }

def save_training_file(examples: list, filepath: str):
    """Save training examples as JSONL."""
    with open(filepath, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"Saved {len(examples)} examples to {filepath}")

# ─── Example: Product classifier training data ────────────────────────────────
SYSTEM_PROMPT = "You classify e-commerce products. Return JSON with category and subcategory."

training_examples = [
    create_training_example(
        SYSTEM_PROMPT,
        "Blue denim jeans, men's size 32x30, straight leg fit",
        '{"category": "Clothing", "subcategory": "Pants", "gender": "Men"}'
    ),
    create_training_example(
        SYSTEM_PROMPT,
        "Wireless Bluetooth headphones, noise-canceling, black",
        '{"category": "Electronics", "subcategory": "Audio", "type": "Headphones"}'
    ),
    create_training_example(
        SYSTEM_PROMPT,
        "14-piece non-stick cookware set, dishwasher safe",
        '{"category": "Kitchen", "subcategory": "Cookware", "piece_count": 14}'
    ),
    # Add 100+ more examples...
]

# Validate before uploading
report = validate_training_file(training_examples)
print(f"Validation: {len(report['issues'])} issues, avg {report['avg_tokens']:.0f} tokens/example")
if report["issues"]:
    for issue in report["issues"]:
        print(f"  ⚠️  {issue}")

save_training_file(training_examples, "product_classifier_train.jsonl")
```

### Step 2: Upload and Start Fine-Tuning Job

```python
"""
Upload training data and start an OpenAI fine-tuning job.
Requirements: pip install openai
"""
import time
from openai import OpenAI

client = OpenAI()

def upload_training_file(filepath: str) -> str:
    """Upload training file and return file_id."""
    print(f"Uploading {filepath}...")
    with open(filepath, "rb") as f:
        response = client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded: {response.id}")
    return response.id

def start_fine_tuning_job(
    training_file_id: str,
    model: str = "gpt-3.5-turbo",
    n_epochs: int = 3,
    suffix: str = "product-classifier"
) -> str:
    """Start a fine-tuning job and return job_id."""
    job = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model=model,
        hyperparameters={"n_epochs": n_epochs},
        suffix=suffix  # Your fine-tuned model will be named gpt-3.5-turbo-...:product-classifier
    )
    print(f"Fine-tuning job started: {job.id}")
    print(f"Status: {job.status}")
    return job.id

def wait_for_completion(job_id: str, check_interval: int = 60) -> dict:
    """Poll job status until completion. Returns final job details."""
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        print(f"Status: {job.status} | Events: {len(job.result_files)} result files")

        if job.status in ["succeeded", "failed", "cancelled"]:
            if job.status == "succeeded":
                print(f"✅ Fine-tuning complete! Model: {job.fine_tuned_model}")
            else:
                print(f"❌ Fine-tuning {job.status}")
            return job

        time.sleep(check_interval)

# ─── Run the pipeline ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Upload
    file_id = upload_training_file("product_classifier_train.jsonl")

    # Step 2: Start job
    job_id = start_fine_tuning_job(
        training_file_id=file_id,
        model="gpt-3.5-turbo",
        n_epochs=3,
        suffix="prod-v1"
    )

    # Step 3: Wait for completion (async in production — don't block)
    job = wait_for_completion(job_id)

    if job.status == "succeeded":
        fine_tuned_model = job.fine_tuned_model
        print(f"\nFine-tuned model ID: {fine_tuned_model}")
        # Save this ID — you'll use it to call the model
```

### Step 3: Evaluate and Use the Fine-Tuned Model

```python
"""
Compare fine-tuned model vs base model on held-out evaluation set.
"""
import json
from openai import OpenAI

client = OpenAI()
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-...:prod-v1"  # Your fine-tuned model ID
BASE_MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT = "You classify e-commerce products. Return JSON with category and subcategory."

# Held-out evaluation set (never used in training)
EVAL_SET = [
    {
        "input": "Pink floral summer dress, women's size S",
        "expected": {"category": "Clothing", "subcategory": "Dresses", "gender": "Women"}
    },
    {
        "input": "USB-C charging cable, 6 feet, fast charging",
        "expected": {"category": "Electronics", "subcategory": "Cables & Chargers"}
    },
    # Add 20+ more held-out examples
]

def evaluate_model(model_id: str, eval_examples: list) -> dict:
    """Run evaluation on a model and return metrics."""
    results = []

    for ex in eval_examples:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ex["input"]}
            ],
            max_tokens=100
        )
        output_text = response.choices[0].message.content

        # Check if output is valid JSON
        try:
            parsed = json.loads(output_text)
            is_valid_json = True
            # Check if category matches expected
            category_correct = parsed.get("category") == ex["expected"].get("category")
        except json.JSONDecodeError:
            is_valid_json = False
            category_correct = False

        results.append({
            "input": ex["input"],
            "output": output_text,
            "valid_json": is_valid_json,
            "category_correct": category_correct
        })

    json_rate = sum(1 for r in results if r["valid_json"]) / len(results)
    accuracy = sum(1 for r in results if r["category_correct"]) / len(results)

    return {
        "model": model_id,
        "json_format_rate": round(json_rate, 3),
        "category_accuracy": round(accuracy, 3),
        "total_examples": len(results),
        "failures": [r for r in results if not r["valid_json"]]
    }

# Compare
print("Evaluating base model...")
base_results = evaluate_model(BASE_MODEL, EVAL_SET)
print(f"  Base model JSON rate: {base_results['json_format_rate']:.1%}")
print(f"  Base model accuracy:  {base_results['category_accuracy']:.1%}")

print("\nEvaluating fine-tuned model...")
ft_results = evaluate_model(FINE_TUNED_MODEL, EVAL_SET)
print(f"  Fine-tuned JSON rate: {ft_results['json_format_rate']:.1%}")
print(f"  Fine-tuned accuracy:  {ft_results['category_accuracy']:.1%}")

improvement = ft_results['category_accuracy'] - base_results['category_accuracy']
print(f"\nImprovement: {improvement:+.1%}")
if improvement > 0:
    print("✅ Fine-tuned model is better. Consider deploying.")
else:
    print("❌ No improvement. Review training data quality.")
```

---

## Part 2: HuggingFace PEFT (LoRA) for Open-Source Models

```python
"""
Fine-tune a Mistral-7B model with LoRA using HuggingFace PEFT.
Requirements: pip install transformers peft datasets accelerate bitsandbytes
Recommended: Run on GPU with 16+ GB VRAM (or use QLoRA for 8GB)
"""
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset

# ─── Load model with QLoRA (4-bit quantization + LoRA) ───────────────────────
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                    # 4-bit quantization
    bnb_4bit_use_double_quant=True,       # Double quantization for extra memory savings
    bnb_4bit_quant_type="nf4",            # NF4 quantization type
    bnb_4bit_compute_dtype=torch.float16  # Compute in fp16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model)  # Prepare quantized model for training

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# ─── Configure LoRA ───────────────────────────────────────────────────────────
lora_config = LoraConfig(
    r=16,                       # Rank — number of dimensions in low-rank matrices
    lora_alpha=32,              # Scaling factor (alpha/r = actual scaling)
    target_modules=[            # Which layers to apply LoRA to
        "q_proj", "v_proj",     # Attention query and value projections
        "k_proj", "o_proj",     # Attention key and output projections
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Check how many parameters are trainable
trainable, total = 0, 0
for _, param in model.named_parameters():
    total += param.numel()
    if param.requires_grad:
        trainable += param.numel()
print(f"Trainable: {trainable:,} ({100 * trainable / total:.2f}% of {total:,} total)")
# → Trainable: 13,631,488 (0.19% of 7,241,732,096 total)

# ─── Prepare dataset ─────────────────────────────────────────────────────────
def format_instruction(example):
    """Format a single example into the instruction-following format."""
    return {
        "text": f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    }

# Example dataset (replace with your actual data)
raw_data = [
    {"instruction": "Classify this product", "input": "Blue jeans, size 32", "output": '{"category": "Clothing"}'},
    {"instruction": "Classify this product", "input": "Wireless earbuds", "output": '{"category": "Electronics"}'},
    # ... more examples
]

dataset = Dataset.from_list([format_instruction(ex) for ex in raw_data])

# ─── Training configuration ──────────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir="./fine_tuned_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,     # Effective batch size = 4 × 4 = 16
    warmup_steps=100,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    report_to="none",                  # Change to "wandb" to track in W&B
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=training_args,
    peft_config=lora_config,
)

# ─── Run training ─────────────────────────────────────────────────────────────
print("Starting training...")
trainer.train()

# ─── Save the fine-tuned model ────────────────────────────────────────────────
trainer.save_model("./fine_tuned_model")
print("Model saved to ./fine_tuned_model")

# ─── Inference with fine-tuned model ─────────────────────────────────────────
from peft import PeftModel

# Load for inference
base_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model_loaded = PeftModel.from_pretrained(base_model, "./fine_tuned_model")

def generate(prompt: str, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model_loaded.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

result = generate("### Instruction:\nClassify this product\n\n### Input:\nRunning shoes, women's size 8\n\n### Response:\n")
print(result)
```

---

## 📂 Navigation
