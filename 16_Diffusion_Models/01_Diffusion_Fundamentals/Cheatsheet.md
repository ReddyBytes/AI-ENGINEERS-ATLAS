# Diffusion Fundamentals — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Forward process** | Adding Gaussian noise to an image step by step until it becomes pure noise |
| **Reverse process** | Using a trained model to remove noise step by step, recovering a clean image |
| **DDPM** | Denoising Diffusion Probabilistic Models — the foundational 2020 paper |
| **Timestep t** | Which "noise level" we're at; t=0 is clean, t=T is pure noise |
| **Noise schedule** | The sequence of βₜ values controlling how fast noise is added |
| **Linear schedule** | βₜ increases linearly — simple but over-noises early steps |
| **Cosine schedule** | ᾱₜ follows a cosine curve — better signal preservation, preferred |
| **ᾱₜ (alpha-bar)** | Cumulative product of (1-β) values; tells you how much signal remains at step t |
| **ε (epsilon)** | The noise that was added; what the model is trained to predict |
| **Denoiser** | The neural network (usually a U-Net) that predicts noise given a noisy image + timestep |
| **Score function** | ∇ log p(x) — mathematically equivalent to noise prediction |

---

## Core Formulas

**Jump directly to any noise level (closed form):**
```
xₜ = √(ᾱₜ) · x₀ + √(1 - ᾱₜ) · ε,    ε ~ N(0, I)
```

**Training loss (noise prediction MSE):**
```
L = E[ || ε - ε_θ(xₜ, t) ||² ]
```

**One reverse step:**
```
xₜ₋₁ = (1/√αₜ) · (xₜ - (βₜ/√(1-ᾱₜ)) · ε_θ(xₜ, t)) + σₜ · z
```
Where z ~ N(0,I) and σₜ adds stochastic noise (for DDPM; DDIM sets σₜ=0).

---

## Noise Schedule Quick Reference

| Property | Linear | Cosine |
|----------|--------|--------|
| Signal at t=200 | ~60% remains | ~85% remains |
| Signal at t=500 | ~20% remains | ~60% remains |
| Image quality | Good | Better |
| Paper | DDPM (2020) | Improved DDPM (2021) |
| Use today? | Rarely | Yes — default in most frameworks |

---

## When to Use Diffusion vs Other Generators

| ✅ Use diffusion when | ❌ Avoid / prefer alternatives when |
|----------------------|-------------------------------------|
| You need high quality, diverse images | You need real-time generation (use GAN/flow) |
| You want text-conditioned generation | Ultra-low latency is critical |
| Training stability matters | You have very limited compute |
| You need controllable outputs (depth, pose) | Simple low-res thumbnails suffice |

---

## Quick Decision Guide

```
Need to generate images?
├── Quality is paramount → Diffusion (SD, SDXL, FLUX)
├── Need it in <50ms → GAN or flow-matching
├── Need text control → Stable Diffusion + CFG
└── Need structural control (pose, depth) → ControlNet (see folder 06)
```

---

## Golden Rules

1. **T=1000 is a training detail** — inference can often use 20-50 steps with DDIM.
2. **Cosine schedule > linear schedule** for image quality.
3. **The loss is just MSE on noise** — simpler than it looks.
4. **Adding more denoising steps at inference** improves quality up to ~50 steps; beyond that, diminishing returns.
5. **The model predicts noise, not the clean image** — though "predict x₀" variants also exist.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep Q&A |
| [📄 Intuition_First.md](./Intuition_First.md) | Pure intuition, no math |

⬅️ **Prev:** [Section 16 README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md)
