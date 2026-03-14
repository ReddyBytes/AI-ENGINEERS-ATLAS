# Diffusion Fundamentals — Interview Q&A

## Beginner Level

**Q1: What is a diffusion model in plain English?**

A: A diffusion model is a type of AI that generates images (or other data) by learning to reverse a process of gradual noise addition. During training, real images are progressively destroyed by adding Gaussian noise until nothing but static remains. The model learns to undo that destruction step by step. At inference time, you start from pure random noise and run the reverse process to produce a new, coherent image.

---

**Q2: Why is it called "diffusion"?**

A: The name comes from the physics concept of diffusion — where a concentrated substance (like ink dropped in water) spreads out into a uniform distribution over time. Adding noise to an image follows the same mathematical pattern: structure gradually "diffuses" into randomness. The model then learns to run the movie in reverse.

---

**Q3: What is the training loss for a diffusion model?**

A: The model is trained to predict the noise that was added to an image at a given timestep. The loss is simple mean squared error between the actual added noise (ε) and the model's predicted noise (ε_θ):

```
L = E[ || ε - ε_θ(xₜ, t) ||² ]
```

This is much simpler than GAN training (which requires a separate discriminator and a delicate balance between generator and discriminator).

---

**Q4: What does T=1000 mean in DDPM?**

A: T=1000 means the forward process runs for 1000 timesteps — 1000 small noise additions to get from a clean image to pure Gaussian noise. During training, the model sees examples at all 1000 noise levels. During inference, you traditionally reverse all 1000 steps, though fast samplers like DDIM can reduce this to 20-50 steps with similar quality.

---

**Q5: What is a noise schedule?**

A: A noise schedule is the sequence of β values (βₜ for t=1..T) that controls how much noise is added at each step. The linear schedule increases β linearly from ~0.0001 to ~0.02. The cosine schedule uses a cosine curve for the cumulative signal, preserving more image structure in early timesteps, which leads to better training signal and higher output quality.

---

## Intermediate Level

**Q6: Explain the closed-form forward process. Why is it useful?**

A: The closed-form formula lets you jump directly from a clean image x₀ to a noisy image at any timestep t in a single operation, without simulating each of the t intermediate steps:

```
xₜ = √(ᾱₜ) · x₀ + √(1 - ᾱₜ) · ε
```

Where ᾱₜ is the cumulative product of (1-βᵢ) for i=1..t. This is possible because each forward step is a Gaussian operation, and a product of Gaussians is still Gaussian. The practical benefit: during training, for each image you can sample a random timestep t, instantly compute the noisy version xₜ, and train the model to denoise it — no need to simulate the full forward chain.

---

**Q7: What is the difference between the linear and cosine noise schedules?**

A: With the linear schedule, β values increase linearly from 0.0001 to 0.02. This causes the signal to degrade quickly at early timesteps — a significant portion of the image content is destroyed very early, leaving the model little useful gradient signal for low-noise predictions. The cosine schedule (introduced in Improved DDPM) ensures ᾱₜ follows a cosine curve, degrading signal more gradually. The result is better training signal at all noise levels and meaningfully higher output quality. Nearly all modern diffusion models use the cosine schedule or a variant.

---

**Q8: Why are diffusion models better than GANs for image quality?**

A: Several reasons:
1. **Training stability**: DDPM uses a simple MSE loss. GANs require simultaneously training a generator and discriminator in a minimax game, which is notoriously unstable and sensitive to hyperparameters.
2. **Mode coverage**: GANs are prone to mode collapse — ignoring large portions of the data distribution. Diffusion models don't have this problem because the training signal comes from reconstructing actual data at every noise level.
3. **Diversity**: Diffusion models can generate a much wider variety of outputs for the same prompt.
4. **Composability**: Diffusion naturally supports classifier-free guidance and ControlNet-style conditioning, giving fine-grained control that GANs struggle to match.
The main downside is inference speed — diffusion requires many steps (though DDIM, DDPM, and DPM++ have dramatically reduced this).

---

**Q9: What is the relationship between diffusion models and score matching?**

A: Score matching is a technique for training models to estimate the score function: ∇ log p(x), the gradient of the log probability of data. It can be shown mathematically that the optimal noise-predicting model ε_θ is proportional to the negative score function. DDPM and score-based diffusion models are two different framings of the same underlying idea. The score matching perspective (popularized by Yang Song et al.) treats the noise levels as a continuous-time SDE (stochastic differential equation), which enables more flexible samplers.

---

## Advanced Level

**Q10: How does the DDPM training objective relate to the variational lower bound (ELBO)?**

A: DDPM is originally derived as a variational autoencoder where the encoder is fixed (the forward noising process) and the decoder is the learned reverse process. The full ELBO contains terms for each timestep, but Ho et al. showed that a simplified objective — just predicting the noise at a single randomly sampled timestep — works better in practice. The simplification drops weighting terms from the full ELBO and results in a clean MSE loss that trains more stably.

---

**Q11: What is the difference between DDPM and DDIM sampling?**

A: DDPM (Denoising Diffusion Probabilistic Models) is a stochastic sampler — it adds a small amount of random noise at each reverse step (σₜ > 0). This requires many steps (~1000) to produce high-quality images. DDIM (Denoising Diffusion Implicit Models) reformulates the reverse process to be deterministic by removing the stochastic noise term (σₜ = 0). Because it's deterministic, DDIM can use "implicit" large time jumps between steps — you can skip from t=800 directly to t=600, which would not work for DDPM. This allows DDIM to produce comparable quality in 20-50 steps. DDIM also enables deterministic image editing (e.g., DDIM inversion for img2img workflows).

---

**Q12: How would you explain the diffusion process using the stochastic differential equation (SDE) framework?**

A: Yang Song et al. (2021) showed that the forward and reverse diffusion processes can both be described as continuous-time SDEs. The forward SDE adds noise infinitesimally: dx = f(x,t)dt + g(t)dw, where dw is Brownian motion. The reverse SDE runs time backward: dx = [f(x,t) - g(t)² ∇log p(x,t)]dt + g(t)dw_bar. The term ∇log p(x,t) is the score function, which is approximated by the neural network. This formulation unifies DDPM, score matching, and flow matching under one framework and enables more flexible and efficient samplers (e.g., DPM-Solver++).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference card |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | Pure intuition, no math |

⬅️ **Prev:** [Section 16 README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md)
