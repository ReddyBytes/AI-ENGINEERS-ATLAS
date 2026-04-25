# Project 09 — Custom LoRA Fine-Tuning: Recap

## What You Built

A complete **LoRA fine-tuning pipeline** for `TinyLlama-1.1B-Chat`. You created a JSONL dataset of instruction-following Q&A pairs, loaded the model in 4-bit quantization with `bitsandbytes`, applied LoRA adapters (~5M trainable parameters out of 1.1B) using the `peft` library, and trained with `SFTTrainer` from `trl`. You evaluated the before/after difference on held-out questions, pushed only the adapter weights (~10–20 MB) to Hugging Face Hub, and deployed an interactive Gradio demo to Spaces.

---

## Concepts Applied

| Concept | Where it appeared |
|---|---|
| LoRA mechanics | Two small matrices A (d×r) and B (r×k) added in parallel to frozen weights |
| Rank decomposition | Weight updates are approximated as low-rank; r controls capacity vs. parameter count |
| Hyperparameter tuning | `r`, `lora_alpha`, `target_modules`, `lora_dropout`, `learning_rate`, `num_epochs` |
| 4-bit quantization | `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")` — ~700MB vs ~2GB |
| Dataset formatting | JSONL with `messages` list; `system/user/assistant` roles for instruction following |
| SFTTrainer | Handles chat template application, gradient accumulation, eval loop, checkpointing |
| Overfitting detection | `train_loss` decreasing while `eval_loss` increases = overfit signal |
| Adapter publishing | `model.save_pretrained()` on PeftModel saves only adapter weights — not the full model |
| Qualitative evaluation | Systematic before/after comparison on held-out questions you know the answer to |
| Gradio + Spaces | `gr.Interface` wrapping a generate function; deployed as a public HF Space |

---

## Extension Ideas

1. **Hyperparameter sweep**: Train the same dataset with `r = 4, 8, 16, 32`. Plot `eval_loss` vs `r` and compare response quality on 5 test questions. Find the minimum `r` that gives acceptable quality — this is the efficiency frontier for your dataset.

2. **Merge and benchmark inference speed**: After training, create two versions — a PeftModel (adapter-based) and a merged model (using `model.merge_and_unload()`). Measure tokens/second for each. The merged model has no extra computation at inference time; the adapter model has a small overhead that is usually negligible.

3. **DPO fine-tuning on top of SFT**: After supervised fine-tuning, collect preference data: for each question, write one good answer and one worse answer. Use `DPOTrainer` from `trl` to further align the model with human preferences. Compare SFT-only vs SFT+DPO responses on your test questions.

---

## Job Role Mapping

| Role | How this project is relevant |
|---|---|
| ML Engineer | LoRA is the standard technique for model customization at every company using LLMs |
| AI Engineer | Understanding when fine-tuning beats RAG or prompt engineering is a core engineering decision |
| Research Engineer | You can now implement and ablate fine-tuning experiments on small models locally |
| MLOps Engineer | The full pipeline (train → eval → push to Hub → deploy) is the standard ML production workflow |
| Data Scientist | Dataset quality is the binding constraint — you experienced this firsthand |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
