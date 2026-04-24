# How Diffusion Works — Interview Q&A

## Beginner Level

**Q1: What is the U-Net's role in a diffusion model?**

<details>
<summary>💡 Show Answer</summary>

A: The U-Net is the neural network that acts as the denoiser. At each reverse step, it receives the current noisy image xₜ and the timestep t, and outputs a prediction of the noise that was added. The noisy image minus the predicted noise gives a slightly cleaner image xₜ₋₁. The U-Net is chosen because it can see both the fine pixel-level details (through its high-resolution paths) and the broad compositional structure (through its bottleneck) simultaneously — both are needed to make good denoising predictions.

</details>

---

<br>

**Q2: Why does the model need to know the timestep t?**

<details>
<summary>💡 Show Answer</summary>

A: Because "remove heavy noise from this near-static image" and "refine the fine details of this nearly-clean image" are fundamentally different tasks. Without knowing t, the model would be confused — it would see a noisy image and have no idea whether to make large structural changes or small textural refinements. The timestep t is fed into the U-Net as a sinusoidal embedding (similar to positional encodings in transformers), allowing the model to adapt its behavior to the current noise level.

</details>

---

<br>

**Q3: What is the training loop for a DDPM?**

<details>
<summary>💡 Show Answer</summary>

A: The training loop has four steps per batch:
1. Sample a batch of real images x₀ from training data
2. Sample random timesteps t uniformly from 1..T
3. Sample noise ε ~ N(0, I) of the same shape as the images
4. Compute noisy images xₜ using the closed-form formula: xₜ = √(ᾱₜ)·x₀ + √(1-ᾱₜ)·ε
5. Feed xₜ and t into the U-Net to get predicted noise ε_pred
6. Compute loss = MSE(ε, ε_pred), backpropagate, update weights

The model sees every noise level during training, which means every call to the forward process produces a unique training example.

</details>

---

<br>

**Q4: What is the difference between DDPM and DDIM sampling?**

<details>
<summary>💡 Show Answer</summary>

A: Both use the same trained model but different reverse process algorithms:
- **DDPM** is stochastic: it adds a small amount of fresh random noise at each step, which requires ~1000 steps for quality but produces diverse outputs.
- **DDIM** is deterministic: it removes the stochastic term, allowing large jumps between timesteps. DDIM can produce comparable quality in 20-50 steps. It also enables DDIM inversion, which is essential for image editing workflows.

</details>

---

## Intermediate Level

**Q5: Explain skip connections in the U-Net and why they matter for denoising.**

<details>
<summary>💡 Show Answer</summary>

A: A U-Net has an encoder (downsampling path) and a decoder (upsampling path). Skip connections directly link each encoder layer to the corresponding decoder layer at the same resolution. This matters for denoising because:
- The encoder compresses the image, losing spatial resolution but gaining semantic understanding
- The decoder needs to reconstruct fine-grained spatial details (e.g., exact texture, edges)
- Skip connections allow the decoder to access the high-resolution feature maps from the encoder directly, without having to reconstruct them through the bottleneck

Without skip connections, the U-Net would produce blurry outputs because fine spatial details would be lost in the bottleneck.

</details>

---

<br>

**Q6: What is x₀-prediction and when is it used?**

<details>
<summary>💡 Show Answer</summary>

A: Instead of predicting the noise ε, the model can be parameterized to predict the clean image x₀ directly. Given xₜ, the model outputs x̂₀. The two are mathematically equivalent (knowing ε is the same as knowing x₀ given xₜ and ᾱₜ), so you can convert between them. x₀-prediction can produce sharper intermediate images during sampling and is used in some distillation methods. DDIM uses x₀-prediction internally even if the model was trained with ε-prediction, by computing x̂₀ = (xₜ - √(1-ᾱₜ)·ε_θ) / √(ᾱₜ).

</details>

---

<br>

**Q7: What is v-prediction? Why was it introduced?**

<details>
<summary>💡 Show Answer</summary>

A: v-prediction was introduced in "Progressive Distillation for Fast Sampling of Diffusion Models" (Salimans & Ho, 2022). The "v" target is defined as:

```
v = √(ᾱₜ) · ε - √(1-ᾱₜ) · x₀
```

This is a velocity-like quantity in the interpolation between x₀ and ε. v-prediction has better numerical properties at t near 0 (where ε-prediction can have high variance) and at t near T (where x₀-prediction can be unstable). Stable Diffusion v2 uses v-prediction, as does the SDXL refinement model.

</details>

---

<br>

**Q8: How does DPM-Solver++ improve on DDIM?**

<details>
<summary>💡 Show Answer</summary>

A: DDIM uses a first-order ODE solver (Euler method) to traverse the reverse SDE. DPM-Solver++ uses a higher-order ODE solver (similar to Runge-Kutta methods). Higher-order solvers need fewer steps to achieve the same accuracy because they better approximate the trajectory of the reverse process. DPM-Solver++ (2022) achieves near-optimal quality in 10-20 steps, compared to DDIM's 30-50, while remaining fast to compute. It's now the default sampler in many interfaces because it gives the best speed/quality tradeoff.

</details>

---

## Advanced Level

**Q9: What does it mean that the reverse process is a "learned Markov chain"?**

<details>
<summary>💡 Show Answer</summary>

A: A Markov chain is a sequence of states where each state depends only on the immediately preceding state. The reverse diffusion process is a Markov chain over the sequence x_T, x_{T-1}, ..., x₀, where:

```
p_θ(xₜ₋₁ | xₜ) = N(xₜ₋₁; μ_θ(xₜ, t), Σ_θ(xₜ, t))
```

"Learned" because μ_θ and Σ_θ are parameterized by the neural network. The key insight from DDPM is that the optimal form of this distribution is Gaussian (which it is, for sufficiently small β values), and the only thing the neural network needs to learn is the mean — specifically, by predicting the noise. This reduces learning a complex generative process to learning a simple regression.

</details>

---

<br>

**Q10: Explain DDIM inversion and how it enables image editing.**

<details>
<summary>💡 Show Answer</summary>

A: DDIM is deterministic, meaning the same noise x_T always produces the same image x₀. Inversion asks: given a real image x₀, what x_T would the DDIM process have used to produce it? By running the DDIM update in reverse (forward through time from t=0 to t=T), you can approximately infer the starting noise. This inferred x_T, when decoded with a different text prompt, produces an edited version of the original image that shares the same structural composition. This is the foundation of techniques like Prompt-to-Prompt (editing by changing cross-attention), Null-text Inversion, and Dreambooth fine-tuning.

</details>

---

<br>

**Q11: Describe the connection between diffusion models and the score function.**

<details>
<summary>💡 Show Answer</summary>

A: The score function is ∇_x log p_t(x) — the gradient of the log probability density with respect to the data x at noise level t. Score matching (Hyvärinen, 2005) is a method for estimating this gradient. Yang Song (2019) showed that you can estimate the score using a deep network trained with denoising score matching. The connection to DDPM: the optimal noise-predicting network satisfies:

```
ε_θ*(xₜ, t) = -√(1 - ᾱₜ) · ∇_xₜ log p(xₜ)
```

The noise prediction is proportional to the negative score. This means DDPM and score-based models are the same algorithm viewed from different mathematical frameworks. The score perspective enables continuous-time formulations (SDEs) and more flexible samplers.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Simplified math walkthrough |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | U-Net deep dive |

⬅️ **Prev:** [Diffusion Fundamentals](../01_Diffusion_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md)
