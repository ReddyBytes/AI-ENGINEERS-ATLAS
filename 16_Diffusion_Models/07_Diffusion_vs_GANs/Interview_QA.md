# Diffusion vs GANs — Interview Q&A

## Beginner Level

**Q1: What is the main training stability difference between GANs and diffusion models?**

<details>
<summary>💡 Show Answer</summary>

A: GANs train two networks in an adversarial minimax game: the generator tries to fool the discriminator, and the discriminator tries to distinguish real from fake. This creates an unstable training dynamic — if the discriminator gets too good, the generator's gradients vanish and it stops learning. If the generator gets too clever, the discriminator's gradients vanish. The networks must stay perfectly balanced throughout training, which is difficult and sensitive to hyperparameters.

Diffusion models train a single network (U-Net) with a straightforward MSE objective: given a noisy image at timestep t, predict the noise that was added. This is a well-conditioned regression problem at every batch — no adversarial dynamic, no competing networks, no vanishing gradients from a second network. The loss surface is smooth and stable. This is why diffusion models train reliably at scale while GANs often require careful hyperparameter tuning and may fail to converge.

</details>

---

<br>

**Q2: What is mode collapse in GANs and why don't diffusion models suffer from it?**

<details>
<summary>💡 Show Answer</summary>

A: Mode collapse is when the GAN generator produces only a narrow subset of the possible outputs — for example, always generating one type of face even though the training set has great diversity. It happens because the generator's optimization target is to fool the discriminator, not to cover the full training distribution. Once the generator finds outputs that reliably fool the discriminator, it has no incentive to produce variety.

Diffusion models don't suffer from mode collapse because their training signal comes from every noise level in the training data independently. Each batch is a regression problem: "given this partially noised image, remove some noise." The training explicitly covers the full training distribution at every step. There's no competition and no incentive to collapse — the model must learn to reconstruct all types of images, not just find a subset that fools a critic.

</details>

---

<br>

**Q3: What is inference speed and why is it a disadvantage for diffusion models compared to GANs?**

<details>
<summary>💡 Show Answer</summary>

A: Inference speed is how long it takes to generate one image after training. A GAN's generator is a single neural network: run one forward pass, get one image — typically under 100ms on a GPU. This is fast enough for real-time applications.

A diffusion model generates by reversing the noising process over many steps. The original DDPM approach takes 1000 denoising steps. Even with DDIM (Denoising Diffusion Implicit Models) reducing this to 20-50 steps, each step requires a U-Net forward pass — typically 2-30 seconds total for a high-quality image. Distilled models (SDXL-Turbo, LCM) can reduce this to 1-4 steps, but quality may decrease. For applications requiring real-time generation (video games, webcam filters), GANs' single-pass inference remains a genuine advantage over diffusion, even after distillation.

</details>

---

## Intermediate Level

**Q4: What is FID score and what does it tell us about diffusion vs GAN quality?**

<details>
<summary>💡 Show Answer</summary>

A: **FID (Fréchet Inception Distance)** measures the statistical similarity between the distribution of generated images and the distribution of real images, using features extracted by InceptionV3. A lower FID score is better — zero means the distributions are identical.

FID captures two aspects: (1) quality — do generated images look realistic? and (2) diversity — does the generator cover the full range of the training distribution (not just a few modes)?

GANs historically achieved low FID scores in specific domains (e.g., StyleGAN2 achieves ~2.84 FID on FFHQ faces), but their FID degrades when trained on diverse, general datasets due to mode collapse. Diffusion models achieve very low FID on general datasets while maintaining diversity, because they don't suffer from mode collapse. On ImageNet (a diverse 1000-class dataset), diffusion models significantly outperform GANs in FID. On narrow domains like human faces, StyleGAN remains competitive.

</details>

---

<br>

**Q5: When should an ML engineer choose a GAN over a diffusion model for a production system?**

<details>
<summary>💡 Show Answer</summary>

A: Choose a GAN over diffusion when:

**Real-time inference is required**: a single generator forward pass produces images in <100ms. Diffusion models take 2-30+ seconds even with acceleration. For video game character generation, webcam-style effects, or any application needing sub-second generation, GANs win.

**Super-resolution pipelines**: ESRGAN and Real-ESRGAN remain the standard for upscaling existing images to higher resolution. They're fast, accurate, and specifically trained for this task.

**Edge deployment**: GAN generators are typically 50-300MB. SDXL is 6-7GB, FLUX is 24GB. Deploying on mobile or embedded devices requires a GAN or a heavily quantized distilled model.

**Domain-specific generation at scale**: if you're generating a specific type of content (e.g., product photos with fixed lighting) and mode collapse is not a risk (because you want consistency), a domain-trained GAN can be faster and smaller than a general diffusion model.

**Cost at scale**: generating 1 million images with a GAN at <100ms each takes ~28 hours at 1 GPU. The same job with diffusion at 5 seconds each takes 58 days. Cost at scale is a genuine constraint.

</details>

---

<br>

**Q6: Explain the architectural differences between a GAN discriminator and a diffusion U-Net. What different functions do they serve?**

<details>
<summary>💡 Show Answer</summary>

A: These serve fundamentally different functions in their respective architectures.

**GAN discriminator**: a classification network. Input: an image (real or generated). Output: a probability (0 = fake, 1 = real). Architecture is typically a convolutional classifier — takes the full image, outputs a scalar. It's an adversary, not a generator component. It's discarded after training; only the generator is kept for inference.

