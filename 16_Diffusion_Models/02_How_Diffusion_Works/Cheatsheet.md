# How Diffusion Works — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Forward process** | Fixed Markov chain: adds Gaussian noise at each of T steps |
| **Reverse process** | Learned Markov chain: removes noise step by step to generate images |
| **DDPM** | Stochastic reverse sampler; ~1000 steps; original algorithm |
| **DDIM** | Deterministic reverse sampler; 20-50 steps; same model, faster |
| **U-Net** | The neural network architecture used as the denoiser |
| **Timestep embedding** | Sinusoidal encoding of t fed into the U-Net so it knows noise level |
| **ε-prediction** | Model predicts the noise that was added; most common parameterization |
| **x₀-prediction** | Model predicts the clean image directly; used in some modern models |
| **v-prediction** | Predicts a linear combination of ε and x₀; used in SD v2+ |
| **DPM-Solver++** | ODE-based sampler; 5-10 steps; current state-of-the-art for speed |

---

## Core Formulas

**Closed-form noise addition (jump to any t):**
```
xₜ = √(ᾱₜ) · x₀  +  √(1 - ᾱₜ) · ε,    ε ~ N(0, I)
```

**Training loss:**
```
L = E_t,x₀,ε [ || ε - ε_θ(√(ᾱₜ)·x₀ + √(1-ᾱₜ)·ε, t) ||² ]
```

**DDPM reverse step:**
```
xₜ₋₁ = (1/√αₜ)(xₜ - βₜ/√(1-ᾱₜ) · ε_θ(xₜ,t))  +  σₜ·z
```

**DDIM reverse step (deterministic):**
```
xₜ₋₁ = √(ᾱₜ₋₁) · (xₜ - √(1-ᾱₜ)·ε_θ(xₜ,t))/√(ᾱₜ) + √(1-ᾱₜ₋₁) · ε_θ(xₜ,t)
```

---

## DDPM vs DDIM at a Glance

| Property | DDPM | DDIM |
|----------|------|------|
| Steps needed | ~1000 | 20-50 |
| Deterministic? | No (stochastic) | Yes |
| Image editing? | Difficult | Yes (via inversion) |
| Same model? | Yes | Yes |
| Quality at 50 steps | Poor | Good |
| Speed | Slow | Fast |

---

## Sampler Speed Guide

| Sampler | Typical Steps | Notes |
|---------|--------------|-------|
| DDPM | 1000 | Original; slow; rarely used in practice |
| DDIM | 50 | Fast; deterministic; great for editing |
| DPM++ 2M | 20-30 | Best speed/quality tradeoff; widely used |
| DPM++ SDE | 20-30 | Stochastic variant; slightly more diversity |
| Euler a | 20-30 | Simple; fast; good default |
| UniPC | 10-20 | State-of-the-art few-step sampling |

---

## U-Net Input/Output

```
Inputs:  xₜ (noisy image tensor)  +  t (timestep embedding)  [+ optional text]
Output:  ε_pred (predicted noise, same shape as xₜ)
```

---

## Training Loop Pseudocode

```python
for step in range(num_training_steps):
    x0 = sample_batch(dataset)           # Real images
    t = torch.randint(1, T, (batch,))    # Random timestep
    eps = torch.randn_like(x0)           # Random noise

    alpha_bar = get_alpha_bar(t)         # Precomputed from schedule
    xt = sqrt(alpha_bar)*x0 + sqrt(1-alpha_bar)*eps  # Add noise

    eps_pred = unet(xt, t)               # Predict noise
    loss = F.mse_loss(eps_pred, eps)     # Simple MSE

    loss.backward()
    optimizer.step()
```

---

## Golden Rules

1. **Same model, different samplers** — DDIM vs DDPM vs DPM++ are just different ways to run the reverse process on the same trained model.
2. **The model never sees clean images at inference** — it starts from pure noise and iteratively denoises.
3. **The timestep embedding is critical** — without it, the model can't tell if it's doing heavy or light denoising.
4. **ε-prediction is the most common** — predict noise, not the clean image directly.
5. **30 DDIM steps ≈ 1000 DDPM steps** in quality for most prompts.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Simplified math walkthrough |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | U-Net deep dive |

⬅️ **Prev:** [Diffusion Fundamentals](../01_Diffusion_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md)
