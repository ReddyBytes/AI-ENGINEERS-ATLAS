# Project 4 — Custom LoRA Fine-Tuning: Starter Code

## How to Use This File

Three scripts to implement:
1. `fine_tune.py` — training script (main TODOs)
2. `evaluate.py` — before/after comparison
3. `app.py` — Gradio demo

All three have working scaffolding. Fill in the `# TODO:` sections.

Run on GPU (Google Colab T4 recommended). CPU-only will be very slow.

---

## Setup

```bash
pip install transformers peft trl datasets accelerate bitsandbytes \
            huggingface_hub gradio torch
```

---

## `fine_tune.py`

```python
"""
LoRA Fine-Tuning Script
=======================
Fine-tune TinyLlama on a custom Q&A dataset using LoRA and SFTTrainer.

Usage:
    python fine_tune.py --dataset dataset.jsonl --output ./lora_output

Requirements:
    pip install transformers peft trl datasets accelerate bitsandbytes torch
    GPU strongly recommended (Google Colab T4 is sufficient)
"""

import argparse
import json
import os
import torch
from pathlib import Path

from datasets import Dataset
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer

# ---------------------------------------------------------------------------
# Configuration — edit these to experiment
# ---------------------------------------------------------------------------

BASE_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DATASET_FILE = "dataset.jsonl"
OUTPUT_DIR = "./lora_output"
HF_REPO_NAME = None   # e.g., "your-username/my-model-lora" — set before pushing

# LoRA hyperparameters
LORA_R = 16                             # rank
LORA_ALPHA = 32                         # scaling factor
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]

# Training hyperparameters
NUM_EPOCHS = 3
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 4        # effective batch = BATCH_SIZE * GRAD_ACCUM
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 512
EVAL_SPLIT = 0.15                       # fraction of data held out for eval


# ---------------------------------------------------------------------------
# Step 1: Dataset loading and validation
# ---------------------------------------------------------------------------

def load_dataset_from_jsonl(file_path: str) -> tuple[Dataset, Dataset]:
    """
    Load dataset from JSONL file and split into train/eval.

    Expected format per line:
        {"messages": [
            {"role": "system",    "content": "..."},
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."}
        ]}

    Returns:
        (train_dataset, eval_dataset) as HuggingFace Dataset objects.
    """
    # TODO: Read the JSONL file line by line.
    #       Parse each line as JSON (skip blank lines and catch JSONDecodeError).
    #       Validate each example: must have "messages" key with list of dicts,
    #       each dict must have "role" and "content" keys.
    #       Print validation summary: total examples, skipped examples.
    #
    #       Create a HuggingFace Dataset from the valid examples list:
    #           dataset = Dataset.from_list(examples)
    #
    #       Split with train_test_split(test_size=EVAL_SPLIT, seed=42).
    #       Return (split["train"], split["test"]).
    pass


def validate_example(example: dict) -> bool:
    """Return True if the example has the expected structure."""
    # TODO: Check that:
    #   - "messages" key exists and is a list
    #   - list has at least 2 elements (user + assistant minimum)
    #   - each element is a dict with "role" and "content"
    #   - "content" is a non-empty string
    #   Return False (not raise) if any check fails.
    pass


# ---------------------------------------------------------------------------
# Step 2: Model and tokenizer loading
# ---------------------------------------------------------------------------

def load_model_and_tokenizer(model_id: str):
    """
    Load base model with 4-bit quantization and the corresponding tokenizer.

    Returns:
        (model, tokenizer) tuple.
    """
    print(f"Loading model: {model_id}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    # TODO: Create a BitsAndBytesConfig for 4-bit quantization:
    #   load_in_4bit=True
    #   bnb_4bit_quant_type="nf4"
    #   bnb_4bit_compute_dtype=torch.float16
    #   bnb_4bit_use_double_quant=True
    #
    # If CUDA is not available (CPU only), skip quantization:
    #   use AutoModelForCausalLM.from_pretrained(model_id) without bnb_config.
    bnb_config = None  # replace with BitsAndBytesConfig

    # TODO: Load the model with AutoModelForCausalLM.from_pretrained():
    #   model_id=model_id
    #   quantization_config=bnb_config  (or omit if CPU)
    #   device_map="auto"
    model = None  # replace

    # TODO: Load the tokenizer with AutoTokenizer.from_pretrained(model_id).
    #       Set tokenizer.pad_token = tokenizer.eos_token
    #       Set tokenizer.padding_side = "right"
    tokenizer = None  # replace

    return model, tokenizer


# ---------------------------------------------------------------------------
# Step 3: Apply LoRA
# ---------------------------------------------------------------------------

def apply_lora(model) -> tuple:
    """
    Prepare model for training and apply LoRA adapters.

    Returns:
        (peft_model, lora_config) tuple.
    """
    # TODO: Call prepare_model_for_kbit_training(model).
    #       This enables gradient checkpointing and casts norms to float32.

    # TODO: Create LoraConfig with the constants defined at the top of this file:
    #   r=LORA_R
    #   lora_alpha=LORA_ALPHA
    #   target_modules=LORA_TARGET_MODULES
    #   lora_dropout=LORA_DROPOUT
    #   bias="none"
    #   task_type=TaskType.CAUSAL_LM
    lora_config = None  # replace

    # TODO: Call get_peft_model(model, lora_config) to wrap the model.
    peft_model = None  # replace

    # Print trainable parameter count
    peft_model.print_trainable_parameters()

    return peft_model, lora_config


# ---------------------------------------------------------------------------
# Step 4: Training
# ---------------------------------------------------------------------------

def build_trainer(
    model,
    tokenizer,
    train_dataset: Dataset,
    eval_dataset: Dataset,
    output_dir: str,
) -> SFTTrainer:
    """
    Configure and return an SFTTrainer instance.
    """
    # TODO: Create TrainingArguments with these settings (adjust as needed):
    #   output_dir=output_dir
    #   num_train_epochs=NUM_EPOCHS
    #   per_device_train_batch_size=BATCH_SIZE
    #   gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS
    #   learning_rate=LEARNING_RATE
    #   fp16=torch.cuda.is_available()
    #   logging_steps=5
    #   evaluation_strategy="epoch"
    #   save_strategy="epoch"
    #   load_best_model_at_end=True
    #   report_to="none"
    training_args = None  # replace

    # TODO: Create and return an SFTTrainer with:
    #   model=model
    #   train_dataset=train_dataset
    #   eval_dataset=eval_dataset
    #   tokenizer=tokenizer
    #   args=training_args
    #   max_seq_length=MAX_SEQ_LENGTH
    #
    # SFTTrainer handles chat template formatting automatically when the dataset
    # has a "messages" column — which ours does.
    pass


# ---------------------------------------------------------------------------
# Step 5: Save and push to Hub
# ---------------------------------------------------------------------------

def save_and_push(model, tokenizer, output_dir: str, hub_repo: str = None) -> None:
    """
    Save the LoRA adapter locally and optionally push to Hugging Face Hub.
    """
    # TODO: Call model.save_pretrained(output_dir).
    #       Call tokenizer.save_pretrained(output_dir).
    #       Print a confirmation message with the output directory.

    if hub_repo:
        # TODO: Call model.push_to_hub(hub_repo).
        #       Call tokenizer.push_to_hub(hub_repo).
        #       Print the Hub URL: f"https://huggingface.co/{hub_repo}"
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LoRA Fine-Tuning with SFTTrainer")
    parser.add_argument("--dataset", default=DATASET_FILE, help="Path to JSONL dataset")
    parser.add_argument("--output", default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--push-to-hub", default=HF_REPO_NAME, help="HF Hub repo name")
    args = parser.parse_args()

    # Load data
    print("Loading dataset...")
    train_dataset, eval_dataset = load_dataset_from_jsonl(args.dataset)
    print(f"Train: {len(train_dataset)} examples, Eval: {len(eval_dataset)} examples")

    # Load model
    model, tokenizer = load_model_and_tokenizer(BASE_MODEL_ID)

    # Apply LoRA
    model, lora_config = apply_lora(model)

    # Build trainer
    trainer = build_trainer(model, tokenizer, train_dataset, eval_dataset, args.output)

    # Train
    print("\nStarting training...")
    trainer.train()

    # Save
    print("\nSaving adapter...")
    save_and_push(model, tokenizer, args.output, args.push_to_hub)

    print("\nDone! To evaluate, run: python evaluate.py")


if __name__ == "__main__":
    main()
```

