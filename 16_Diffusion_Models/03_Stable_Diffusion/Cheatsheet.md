# Stable Diffusion — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Latent Diffusion** | Diffusion in compressed VAE latent space, not pixel space |
| **VAE** | Variational Autoencoder; encodes pixels to 64×64×4 latents and back |
| **CLIP** | Text encoder; converts prompt tokens to context vectors for cross-attention |
| **Cross-attention** | Mechanism in U-Net that lets image features attend to text tokens |
| **Guidance scale (CFG)** | How strongly the model follows the text prompt; default ~7.5 |
| **Negative prompt** | Text describing what to avoid; used in CFG computation |
| **Inference steps** | Number of denoising steps at generation time; typically 20-50 |
| **Latent scale factor** | 0.18215 — SD's constant to normalize VAE latent distribution |
| **img2img** | Encode a real image to latents, add noise, then denoise with new prompt |
| **Inpainting** | Mask part of an image; diffusion fills in the masked region |
| **LoRA** | Low-Rank Adaptation; efficient fine-tuning to add new styles/subjects |

---

## Model Variants Comparison

| Model | Resolution | Text Encoder | U-Net Size | VRAM (fp16) |
|-------|-----------|--------------|-----------|-------------|
| SD 1.5 | 512×512 | CLIP ViT-L (768d) | 860M | ~4GB |
| SD 2.1 | 768×768 | OpenCLIP ViT-H (1024d) | 865M | ~5GB |
| SDXL base | 1024×1024 | CLIP-L + OpenCLIP-G | 2.6B | ~8GB |
| SDXL refiner | 1024×1024 | CLIP-L + OpenCLIP-G | 2.6B | ~8GB (add-on) |

---

## Full Pipeline at a Glance

```
Text prompt
    ↓ CLIP tokenizer + encoder
Text context vectors (77, 768)
    ↓ Used in U-Net cross-attention
Random noise (64×64×4)
    ↓ U-Net denoising × N steps
Clean latent (64×64×4)
    ↓ VAE decoder
Final image (512×512×3)
```

---

## Important Constants (SD 1.5)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Latent channels | 4 | Not RGB — learned channels |
| Latent spatial factor | 8× | 512px → 64 latent |
| VAE scale factor | 0.18215 | Multiply before diffusion |
| CLIP max tokens | 77 | Longer prompts get truncated |
| Text embedding dim | 768 | Per token vector |
| T (noise steps) | 1000 | Training; 20-50 at inference |
| Default guidance scale | 7.5 | Can tune 1–15 |

---

## When to Use Each Model

| ✅ Use SD 1.5 when | ✅ Use SD 2.1 when | ✅ Use SDXL when |
|-------------------|-------------------|-----------------|
| Maximum LoRA/ControlNet compatibility | Better image quality needed | Best quality + 1024px |
| Limited VRAM (<6GB) | Open vocabulary text encoding | Creating detailed scenes |
| Maximum ecosystem support | 768px native resolution | Professional outputs |
| Fast iteration | No legacy LoRAs needed | VRAM > 8GB available |

---

## Quick Decision Guide

```
Generating images with Stable Diffusion?
├── Need max compatibility (ControlNet, LoRA, WebUI) → SD 1.5
├── Better quality, less ecosystem → SD 2.1
├── Best quality, have 8GB+ VRAM → SDXL
├── Need to edit an existing image → img2img (any SD)
├── Need to fill in a region → Inpainting (any SD)
└── Need custom style/subject → Fine-tune with LoRA
```

---

## Golden Rules

1. **The VAE is frozen during diffusion inference** — only the U-Net runs the denoising loop.
2. **Longer prompts don't always help** — CLIP truncates at 77 tokens; prioritize key concepts early.
3. **The negative prompt is as important as the positive** — common additions: "blurry, low quality, distorted, watermark."
4. **CFG scale 7-8 is the sweet spot** — higher is not always better (see folder 04).
5. **img2img denoising strength** controls how much of the original is preserved: 0.0 = no change, 1.0 = fully regenerated.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Generate images with diffusers |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full SD architecture diagram |

⬅️ **Prev:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md)
