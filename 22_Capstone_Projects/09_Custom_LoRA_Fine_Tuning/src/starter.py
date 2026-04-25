"""
LoRA Fine-Tuning Script
=======================
Fine-tune TinyLlama on a custom Q&A dataset using LoRA and SFTTrainer.

Usage:
    python starter.py --dataset dataset.jsonl --output ./lora_output

Requirements:
    pip install transformers peft trl datasets accelerate bitsandbytes torch
    GPU strongly recommended (Google Colab T4 is sufficient)

Three scripts in this project:
    starter.py   — this file (training)
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
    # TODO: Check that:
    #   - "messages" key exists and is a list
    #   - list has at least 2 elements (user + assistant minimum)
    #   - each element is a dict with "role" and "content" keys
    #   - "content" is a non-empty string
    #   Return False (not raise) if any check fails.
    pass


def load_dataset_from_jsonl(file_path: str) -> tuple[Dataset, Dataset]:
    """
    Load dataset from JSONL file and split into train/eval.

    Returns:
        (train_dataset, eval_dataset) as HuggingFace Dataset objects.
    """
    # TODO: Read the JSONL file line by line.
    #       Parse each line as JSON (skip blank lines and catch JSONDecodeError).
    #       Validate each example with validate_example() — collect valid ones.
    #       Print: total examples, skipped examples.
    #
    #       Create a HuggingFace Dataset:
    #           dataset = Dataset.from_list(examples)
    #
    #       Split with train_test_split(test_size=EVAL_SPLIT, seed=42).
    #       Return (split["train"], split["test"]).
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

    # TODO: If CUDA is available, create BitsAndBytesConfig:
    #   load_in_4bit=True
    #   bnb_4bit_quant_type="nf4"
    #   bnb_4bit_compute_dtype=torch.float16
    #   bnb_4bit_use_double_quant=True
    #
    # If CUDA is not available, set bnb_config = None.
    bnb_config = None  # ← replace with your BitsAndBytesConfig (or None for CPU)

    # TODO: Load model with AutoModelForCausalLM.from_pretrained():
    #   If bnb_config is not None: pass quantization_config=bnb_config, device_map="auto"
    #   If CPU: just pass model_id, no quantization config
    model = None  # ← replace

    # TODO: Load tokenizer with AutoTokenizer.from_pretrained(model_id).
    #       Set tokenizer.pad_token = tokenizer.eos_token
    #       Set tokenizer.padding_side = "right"
    tokenizer = None  # ← replace

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
    # TODO: Call prepare_model_for_kbit_training(model).
    #       This enables gradient checkpointing and casts layer norms to float32.
    #       Required before get_peft_model() on quantized models.

    # TODO: Create LoraConfig with the constants at the top of this file:
    #   r=LORA_R
    #   lora_alpha=LORA_ALPHA
    #   target_modules=LORA_TARGET_MODULES
    #   lora_dropout=LORA_DROPOUT
    #   bias="none"
    #   task_type=TaskType.CAUSAL_LM
    lora_config = None  # ← replace

    # TODO: Call get_peft_model(model, lora_config) to inject adapter matrices.
    #       The returned model has only adapter params set to requires_grad=True.
    peft_model = None  # ← replace

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
    # TODO: Create TrainingArguments:
    #   output_dir=output_dir
    #   num_train_epochs=NUM_EPOCHS
    #   per_device_train_batch_size=BATCH_SIZE
    #   gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS
    #   learning_rate=LEARNING_RATE
    #   fp16=torch.cuda.is_available()   ← half-precision on GPU only
    #   logging_steps=5
    #   evaluation_strategy="epoch"
    #   save_strategy="epoch"
    #   load_best_model_at_end=True
    #   report_to="none"
    training_args = None  # ← replace

    # TODO: Create and return SFTTrainer:
    #   model=model
    #   train_dataset=train_dataset
    #   eval_dataset=eval_dataset
    #   tokenizer=tokenizer
    #   args=training_args
    #   max_seq_length=MAX_SEQ_LENGTH
    #
    # SFTTrainer applies the chat template automatically when your dataset
    # has a "messages" column — which ours does.
    pass


# ---------------------------------------------------------------------------
# Step 5: Save and push to Hub
# ---------------------------------------------------------------------------

def save_and_push(model, tokenizer, output_dir: str, hub_repo: str = None) -> None:
    """
    Save the LoRA adapter locally and optionally push to Hugging Face Hub.

    Note: model.save_pretrained() on a PeftModel saves ONLY the adapter weights
    (~10–20MB), NOT the full base model. This is the correct behavior.
    """
    # TODO: Call model.save_pretrained(output_dir).
    #       Call tokenizer.save_pretrained(output_dir).
    #       Print a confirmation with the output directory.

    if hub_repo:
        # TODO: Call model.push_to_hub(hub_repo).
        #       Call tokenizer.push_to_hub(hub_repo).
        #       Print: f"Model published: https://huggingface.co/{hub_repo}"
        pass


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

    # TODO: Apply chat template: tokenizer.apply_chat_template(
    #           messages, tokenize=False, add_generation_prompt=True
    #       )
    #       Tokenize the prompt: tokenizer(prompt, return_tensors="pt").to(model.device)
    #       Generate with torch.no_grad():
    #           model.generate(
    #               **inputs,
    #               max_new_tokens=max_new_tokens,
    #               temperature=0.7,
    #               do_sample=True,
    #               pad_token_id=tokenizer.eos_token_id,
    #           )
    #       Decode ONLY the new tokens:
    #           generated = outputs[0][inputs.input_ids.shape[1]:]
    #           return tokenizer.decode(generated, skip_special_tokens=True)
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

    print("\nDone! To evaluate: python evaluate.py")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Sample dataset entries (copy to dataset.jsonl, add 50+ total)
# ---------------------------------------------------------------------------
#
# {"messages": [{"role": "system", "content": "You are an expert AI/ML tutor."}, {"role": "user", "content": "What is LoRA?"}, {"role": "assistant", "content": "LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that freezes pre-trained model weights and adds small trainable rank-decomposition matrices alongside specific layers. Weight updates are represented as the product of two low-rank matrices A (d x r) and B (r x k), where r is much smaller than d and k. This reduces trainable parameters by 90-99% while achieving comparable performance to full fine-tuning."}]}
# {"messages": [{"role": "system", "content": "You are an expert AI/ML tutor."}, {"role": "user", "content": "What does rank r control in LoRA?"}, {"role": "assistant", "content": "The rank r controls the size of the trainable adapter matrices. A higher r means more parameters and more representational capacity — the adapter can learn more complex weight updates. A lower r is more parameter-efficient and acts as stronger regularization. For small datasets (50-500 examples), r=4 to r=16 is typical."}]}