---

## `evaluate.py`

```python
"""
Before/After Evaluation
=======================
Compare base model vs fine-tuned model on held-out test questions.

Usage:
    python evaluate.py

Requires:
    - Base model accessible (downloads from HF Hub)
    - ./lora_output/ directory with saved LoRA adapter
"""

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_ADAPTER_PATH = "./lora_output"   # or your HF Hub repo name

# Test questions — use ones NOT in your training set
TEST_QUESTIONS = [
    "What is gradient descent and why does it work?",
    "Explain the difference between overfitting and underfitting.",
    "What is the purpose of the softmax function in neural networks?",
    "How do transformers differ from RNNs?",
    "When should you use fine-tuning vs RAG?",
]


def load_base_model():
    """Load the base model without any LoRA adapter."""
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )
    return model, tokenizer


def load_finetuned_model():
    """Load base model + LoRA adapter."""
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )
    # TODO: Load LoRA adapter with PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH).
    #       Call model.eval() to set evaluation mode.
    model = None  # replace
    return model, tokenizer


def generate_response(model, tokenizer, question: str, max_new_tokens: int = 256) -> str:
    """
    Generate a response for a question using the TinyLlama chat template.
    """
    # TODO: Create messages list with system and user roles.
    #       Apply chat template: tokenizer.apply_chat_template(
    #           messages, tokenize=False, add_generation_prompt=True
    #       )
    #       Tokenize the prompt: tokenizer(prompt, return_tensors="pt").to(model.device)
    #       Generate with: model.generate(
    #           **inputs,
    #           max_new_tokens=max_new_tokens,
    #           temperature=0.7,
    #           do_sample=True,
    #           pad_token_id=tokenizer.eos_token_id,
    #       )
    #       Decode only the new tokens (slice off the input tokens).
    #       Return decoded string with skip_special_tokens=True.
    pass


def evaluate():
    """Run before/after comparison for all test questions."""
    print("Loading base model...")
    base_model, base_tokenizer = load_base_model()

    print("Loading fine-tuned model...")
    ft_model, ft_tokenizer = load_finetuned_model()

    results = []

    for i, question in enumerate(TEST_QUESTIONS, start=1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print(f"{'='*60}")

        base_answer = generate_response(base_model, base_tokenizer, question)
        ft_answer = generate_response(ft_model, ft_tokenizer, question)

        print(f"\nBASE MODEL:\n{base_answer}")
        print(f"\nFINE-TUNED MODEL:\n{ft_answer}")

        results.append({
            "question": question,
            "base_answer": base_answer,
            "finetuned_answer": ft_answer,
        })

    # Save results for review
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to evaluation_results.json")


if __name__ == "__main__":
    evaluate()
```

