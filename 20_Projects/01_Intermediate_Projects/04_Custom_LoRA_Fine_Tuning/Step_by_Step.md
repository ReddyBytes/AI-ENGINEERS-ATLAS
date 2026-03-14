# Project 4 — Custom LoRA Fine-Tuning: Step-by-Step Guide

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

---

## Stage 1 — Dataset Creation

This is the most important stage. Model quality is bounded by data quality.

### Step 1: Choose your topic

Pick a topic where you can write 50–80 accurate Q&A pairs in 1–2 hours. Options:
- AI/ML concepts from this repo's theory files (good choice — you have content already)
- Python programming patterns
- A domain you work in professionally
- A well-defined knowledge area (e.g., chess openings, cooking techniques, a specific API)

For the rest of this guide, we assume you are using AI/ML concepts as the topic.

### Step 2: Understand the instruction-following format

Modern LLMs are fine-tuned on instruction-following data in a specific format. The `TinyLlama` chat model uses this template:

```
<|system|>
You are a helpful AI assistant who explains machine learning concepts clearly.</s>
<|user|>
What is the attention mechanism in transformers?</s>
<|assistant|>
The attention mechanism allows a transformer model to focus on different parts
of the input when producing each output token. Rather than compressing all input
into a single fixed vector (as RNNs do), attention computes a weighted sum over
all input positions, where the weights reflect how relevant each position is to
the current output.</s>
```

Your dataset must follow this format exactly for the model to learn correctly.

**Theory connection:** Read `14_Hugging_Face_Ecosystem/02_Transformers_Library/Theory.md` — specifically the section on chat templates and tokenization.

### Step 3: Create your JSONL dataset

Each line in `dataset.jsonl` is one example:

```json
{"messages": [{"role": "system", "content": "You are an expert AI tutor explaining machine learning concepts clearly and accurately."}, {"role": "user", "content": "What is LoRA?"}, {"role": "assistant", "content": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning technique that adds small trainable matrices to frozen pre-trained model weights. Instead of updating all parameters (which could be billions), LoRA represents weight changes as the product of two low-rank matrices, drastically reducing the number of trainable parameters — often to under 1% of the original model size."}]}
```

Write at least 50 examples. Vary the question types:
- Definition questions ("What is X?")
- How-to questions ("How does X work?")
- Comparison questions ("What is the difference between X and Y?")
- Troubleshooting questions ("Why would X fail?")
- Application questions ("When would you use X instead of Y?")

### Step 4: Validate your dataset

Before training, verify:
- All 50+ examples parse as valid JSON
- Every example has "messages" with roles "system", "user", "assistant"
- Answers are accurate — check them against theory files
- No blank questions or answers

```python
import json
from pathlib import Path

with open("dataset.jsonl") as f:
    examples = [json.loads(line) for line in f if line.strip()]

print(f"Total examples: {len(examples)}")
for i, ex in enumerate(examples[:3]):
    print(f"\nExample {i+1}:")
    for msg in ex["messages"]:
        print(f"  [{msg['role']}]: {msg['content'][:100]}...")
```

---

## Stage 2 — Environment and Base Model

### Step 5: Set up your environment (Colab recommended)

```bash
# Install all dependencies
pip install transformers peft trl datasets accelerate bitsandbytes \
            huggingface_hub gradio torch
```

If on Colab, check your GPU:
```python
import torch
print(torch.cuda.is_available())       # True on Colab with GPU enabled
print(torch.cuda.get_device_name(0))   # T4, A100, etc.
```

### Step 6: Choose your base model

| Model | Size | Tokens/sec | Good for |
|---|---|---|---|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B params, ~2GB VRAM | ~50–100 | This project (recommended) |
| `facebook/opt-125m` | 125M params, ~250MB | ~200+ | CPU testing, very fast |
| `microsoft/phi-2` | 2.7B params, ~5GB VRAM | ~20–40 | Better quality, needs more VRAM |

For this guide: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`

### Step 7: Load the base model with quantization

4-bit quantization via `bitsandbytes` reduces VRAM from ~2GB to ~700MB, fitting on Colab's free T4:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
```

**Theory connection:** Read `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md` — the quantization section explains why 4-bit training works and what precision is used for the LoRA matrices vs the frozen base weights.

---

## Stage 3 — LoRA Configuration

### Step 8: Configure LoRA

```python
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

# Prepare quantized model for training
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,                        # rank — higher = more params = more capacity
    lora_alpha=32,               # scaling: lora_alpha/r = effective lr scale
    target_modules=[             # which weight matrices to adapt
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
    lora_dropout=0.05,           # regularization
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 5,111,808 || all params: 1,105,965,056 || trainable%: 0.46
```

Understand each parameter before changing it:
- `r=16`: The rank of the decomposition. Experiment with 4, 8, 16, 32.
- `lora_alpha=32`: Try `2 * r` as a starting point.
- `target_modules`: Start with just attention projections. Adding MLP layers increases params.
- `lora_dropout=0.05`: Small regularization helps with small datasets.

### Step 9: Examine what changed

