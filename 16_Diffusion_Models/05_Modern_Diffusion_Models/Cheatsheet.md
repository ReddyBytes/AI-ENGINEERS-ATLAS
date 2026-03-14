# Modern Diffusion Models — Cheatsheet

## Quick Model Comparison

| Property | SD 1.5 | SD 2.1 | SDXL | FLUX.1-dev | FLUX.1-schnell |
|----------|--------|--------|------|-----------|----------------|
| Native resolution | 512×512 | 768×768 | 1024×1024 | 1024×1024+ | 1024×1024+ |
| Architecture | U-Net | U-Net | U-Net (larger) | DiT (transformer) | DiT (distilled) |
| Text encoder | CLIP ViT-L | OpenCLIP ViT-H | CLIP-L + OpenCLIP-G | CLIP-L + T5-XXL | CLIP-L + T5-XXL |
| Training objective | DDPM/ε-pred | DDPM/v-pred | DDPM/v-pred | Flow matching | Flow matching |
| Parameters (denoiser) | 860M | 865M | 2.6B | 12B | 12B (distilled) |
| VRAM (fp16) | ~4GB | ~5GB | ~8GB | ~24GB (full) | ~24GB (full) |
| VRAM (fp8 quantized) | — | — | — | ~12GB | ~12GB |
| Inference steps | 20-50 | 20-50 | 20-50 | 20-50 | 1-4 |
| LoRA ecosystem | Massive | Small | Large | Growing | Growing |
| ControlNet ecosystem | Massive | Medium | Large | Emerging | Emerging |
| License | CreativeML | CreativeML | CreativeML | Non-commercial (dev) | Apache 2.0 (schnell) |

---

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **DiT** | Diffusion Transformer — replaces U-Net with a transformer architecture |
| **Flow matching** | Training objective using straight-line paths from noise to image; used in FLUX, SD3 |
| **Rectified flow** | Specific flavor of flow matching with linear interpolation between x₀ and noise |
| **MM-DiT** | Multimodal DiT — joint processing of image and text tokens in SD3 |
| **FLUX.1-dev** | High-quality open FLUX model; non-commercial license; 20-50 steps |
| **FLUX.1-schnell** | Fast open FLUX model; Apache 2.0; 1-4 steps; distilled |
| **Guidance distillation** | Baking CFG into model weights to eliminate second forward pass |
| **T5-XXL** | Large language model encoder (4.9B params) used by FLUX for complex text |
| **Base + Refiner** | SDXL two-stage pipeline: base makes structure, refiner adds high-freq detail |

---

## When to Use Each Model

| ✅ Use SD 1.5 when | ✅ Use SDXL when | ✅ Use FLUX.1-dev when |
|-------------------|----------------|----------------------|
| VRAM is limited (<6GB) | Good quality + ecosystem | Best possible quality |
| Max ControlNet compatibility | Native 1024px | Text rendering in images |
| Large LoRA library needed | LoRA + ControlNet | Complex prompt understanding |
| Fast iteration | 8GB+ VRAM available | Long, detailed prompts |
| Legacy workflows | Multi-aspect ratios | 24GB VRAM or quantization |

| ✅ Use FLUX.1-schnell when | ✅ Use SD 2.1 when |
|--------------------------|------------------|
| Maximum speed (1-4 steps) | Higher res than 1.5 needed |
| Commercial/open use (Apache 2.0) | Some LoRA ecosystem |
| Prototyping, rapid iteration | Avoiding proprietary tools |
| Consumer apps | Budget compute |

---

## SDXL Pipeline at a Glance

```
Prompt → CLIP-L + OpenCLIP-G (two encoders)
       → SDXL Base U-Net (1024×1024, 2.6B params)
       → [Optional: SDXL Refiner (high-freq detail, 20% of steps)]
       → VAE Decode
       → 1024×1024 image
```

## FLUX Pipeline at a Glance

```
Prompt → CLIP-L + T5-XXL (two encoders)
       → Patchify latent (image → patch tokens)
       → FLUX DiT (12B params, joint image+text attention)
       → Depatchify
       → VAE Decode
       → High-quality image
```

---

## What Changed Between Generations

| Pain Point | SD 1.5 Problem | SDXL Solution | FLUX Solution |
|-----------|---------------|---------------|---------------|
| Resolution | 512px native, tiling artifacts at higher res | 1024px native training | 1024px+, flexible aspect |
| Text understanding | CLIP 77 token limit, poor syntax | Dual encoders, richer vocab | CLIP + T5-XXL (unlimited length) |
| Text rendering | Poor (can't write words in images) | Better | Much better |
| Anatomy (hands/faces) | Frequent failures | Improved | Strong |
| Complex compositions | Unreliable | Better | Strong |
| Inference speed | 20-50 DDIM steps | 20-50 steps | 1-4 steps (schnell) |

---

## VRAM Requirements (Practical)

| Model | fp16 | bf16 | fp8 quantized | CPU offload |
|-------|------|------|---------------|-------------|
| SD 1.5 | 4GB | 4GB | N/A | 2GB GPU |
| SDXL base | 8GB | 8GB | N/A | 4GB GPU |
| FLUX.1-dev | 24GB | 24GB | ~12GB | ~6-8GB GPU (slow) |
| FLUX.1-schnell | 24GB | 24GB | ~12GB | ~6-8GB GPU (slow) |

---

## Golden Rules

1. **Match your LoRA to your base model** — SD 1.5, SDXL, and FLUX LoRAs are not interchangeable.
2. **FLUX needs 12GB+ VRAM in practice** — use quantization (fp8/nf4) for 12GB, CPU offload for less.
3. **SDXL is the ecosystem winner** — most ControlNets, LoRAs, and UIs support it well.
4. **FLUX.1-schnell is Apache 2.0** — the only production-usable open FLUX model.
5. **Flow matching ≠ DDPM** — use the correct scheduler class (FlowMatchEulerDiscreteScheduler for FLUX).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Detailed model comparison |

⬅️ **Prev:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [ControlNet and Adapters](../06_ControlNet_and_Adapters/Theory.md)