---

## `app.py`

```python
"""
Gradio Demo
===========
Interactive demo of the fine-tuned model for Hugging Face Spaces.

Usage (local):
    python app.py

For Spaces deployment:
    Upload this file + requirements.txt to a new Gradio Space.
"""

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_ADAPTER_ID = "your-username/tinyllama-ml-tutor-lora"  # your Hub repo

# Load once at startup (not on every request)
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)

# TODO: Load the LoRA adapter with PeftModel.from_pretrained(base_model, LORA_ADAPTER_ID).
#       Set model.eval().
model = None  # replace with your loaded PeftModel
print("Model ready.")


def answer_question(question: str) -> str:
    """
    Generate an answer for the input question using the fine-tuned model.
    Called by Gradio on each submit.
    """
    if not question.strip():
        return "Please enter a question."

    # TODO: Call generate_response logic here (same as in evaluate.py).
    #       Apply chat template, tokenize, generate, decode.
    #       Return the decoded response string.
    pass


# ---------------------------------------------------------------------------
# Gradio interface
# ---------------------------------------------------------------------------

demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(
        label="Your question",
        placeholder="Ask about machine learning concepts...",
        lines=3,
    ),
    outputs=gr.Textbox(
        label="Answer",
        lines=8,
    ),
    title="AI/ML Tutor (Fine-tuned TinyLlama + LoRA)",
    description=(
        "This model was fine-tuned on AI/ML Q&A data using LoRA. "
        "Ask questions about machine learning, transformers, RAG, agents, and more."
    ),
    examples=[
        ["What is LoRA and why is it useful?"],
        ["Explain the difference between RAG and fine-tuning."],
        ["What is the attention mechanism in transformers?"],
        ["What are the main hyperparameters in LoRA and what do they control?"],
        ["When would you use a vector database?"],
    ],
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch()
```

