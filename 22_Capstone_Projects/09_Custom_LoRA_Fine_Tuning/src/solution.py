"""
LoRA Fine-Tuning Script — SOLUTION
====================================
Fine-tune TinyLlama on a custom Q&A dataset using LoRA and SFTTrainer.

Usage:
    python solution.py --dataset dataset.jsonl --output ./lora_output

Requirements:
    pip install transformers peft trl datasets accelerate bitsandbytes torch
    GPU strongly recommended (Google Colab T4 is sufficient)

Three scripts in this project:
    solution.py  — this file (training)
    evaluate.py  — before/after comparison (copy from 03_GUIDE.md)
    app.py       — Gradio demo (copy from 03_GUIDE.md)
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

# LoRA hyperparameters  ← experiment with these
LORA_R = 16                             # rank — higher = more capacity, more overfit risk
LORA_ALPHA = 32                         # scaling factor: effective scale = lora_alpha / r
LORA_DROPOUT = 0.05                     # regularization for small datasets
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]  # attention projections

# Training hyperparameters  ← experiment with these
NUM_EPOCHS = 3
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 4        # effective batch = BATCH_SIZE * GRAD_ACCUM = 8
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 512
EVAL_SPLIT = 0.15                       # fraction of data held out for eval


# ---------------------------------------------------------------------------
# Step 1: Dataset loading and validation
# ---------------------------------------------------------------------------

def validate_example(example: dict) -> bool:
    """
    Return True if the example has the expected structure.

    Required structure:
        {
            "messages": [
                {"role": "system",    "content": "..."},
                {"role": "user",      "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    """
    # Check that "messages" key exists and is a list
    if "messages" not in example or not isinstance(example["messages"], list):
        return False

    # Must have at least a user and an assistant message
    if len(example["messages"]) < 2:
        return False

    # Each message must be a dict with "role" and "content" keys, content non-empty
    for msg in example["messages"]:
        if not isinstance(msg, dict):
            return False
        if "role" not in msg or "content" not in msg:
            return False
        if not isinstance(msg["content"], str) or not msg["content"].strip():
            return False

    return True


def load_dataset_from_jsonl(file_path: str) -> tuple[Dataset, Dataset]:
    """
    Load dataset from JSONL file and split into train/eval.

    Returns:
        (train_dataset, eval_dataset) as HuggingFace Dataset objects.
    """
    examples = []
    skipped = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # ← skip blank lines

            try:
                example = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  Warning: skipping line {line_num} (JSON error): {e}")
                skipped += 1
                continue

            if validate_example(example):
                examples.append(example)
            else:
                print(f"  Warning: skipping line {line_num} (invalid format)")
                skipped += 1

    print(f"Dataset: {len(examples)} valid examples, {skipped} skipped.")

    if not examples:
        raise ValueError(f"No valid examples found in {file_path}. Check dataset format.")

    # Convert to HuggingFace Dataset format
    dataset = Dataset.from_list(examples)  # ← HuggingFace Dataset from list of dicts

    # Split into train and eval sets
    split = dataset.train_test_split(test_size=EVAL_SPLIT, seed=42)  # ← seed=42 for reproducibility
    return split["train"], split["test"]


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

    if torch.cuda.is_available():
        # 4-bit quantization reduces VRAM from ~4GB to ~1.2GB for TinyLlama
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,                          # ← quantize weights to 4-bit
            bnb_4bit_quant_type="nf4",                  # ← NF4 is best for LLMs
            bnb_4bit_compute_dtype=torch.float16,       # ← compute in fp16 for speed
            bnb_4bit_use_double_quant=True,             # ← quantize the quantization constants
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",                          # ← automatically map layers to GPU
        )
    else:
        # CPU fallback — no quantization (much slower, only for testing)
        bnb_config = None
        model = AutoModelForCausalLM.from_pretrained(model_id)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token   # ← required: TinyLlama has no separate pad token
    tokenizer.padding_side = "right"            # ← right-padding is correct for causal LM training

    return model, tokenizer


# ---------------------------------------------------------------------------
# Step 3: Apply LoRA
# ---------------------------------------------------------------------------

def apply_lora(model):
    """
    Prepare model for training and apply LoRA adapters.

    Returns:
        (peft_model, lora_config) tuple.
    """
    # REQUIRED for quantized models: enables gradient checkpointing and
    # casts layer norms from 4-bit to float32 (needed for stable gradients)
    model = prepare_model_for_kbit_training(model)

    # LoRA injects small trainable matrices A (d×r) and B (r×k) into the
    # attention projection layers. Only these matrices are trained.
    lora_config = LoraConfig(
        r=LORA_R,                           # ← rank: dimension of the low-rank matrices
        lora_alpha=LORA_ALPHA,              # ← scaling: output is scaled by lora_alpha / r
        target_modules=LORA_TARGET_MODULES, # ← inject LoRA into all 4 attention projections
        lora_dropout=LORA_DROPOUT,          # ← dropout on LoRA layers for regularization
        bias="none",                        # ← don't train biases (saves params, no quality loss)
        task_type=TaskType.CAUSAL_LM,       # ← causal language modeling (autoregressive generation)
    )

    # Inject the LoRA adapter matrices into the model
    # After this call, only adapter weights have requires_grad=True
    peft_model = get_peft_model(model, lora_config)

    peft_model.print_trainable_parameters()
    # Expected output: trainable params: ~5M || all params: 1.1B || trainable%: 0.46

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
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,  # ← effective batch = 2 * 4 = 8
        learning_rate=LEARNING_RATE,
        fp16=torch.cuda.is_available(),         # ← half-precision on GPU only (unsupported on CPU)
        logging_steps=5,                        # ← log loss every 5 steps
        evaluation_strategy="epoch",            # ← evaluate at end of each epoch
        save_strategy="epoch",                  # ← save checkpoint at end of each epoch
        load_best_model_at_end=True,            # ← restore best checkpoint after training
        report_to="none",                       # ← disable wandb/tensorboard logging
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        args=training_args,
        max_seq_length=MAX_SEQ_LENGTH,
        # SFTTrainer automatically applies the chat template when the dataset
        # has a "messages" column — no manual formatting needed
    )

    return trainer


# ---------------------------------------------------------------------------
# Step 5: Save and push to Hub
# ---------------------------------------------------------------------------

def save_and_push(model, tokenizer, output_dir: str, hub_repo: str = None) -> None:
    """
    Save the LoRA adapter locally and optionally push to Hugging Face Hub.

    Note: model.save_pretrained() on a PeftModel saves ONLY the adapter weights
    (~10–20MB), NOT the full base model. This is the correct behavior.
    """
    # Save adapter weights and tokenizer config locally
    model.save_pretrained(output_dir)       # ← saves only LoRA adapter weights (~10-20MB)
    tokenizer.save_pretrained(output_dir)
    print(f"Adapter saved to: {output_dir}")

    if hub_repo:
        # Push only the adapter to the Hub — base model stays on Hub and is loaded separately
        model.push_to_hub(hub_repo)
        tokenizer.push_to_hub(hub_repo)
        print(f"Model published: https://huggingface.co/{hub_repo}")


# ---------------------------------------------------------------------------
# Inference helper (used by evaluate.py and app.py)
# ---------------------------------------------------------------------------

def generate_response(model, tokenizer, question: str, max_new_tokens: int = 256) -> str:
    """
    Generate a response for a question using the TinyLlama chat template.

    Args:
        model: The loaded model (base or fine-tuned PeftModel).
        tokenizer: The corresponding tokenizer.
        question: The user's question string.

    Returns:
        The model's generated answer as a string.
    """
    messages = [
        {"role": "system", "content": "You are an expert AI tutor."},
        {"role": "user", "content": question},
    ]

    # Apply the model-specific chat template (adds <|system|>, <|user|>, <|assistant|> tokens)
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,                # ← return string, not token IDs
        add_generation_prompt=True,    # ← adds the <|assistant|> token to trigger generation
    )

    # Tokenize and move to same device as model
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generate without gradient computation (inference mode)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,                          # ← slight randomness for natural responses
            do_sample=True,                           # ← enable sampling (required with temperature)
            pad_token_id=tokenizer.eos_token_id,     # ← use EOS as pad token during generation
        )

    # Decode ONLY the newly generated tokens (not the input prompt)
    generated = outputs[0][inputs.input_ids.shape[1]:]  # ← slice off prompt tokens
    return tokenizer.decode(generated, skip_special_tokens=True)


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

    print("\nDone! To evaluate: python evaluate.py")


