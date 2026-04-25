# Project 09 — Custom LoRA Fine-Tuning: Build Guide

## Overview

| Stage | What you build | Time estimate |
|---|---|---|
| 1 | Dataset creation and formatting | 60–90 min |
| 2 | Environment and base model loading | 30 min |
| 3 | LoRA configuration | 20 min |
| 4 | SFTTrainer setup and training run | 30 min + training time |
| 5 | Evaluation (before vs after) | 30 min |
| 6 | Push to Hugging Face Hub | 20 min |
| 7 | Gradio demo and Spaces deployment | 45 min |

Total: approximately 4–5 hours (plus training time)

Read `01_MISSION.md` and `02_ARCHITECTURE.md` before starting.

---

## Stage 1 — Dataset Creation

This is the most important stage. Model quality is bounded by data quality.

### Step 1: Choose your topic

Pick a topic where you can write 50–80 accurate Q&A pairs in 1–2 hours. Options:
- AI/ML concepts from this repo's theory files (you have content already)
- Python programming patterns
- A domain you work in professionally
- A well-defined knowledge area (chess openings, cooking techniques, a specific API)

### Step 2: Understand the instruction-following format

Modern LLMs are fine-tuned on instruction-following data in a specific format. TinyLlama uses this template:

```
<|system|>
You are a helpful AI assistant who explains machine learning concepts clearly.</s>
<|user|>
What is the attention mechanism in transformers?</s>
<|assistant|>
The attention mechanism allows a transformer model to focus on different parts
of the input when producing each output token...</s>
```

Your dataset must follow the `messages` format for the tokenizer to apply the correct template automatically.

**Theory connection:** Read `14_Hugging_Face_Ecosystem/02_Transformers_Library/Theory.md` — specifically the chat templates and tokenization section.

### Step 3: Create your JSONL dataset

Each line in `dataset.jsonl` is one JSON object:

```json
{"messages": [
  {"role": "system", "content": "You are an expert AI tutor explaining machine learning concepts clearly and accurately."},
  {"role": "user", "content": "What is LoRA?"},
  {"role": "assistant", "content": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning technique that adds small trainable matrices to frozen pre-trained model weights. Instead of updating all parameters, LoRA represents weight changes as the product of two low-rank matrices, reducing trainable parameters to under 1% of the original model size."}
]}
```

Write at least 50 examples. Vary the question types: definition questions, how-to questions, comparison questions, troubleshooting questions, application questions.

### Step 4: Validate your dataset

<details><summary>💡 Hint</summary>

Read the JSONL file line by line, parse each line as JSON. Check that each example has a `messages` key that is a list, each message has `role` and `content`, and `content` is a non-empty string. Print a summary: total examples, skipped examples.

</details>

<details><summary>✅ Answer</summary>

```python
import json

def validate_example(example: dict) -> bool:
    if "messages" not in example or not isinstance(example["messages"], list):
        return False
    if len(example["messages"]) < 2:
        return False
    for msg in example["messages"]:
        if not isinstance(msg, dict):
            return False
        if "role" not in msg or "content" not in msg:
            return False
        if not isinstance(msg["content"], str) or not msg["content"].strip():
            return False
    return True

with open("dataset.jsonl") as f:
    all_examples = []
    skipped = 0
    for line in f:
        if not line.strip():
            continue
        try:
            ex = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if validate_example(ex):
            all_examples.append(ex)
        else:
            skipped += 1

print(f"Valid: {len(all_examples)}, Skipped: {skipped}")
```

</details>

---

## Stage 2 — Environment and Base Model

### Step 5: Set up your environment (Colab recommended)

```bash
pip install transformers peft trl datasets accelerate bitsandbytes \
            huggingface_hub gradio torch
```

If on Colab, check your GPU:
```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

### Step 6: Choose your base model

| Model | Size | Tokens/sec (T4) | Good for |
|---|---|---|---|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B params, ~2GB VRAM | ~50–100 | This project (recommended) |
| `facebook/opt-125m` | 125M params, ~250MB | ~200+ | CPU testing, very fast |
| `microsoft/phi-2` | 2.7B params, ~5GB VRAM | ~20–40 | Better quality, needs more VRAM |

### Step 7: Load the base model with quantization

<details><summary>💡 Hint</summary>

Create a `BitsAndBytesConfig` with `load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_compute_dtype=torch.float16`, `bnb_4bit_use_double_quant=True`. Pass it to `AutoModelForCausalLM.from_pretrained()` with `device_map="auto"`. Skip quantization if `torch.cuda.is_available()` is False.

</details>

<details><summary>✅ Answer</summary>

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

if torch.cuda.is_available():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id, quantization_config=bnb_config, device_map="auto"
    )
else:
    model = AutoModelForCausalLM.from_pretrained(model_id)

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
```

</details>

**Theory connection:** Read `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md` — the quantization section explains why 4-bit training works.

---

## Stage 3 — LoRA Configuration

### Step 8: Configure LoRA

<details><summary>💡 Hint</summary>

Call `prepare_model_for_kbit_training(model)` first — required on quantized models. Then create `LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj","o_proj"], lora_dropout=0.05, bias="none", task_type=TaskType.CAUSAL_LM)`. Wrap with `get_peft_model(model, lora_config)`.

</details>

<details><summary>✅ Answer</summary>

```python
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Expected: trainable params: ~5M || all params: 1.1B || trainable%: 0.46
```

</details>

### Step 9: Examine what changed

After `get_peft_model()`, inspect which parameters are trainable:

