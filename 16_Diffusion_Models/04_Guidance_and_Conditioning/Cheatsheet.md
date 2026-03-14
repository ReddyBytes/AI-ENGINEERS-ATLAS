# Guidance and Conditioning — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **CFG** | Classifier-Free Guidance — technique to steer diffusion toward a text prompt |
| **Guidance scale (w)** | How strongly to follow the text prompt; typical range 1–15 |
| **Unconditioned prediction** | U-Net output with no prompt (or negative prompt as baseline) |
| **Conditioned prediction** | U-Net output with the positive text prompt |
| **Negative prompt** | Text describing what to avoid; replaces empty string in unconditioned run |
| **Cross-attention** | Mechanism letting image features attend to text token embeddings |
| **ControlNet** | Adds structural conditioning (depth, pose, edges) via a parallel U-Net encoder |
| **IP-Adapter** | Adds image conditioning via cross-attention with image features |
| **CFG Distillation** | Bakes CFG into model weights so only one forward pass is needed (FLUX, Turbo) |

---

## CFG Formula

```
ε_guided = ε_uncond + w × (ε_text − ε_uncond)
```

- w=1: uses ε_text directly (same as conditioned output)
- w>1: extrapolates beyond ε_text in the direction of the text
- Negative prompt replaces empty string for ε_uncond

---

## CFG Scale Guide

| Scale | Use When | Effect |
|-------|----------|--------|
| 1.0–3.0 | Creative / abstract generation | Loosely follows prompt; model's own style |
| 5.0–7.0 | Balanced | Good quality, moderate prompt adherence |
| 7.5 | **Default (SD 1.5)** | Standard sweet spot |
| 8.0–12.0 | Strict prompt following | High adherence; may lose some naturalness |
| 15+ | Usually avoid | Over-saturation, distortion artifacts |

---

## Negative Prompt Tips

### Universal Negative Prompt (SD 1.5)
```
blurry, low quality, low resolution, pixelated, jpeg artifacts,
watermark, text, signature, ugly, deformed, bad anatomy,
extra limbs, missing limbs, mutated hands, bad proportions
```

### For Portraits
```
bad face, asymmetrical eyes, crossed eyes, disfigured, blurry face,
ugly, bad skin, extra fingers, fewer fingers
```

### For Landscapes/Scenes
```
flat lighting, oversaturated, grainy, noisy, low quality, overexposed
```

### For Photorealism
```
painting, drawing, illustration, cartoon, anime, rendered, digital art
```

---

## Quick Decision Guide

```
Prompt not being followed closely?
├── Increase CFG scale (try 8.5-10)
├── Put key concepts earlier in the prompt
└── Use a more specific prompt

Image quality issues?
├── Decrease CFG scale (try 6-7)
├── Add negative prompts for the specific artifact
└── Try fewer inference steps (may help with over-rendering)

Image too generic / boring?
└── Decrease CFG scale (try 4-6); model has more creative freedom

Need structural control (pose, depth)?
└── Use ControlNet (see folder 06)
```

---

## Conditioning Types at a Glance

| Type | How | Effect |
|------|-----|--------|
| Text (positive) | Cross-attention + CFG | Generates toward the prompt |
| Text (negative) | CFG unconditioned baseline | Pushes away from concepts |
| Image (img2img) | VAE encode → noisy start | Keeps composition of source |
| Reference image (IP-Adapter) | Cross-attention | Applies style/content from reference |
| Depth map (ControlNet) | Parallel U-Net encoder | Enforces 3D depth structure |
| Pose skeleton (ControlNet) | Parallel U-Net encoder | Enforces body pose |
| Edges (ControlNet) | Parallel U-Net encoder | Enforces shape/composition |

---

## Golden Rules

1. **w=7-8 is the sweet spot** for most models — use as your default.
2. **Negative prompts ≠ instructions** — they are push-away signals, not commands.
3. **CFG costs 2× compute** — every step runs two U-Net passes.
4. **More specific prompts beat higher CFG** — describe what you want precisely rather than cranking up guidance.
5. **FLUX / Turbo use 1 forward pass** — CFG distillation eliminates the second pass at the cost of less flexibility.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | CFG scale comparison code |

⬅️ **Prev:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Modern Diffusion Models](../05_Modern_Diffusion_Models/Theory.md)