---

## Sample Dataset Entries

Use this as a template for your `dataset.jsonl`. Write 50+ entries like these:

```json
{"messages": [{"role": "system", "content": "You are an expert AI/ML tutor who explains concepts clearly and accurately."}, {"role": "user", "content": "What is LoRA?"}, {"role": "assistant", "content": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that freezes pre-trained model weights and adds small trainable rank-decomposition matrices alongside specific layers. Instead of updating all model parameters during fine-tuning (which could be billions), LoRA represents weight updates as the product of two low-rank matrices A (d × r) and B (r × k), where r is much smaller than d and k. This reduces trainable parameters by 90–99% while achieving comparable performance to full fine-tuning."}]}
{"messages": [{"role": "system", "content": "You are an expert AI/ML tutor who explains concepts clearly and accurately."}, {"role": "user", "content": "What is the difference between RAG and fine-tuning?"}, {"role": "assistant", "content": "RAG (Retrieval-Augmented Generation) and fine-tuning are two different ways to customize LLM behavior. RAG injects knowledge at inference time: relevant documents are retrieved and included in the context window with each query. Fine-tuning bakes knowledge into model weights during a training process. RAG is better when: knowledge changes frequently, answers must be auditable, or you have limited compute. Fine-tuning is better when: you need consistent style/format, domain-specific vocabulary is critical, or you want faster inference without retrieval overhead."}]}
{"messages": [{"role": "system", "content": "You are an expert AI/ML tutor who explains concepts clearly and accurately."}, {"role": "user", "content": "What does the rank r control in LoRA?"}, {"role": "assistant", "content": "The rank r in LoRA controls the size of the trainable adapter matrices. Specifically, LoRA adds two matrices A (shape d × r) and B (shape r × k) alongside each adapted weight matrix. A higher r means more parameters and more representational capacity — the adapter can learn more complex weight updates. A lower r is more parameter-efficient and acts as stronger regularization. For small fine-tuning datasets (50–500 examples), r=4 to r=16 is typical. For larger datasets, r=32 to r=64 may be appropriate. Setting r too high on a small dataset risks overfitting."}]}
```

---

## Common Mistakes

**Wrong chat template format**: Different models use different special tokens. TinyLlama uses `<|system|>`, `<|user|>`, `<|assistant|>` with `</s>` endings. Check the model's tokenizer config if generation looks wrong.

**Not calling `prepare_model_for_kbit_training()`**: Skipping this on a quantized model will cause gradient computation errors. Always call it before `get_peft_model()`.

**Training on CPU**: Will take hours for even 50 examples. Use GPU. Google Colab free tier is sufficient.

**Pushing full model instead of adapter**: `model.save_pretrained()` on a PeftModel saves only the adapter (~10MB). That is correct. Do not call `.merge_and_unload()` before pushing if you want to share just the adapter.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| Starter_Code.md | ← you are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [03 — Multi-Tool Research Agent](../03_Multi_Tool_Research_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Production RAG System](../05_Production_RAG_System/Project_Guide.md)