```python
for name, param in model.named_parameters():
    if param.requires_grad:
        print(f"{name}: {param.shape}")
```

You should see only the LoRA adapter weights (`lora_A` and `lora_B` matrices). The original model weights are frozen.

---

## Stage 4 — Training

### Step 10: Load and format your dataset

<details><summary>✅ Answer</summary>

```python
from datasets import Dataset

dataset = Dataset.from_list(all_examples)
split = dataset.train_test_split(test_size=0.15, seed=42)
train_dataset = split["train"]
eval_dataset = split["test"]
print(f"Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")
```

</details>

### Step 11: Configure SFTTrainer

<details><summary>💡 Hint</summary>

Create `TrainingArguments(output_dir=..., num_train_epochs=3, per_device_train_batch_size=2, gradient_accumulation_steps=4, learning_rate=2e-4, fp16=torch.cuda.is_available(), logging_steps=5, evaluation_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True, report_to="none")`. Then create `SFTTrainer(model, train_dataset, eval_dataset, tokenizer, args, max_seq_length=512)`.

</details>

<details><summary>✅ Answer</summary>

```python
from trl import SFTTrainer
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./lora_output",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=torch.cuda.is_available(),
    logging_steps=5,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=512,
)
```

</details>

**Theory connection:** Read `14_Hugging_Face_Ecosystem/05_Trainer_API/Theory.md` — covers `TrainingArguments`, gradient accumulation, and evaluation strategies.

### Step 12: Train and monitor

```python
trainer.train()
```

Watch the training log:
- `loss` should decrease over steps
- `eval_loss` should decrease over epochs
- If `eval_loss` increases while `train_loss` decreases, you are overfitting — reduce epochs or increase dropout

---

## Stage 5 — Evaluation

### Step 13: Compare base vs fine-tuned responses

<details><summary>💡 Hint</summary>

Write a `generate_response(model, tokenizer, question)` function. Apply the chat template with `tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)`. Tokenize the prompt, call `model.generate(...)`, then decode only the new tokens by slicing `outputs[0][inputs.input_ids.shape[1]:]`.

</details>

<details><summary>✅ Answer</summary>

```python
def generate_response(model, tokenizer, question: str, max_new_tokens: int = 256) -> str:
    messages = [
        {"role": "system", "content": "You are an expert AI tutor."},
        {"role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            temperature=0.7, do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)
```

</details>

Test with 5 held-out questions not in your training set. Record both responses.

### Step 14: Evaluate qualitatively

For each test question, note:
- Did the fine-tuned model use topic-specific vocabulary correctly?
- Is the answer more accurate?
- Is the format/style more consistent?
- Are there new errors (hallucinations introduced by fine-tuning)?

Create a comparison table: Question | Base model | Fine-tuned | Winner

---

## Stage 6 — Push to Hugging Face Hub

### Step 15: Log in

```python
from huggingface_hub import login
login()  # prompts for your HF token
```

Get your token at: huggingface.co/settings/tokens

### Step 16: Save and push the LoRA adapter

You push only the adapter weights (~10–20 MB), not the full 1.1B parameter base model:

```python
model.save_pretrained("./lora_adapter")
tokenizer.save_pretrained("./lora_adapter")
model.push_to_hub("your-username/tinyllama-ml-tutor-lora")
tokenizer.push_to_hub("your-username/tinyllama-ml-tutor-lora")
```

### Step 17: Write a model card

On the Hub, edit the README for your model. A good model card includes: base model, task, training data description, LoRA config, evaluation results, example input/output, intended use and limitations.

**Theory connection:** Read `14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md`.

---

## Stage 7 — Gradio Demo on Hugging Face Spaces

### Step 18: Create and test a Gradio app

<details><summary>💡 Hint</summary>

Load the base model once at module startup with `PeftModel.from_pretrained(base_model, LORA_ADAPTER_ID)`. Set `model.eval()`. Write a `answer_question(question: str) -> str` function that runs the generation logic. Pass it to `gr.Interface(fn=answer_question, inputs=gr.Textbox(...), outputs=gr.Textbox(...))`.

</details>

### Step 19: Deploy to Hugging Face Spaces

1. Go to huggingface.co/spaces → Create new Space
2. Choose Gradio as the SDK
3. Upload your `app.py` and create a `requirements.txt`:
   ```
   transformers
   peft
   torch
   accelerate
   gradio
   ```
4. The Space will build and deploy automatically

---

## Checklist Before Moving On

- [ ] Dataset has 50+ examples in correct JSONL format
- [ ] All examples pass the validation check (valid JSON, correct roles)
- [ ] Training loss decreases over epochs
- [ ] At least 5 held-out questions evaluated before and after
- [ ] LoRA adapter is on Hugging Face Hub
- [ ] Model card is written with training details
- [ ] Gradio demo works locally
- [ ] (Optional) Gradio app deployed to Spaces

---

## Common Mistakes

**Not calling `prepare_model_for_kbit_training()`**: Skipping this on a quantized model causes gradient computation errors. Always call it before `get_peft_model()`.

**Wrong chat template format**: Different models use different special tokens. Check the model's tokenizer config if generation looks wrong.

**Training on CPU**: Will take hours for even 50 examples. Use GPU. Google Colab free tier is sufficient.

**Pushing full model instead of adapter**: `model.save_pretrained()` on a PeftModel saves only the adapter (~10MB). That is correct. Do not call `.merge_and_unload()` before pushing if you want to share just the adapter.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| 03_GUIDE.md | you are here |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