After `get_peft_model()`, the model has new modules. Inspect them:

```python
for name, param in model.named_parameters():
    if param.requires_grad:
        print(f"{name}: {param.shape}")
```

You should see only the LoRA adapter weights as trainable. The original model weights are frozen.

---

## Stage 4 — Training

### Step 10: Load and format your dataset

```python
from datasets import Dataset
import json

# Load your JSONL file
with open("dataset.jsonl") as f:
    examples = [json.loads(line) for line in f if line.strip()]

# Convert to HuggingFace Dataset
dataset = Dataset.from_list(examples)

# Split: 80% train, 20% eval
split = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = split["train"]
eval_dataset = split["test"]

print(f"Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")
```

### Step 11: Configure SFTTrainer

```python
from trl import SFTTrainer
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./lora_output",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,   # effective batch size = 2*4 = 8
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    report_to="none",                # set to "wandb" if you use Weights & Biases
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

**Theory connection:** Read `14_Hugging_Face_Ecosystem/05_Trainer_API/Theory.md` — covers `TrainingArguments` options, gradient accumulation, and evaluation strategies.

### Step 12: Train and monitor

```python
trainer.train()
```

Watch the training log. You should see:
- `loss` decreasing over steps
- `eval_loss` decreasing over epochs
- If `eval_loss` increases while `train_loss` decreases, you are overfitting (reduce epochs or increase dropout)

For 50 examples and 3 epochs on a T4, this takes ~10–15 minutes.

---

## Stage 5 — Evaluation

### Step 13: Compare base vs fine-tuned responses

Load the base model (without LoRA) and your fine-tuned model, then run the same test questions through both:

```python
def generate_response(model, tokenizer, question: str) -> str:
    """Generate a response for a question using the chat template."""
    messages = [
        {"role": "system", "content": "You are an expert AI tutor."},
        {"role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)
```

Test with 5 held-out questions not in your training set. Record both responses.

### Step 14: Evaluate qualitatively

For each test question, note:
- Did the fine-tuned model use topic-specific vocabulary correctly?
- Is the answer more accurate?
- Is the format/style more consistent?
- Are there new errors (hallucinations introduced by fine-tuning)?

Create a simple table:
| Question | Base model | Fine-tuned | Winner |

---

## Stage 6 — Push to Hugging Face Hub

### Step 15: Log in to Hugging Face Hub

```python
from huggingface_hub import login
login()  # prompts for your HF token
```

Get your token at: huggingface.co/settings/tokens

### Step 16: Save and push the LoRA adapter

You push **only the adapter weights** (~10–20 MB), not the full 1.1B parameter base model:

```python
# Save locally first
model.save_pretrained("./lora_adapter")
tokenizer.save_pretrained("./lora_adapter")

# Push to Hub
model.push_to_hub("your-username/tinyllama-ml-tutor-lora")
tokenizer.push_to_hub("your-username/tinyllama-ml-tutor-lora")
```

### Step 17: Write a model card

On the Hub, edit the README for your model. A good model card includes:
- What the model is (base model + LoRA adapter)
- What task it was trained for
- Training data description (do not share private data)
- LoRA config used
- Evaluation results
- Example input/output
- Intended use and limitations

**Theory connection:** Read `14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md`.

---

## Stage 7 — Gradio Demo on Hugging Face Spaces

### Step 18: Create a Gradio app

Create `app.py`:

```python
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_ADAPTER = "your-username/tinyllama-ml-tutor-lora"

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16)
model = PeftModel.from_pretrained(base_model, LORA_ADAPTER)
model.eval()

def answer_question(question: str) -> str:
    messages = [
        {"role": "system", "content": "You are an expert AI tutor."},
        {"role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256, temperature=0.7, do_sample=True)
    generated = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)

demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(label="Your question about AI/ML"),
    outputs=gr.Textbox(label="Answer"),
    title="AI/ML Tutor (Fine-tuned TinyLlama)",
    description="Ask questions about machine learning concepts.",
    examples=[
        ["What is LoRA and why is it useful?"],
        ["Explain the difference between RAG and fine-tuning."],
        ["What is the attention mechanism?"],
    ]
)

demo.launch()
```

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
4. The Space will build and deploy automatically (free CPU or GPU tier)

---

## Extension Challenges

1. **Hyperparameter sweep**: Train with `r = 4, 8, 16, 32`. Compare eval_loss and response quality. What is the minimum `r` that gives acceptable quality?

2. **Merge and export**: Use `model.merge_and_unload()` to merge the LoRA weights into the base model. Compare inference speed before and after merging.

3. **DPO fine-tuning**: After SFT, collect preference data (for each question, one good answer and one bad answer). Use `DPOTrainer` from `trl` to further align the model.

4. **Multi-turn conversations**: Extend your Gradio app to support chat history using `gr.ChatInterface`.

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

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| Step_by_Step.md | ← you are here |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [03 — Multi-Tool Research Agent](../03_Multi_Tool_Research_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Production RAG System](../05_Production_RAG_System/Project_Guide.md)