**Diffusion U-Net**: a noise prediction network. Input: a noisy image xₜ and timestep t. Output: the predicted noise ε_pred that was added to create xₜ. Architecture is an encoder-decoder with skip connections (U-Net shape) — it needs to reason at multiple spatial scales to predict both coarse structure and fine detail in the noise. The timestep t is embedded and injected at each layer. It's used at inference time for every denoising step.

The U-Net also supports text conditioning via cross-attention layers that take text embeddings as input — enabling text-to-image generation. The GAN discriminator has no equivalent conditioning mechanism (GANs are notoriously difficult to condition on free-form text).

</details>

---

## Advanced Level

**Q7: Describe the quality-diversity tradeoff between GANs and diffusion models and how it impacts production use cases.**

<details>
<summary>💡 Show Answer</summary>

A: Quality and diversity are often in tension in generative models. High quality typically means the model has learned to produce precise, sharp, photorealistic outputs — but may only do so for a subset of possible outputs (low diversity). High diversity means the model covers the full training distribution but may sacrifice per-sample fidelity.

**GANs**: achieve high quality in specific, narrow domains (human faces, cars) but low diversity — mode collapse limits output variety. StyleGAN2 on faces achieves stunning quality because it's trained in a narrow, well-defined distribution. The same model on general image synthesis would collapse. In production: excellent for applications with a fixed, narrow generation target and high quality requirement.

**Diffusion models**: achieve high quality AND high diversity across broad distributions. The training objective (denoising at every noise level) inherently covers the full distribution. However, controlling the quality-diversity tradeoff at inference is possible via CFG scale: high CFG scale → higher quality (closer to text prompt) but lower diversity; low CFG scale → higher diversity but lower fidelity. Production implication: diffusion models are the default choice for general-purpose generation, creative applications, and any use case requiring breadth.

**Real production impact**: a customer generating personalized product photos for an e-commerce platform wants both quality and diversity. Diffusion wins — it can produce hundreds of varied high-quality product shots. A game studio generating face textures for a specific character wants consistent high quality with minimal variation. A GAN trained on that character's face distribution wins.

</details>

---

<br>

**Q8: What are the memory requirements for GANs vs diffusion models at inference, and how does this affect deployment architecture?**

<details>
<summary>💡 Show Answer</summary>

A: Memory comparison at inference:

**GAN (e.g., StyleGAN2, 1024×1024)**:
- Generator: ~130MB (parameters)
- VRAM at inference: ~1-2GB (parameters + activations for one forward pass)
- Suitable for: consumer GPU (6GB VRAM), mobile (with quantization), edge devices

**Diffusion model (Stable Diffusion 1.5)**:
- U-Net + VAE + CLIP text encoder: ~4GB
- VRAM at inference: 4-8GB (must hold all components simultaneously)
- Suitable for: mid-range consumer GPU (8GB VRAM+)

**Stable Diffusion XL**:
- 6-7GB parameters
- VRAM at inference: 8-16GB
- Suitable for: high-end consumer or professional GPU

**FLUX.1 dev (12B parameters)**:
- ~24GB in fp16
- VRAM at inference: 24-32GB
- Suitable for: A100/H100 in cloud; not consumer hardware at full precision

Deployment implications: GANs can be served from much smaller and cheaper hardware. Diffusion models require GPU instances (not CPU-only). At scale: serving 1000 diffusion inference requests/hour requires significantly more GPU capacity than 1000 GAN requests/hour. Distillation and quantization (int8, int4) reduce diffusion inference cost but add model complexity. For cost-sensitive, high-volume production: GANs remain competitive if quality-diversity requirements allow it.

</details>

---

<br>

**Q9: Explain why text conditioning is fundamentally harder for GANs than for diffusion models, and how this led to diffusion models dominating text-to-image generation.**

<details>
<summary>💡 Show Answer</summary>

A: Text conditioning requires the model to understand arbitrary natural language prompts and generate images that semantically match them. This is a challenging conditioning problem.

**Why GANs struggle with text conditioning**:
The GAN discriminator must evaluate whether a generated image matches a text prompt — a much harder task than "real vs fake." The discriminator needs to understand semantics. Most attempts at text-conditional GANs required complex architectures (e.g., AttnGAN, DF-GAN) that were harder to train and still produced lower quality than diffusion at scale. Mode collapse becomes worse with text conditioning — the generator can produce one plausible image for any prompt rather than exploring the diversity of valid matches.

**Why diffusion models handle text conditioning naturally**:
Diffusion models use cross-attention to condition the denoising process on text embeddings. This is architecturally natural: at each denoising step, the U-Net can attend to the text embedding to guide what it removes. The CLIP text encoder provides a rich semantic space that aligns well with image features. Classifier-free guidance (CFG) amplifies text adherence at inference — a simple technique with no adversarial training complications.

**Classifier-free guidance specifically**: by training the diffusion model both with and without text conditioning (randomly dropping the text during training), CFG allows controlling text adherence at inference: `noise_pred = uncond + scale * (cond - uncond)`. Increasing scale pushes generation toward the text description. This fine-grained inference-time control has no GAN equivalent and was critical to the quality of DALL-E 2, Stable Diffusion, and all modern text-to-image models.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Full side-by-side comparison table |

⬅️ **Prev:** [ControlNet and Adapters](../06_ControlNet_and_Adapters/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 16 Complete](../Readme.md)