# ---------------------------------------------------------------------------
# Demo / __main__ block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create a minimal sample dataset.jsonl for learners to inspect
    sample_dataset_path = Path("dataset.jsonl")
    if not sample_dataset_path.exists():
        print("Creating sample dataset.jsonl (add 50+ examples before real training)...\n")
        sample_entries = [
            {
                "messages": [
                    {"role": "system", "content": "You are an expert AI/ML tutor."},
                    {"role": "user", "content": "What is LoRA?"},
                    {"role": "assistant", "content": (
                        "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that "
                        "freezes pre-trained model weights and adds small trainable rank-decomposition "
                        "matrices alongside specific layers. Weight updates are represented as the "
                        "product of two low-rank matrices A (d x r) and B (r x k), where r is much "
                        "smaller than d and k. This reduces trainable parameters by 90-99% while "
                        "achieving comparable performance to full fine-tuning."
                    )},
                ]
            },
            {
                "messages": [
                    {"role": "system", "content": "You are an expert AI/ML tutor."},
                    {"role": "user", "content": "What does rank r control in LoRA?"},
                    {"role": "assistant", "content": (
                        "The rank r controls the size of the trainable adapter matrices. A higher r "
                        "means more parameters and more representational capacity — the adapter can "
                        "learn more complex weight updates. A lower r is more parameter-efficient and "
                        "acts as stronger regularization. For small datasets (50-500 examples), "
                        "r=4 to r=16 is typical."
                    )},
                ]
            },
            {
                "messages": [
                    {"role": "system", "content": "You are an expert AI/ML tutor."},
                    {"role": "user", "content": "Why is prepare_model_for_kbit_training needed?"},
                    {"role": "assistant", "content": (
                        "prepare_model_for_kbit_training is required when fine-tuning a quantized "
                        "model (4-bit or 8-bit). It enables gradient checkpointing to save VRAM, "
                        "and casts layer normalization weights from 4-bit back to float32 — "
                        "layer norms must remain in full precision for stable gradient computation. "
                        "Skipping this call causes gradient errors during training."
                    )},
                ]
            },
        ]
        with open(sample_dataset_path, "w") as f:
            for entry in sample_entries:
                f.write(json.dumps(entry) + "\n")
        print(f"Created {sample_dataset_path} with {len(sample_entries)} sample entries.")
        print("Add 50+ more examples before training for meaningful results.\n")

    # Demonstrate dataset validation
    print("Validating sample dataset...")
    train_ds, eval_ds = load_dataset_from_jsonl(str(sample_dataset_path))
    print(f"Train split: {len(train_ds)}, Eval split: {len(eval_ds)}\n")

    print("Configuration summary:")
    print(f"  Base model:    {BASE_MODEL_ID}")
    print(f"  LoRA rank:     {LORA_R}")
    print(f"  LoRA alpha:    {LORA_ALPHA}")
    print(f"  Target modules: {LORA_TARGET_MODULES}")
    print(f"  Epochs:        {NUM_EPOCHS}")
    print(f"  Learning rate: {LEARNING_RATE}")
    print(f"  CUDA available: {torch.cuda.is_available()}\n")

    print("To run training:")
    print(f"  python solution.py --dataset {sample_dataset_path} --output {OUTPUT_DIR}")
    print("\nNote: Training requires a GPU. Use Google Colab (free T4 GPU) for best results.")
