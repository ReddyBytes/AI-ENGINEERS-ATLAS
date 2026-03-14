# Diffusion vs GANs — Cheatsheet

## At a Glance

| | GANs | Diffusion | VAEs |
|--|-----|-----------|------|
| Training | Adversarial (unstable) | MSE denoising (stable) | ELBO (stable) |
| Inference | Single forward pass | 20-1000 steps | Single forward pass |
| Speed | Very fast | Slow (DDPM) → fast (DDIM/DPM++) | Very fast |
| Image quality | Sharp but limited diversity | Excellent quality + diversity | Blurry/soft |
| Mode collapse risk | High | None | Low |
| Text conditioning | Hard | Natural (cross-attention) | Possible but limited |
| Fine-grained control | Limited | Excellent (ControlNet, LoRA, CFG) | Limited |
| Inference VRAM | Low | Medium-High | Low |
| Training stability | Poor | Good | Good |

---

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **GAN** | Generative Adversarial Network — generator vs discriminator adversarial game |
| **Generator** | In a GAN: the network that creates fake images from noise |
| **Discriminator** | In a GAN: the network that classifies real vs fake |
| **Mode collapse** | GAN failure: generator only produces a narrow subset of possible outputs |
| **Vanishing gradient** | GAN failure: perfect discriminator → near-zero gradient for generator |
| **Training instability** | GAN training oscillates / diverges without careful tuning |
| **ELBO** | Evidence Lower BOund — the training objective for VAEs |
| **KL divergence** | In VAE: regularization that keeps latent space organized |
| **Reconstruction loss** | In VAE: penalty for failing to reconstruct input images |
| **Blurry outputs** | Characteristic VAE failure: averaging over possible reconstructions |

---

## GAN Failure Modes

| Failure Mode | What Happens | Cause |
|-------------|--------------|-------|
| Mode collapse | Generator produces only one/few outputs | Nash equilibrium degeneracy |
| Training divergence | Loss explodes; model produces noise | Discriminator too strong |
| Vanishing gradient | Generator stops learning | Discriminator too good early |
| Checkerboard artifacts | Grid-like patterns in output | Transposed convolution stride |
| Over-sharpening | Unnaturally crisp textures | Adversarial over-optimization |

---

## Inference Speed Comparison

| Model | Steps | Time (A100) | Time (RTX 3090) |
|-------|-------|-------------|-----------------|
| GAN (StyleGAN3) | 1 | <100ms | <200ms |
| VAE decoder | 1 | <50ms | <100ms |
| Diffusion DDPM | 1000 | ~90s | ~200s |
| Diffusion DDIM | 50 | ~5s | ~10s |
| Diffusion DPM++ | 20 | ~2s | ~4s |
| Diffusion (distilled) | 1-4 | <1s | ~2s |

---

## When to Use Each

| ✅ Use GANs when | ✅ Use Diffusion when | ✅ Use VAEs when |
|----------------|---------------------|----------------|
| Real-time inference needed | Quality is paramount | Latent encoding needed |
| < 100ms generation required | Diversity matters | Fast compression needed |
| Super-resolution | Text conditioning | Downstream feature use |
| Domain transfer | Structural control (ControlNet) | Anomaly detection |
| Video frame generation | Fine-tuning (LoRA) | Quick baseline generation |
| Face swapping/avatars | Long-form content (video/3D) | Interpolation in latent space |

---

## Architecture Summary

```
GAN:
  Random noise z → Generator → Image x̂
  Real image x → Discriminator → P(real)
  Fake image x̂ → Discriminator → P(real)
  Train: G maximize D(G(z)); D minimize mistakes

Diffusion:
  Real image → +noise → noisy image at t → U-Net → predicted noise
  Train: minimize MSE(actual noise, predicted noise)
  Generate: start from noise, iteratively subtract predicted noise

VAE:
  Real image → Encoder → μ, σ → sample z → Decoder → reconstructed image
  Train: maximize ELBO = -reconstruction loss + -KL(q(z|x) || p(z))
  Generate: sample z ~ N(0,I) → Decoder → image
```

---

## Notable Models in Each Family

| GANs | Diffusion | VAEs |
|------|-----------|------|
| StyleGAN2/3 (faces) | DDPM (original) | VQ-VAE |
| BigGAN (ImageNet) | Stable Diffusion | VQ-VAE-2 |
| CycleGAN (domain transfer) | DALL-E 2/3 | DALL-E (first, 2021) |
| ESRGAN (super-res) | SDXL | SD VAE (latent encoder) |
| Pix2Pix (img2img) | FLUX | Stable Cascade (VQGAN) |
| GauGAN (segmentation) | Imagen | LDM (latent precursor) |

---

## Golden Rules

1. **Quality generation at any latency budget → Diffusion** (use distilled models for speed).
2. **Real-time, single-step generation → GAN** (StyleGAN3 is still state-of-the-art for faces).
3. **Need latent encoding for downstream tasks → VAE**.
4. **All modern text-to-image uses diffusion** — GANs never scaled to text conditioning reliably.
5. **VAE inside SD is the reason SD is fast** — the latent space is a VAE latent, not pixel space.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Full comparison table |

⬅️ **Prev:** [ControlNet and Adapters](../06_ControlNet_and_Adapters/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 16 README](../Readme.md)
