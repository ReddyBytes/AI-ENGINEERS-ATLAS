# Stable Diffusion — Interview Q&A

## Beginner Level

**Q1: What does "latent diffusion" mean and why is it important?**

<details>
<summary>💡 Show Answer</summary>

A: Latent diffusion means running the diffusion process in the compressed latent space of a VAE rather than directly on pixels. A 512×512 image has 786,432 pixel values. The SD 1.5 VAE compresses this to a 64×64×4 latent with only 16,384 values — a 48× reduction. The denoising loop runs on these small latents, making each U-Net forward pass 48× cheaper in memory and significantly faster. Only the very last step (VAE decode) is in pixel space. This is what makes high-quality diffusion possible on consumer GPUs.

</details>

---

<br>

**Q2: What is CLIP's role in Stable Diffusion?**

<details>
<summary>💡 Show Answer</summary>

A: CLIP (Contrastive Language-Image Pre-training) provides the text encoder. When you type a prompt, it gets tokenized into up to 77 tokens, then passed through CLIP's transformer encoder. The output is a sequence of 768-dimensional vectors — one per token — that capture the semantic meaning of the text in a way that was learned by aligning with images. These vectors are used as keys and values in the cross-attention layers of the U-Net, allowing the text to guide what gets generated at each spatial location.

</details>

---

<br>

**Q3: What is the VAE in Stable Diffusion and what is its role?**

<details>
<summary>💡 Show Answer</summary>

A: The VAE (Variational Autoencoder) has two jobs:
1. **Encode**: At the start of img2img, or conceptually in the training process, the VAE encoder compresses a 512×512 RGB image into a 64×64×4 latent tensor.
2. **Decode**: At the very end of every generation, the VAE decoder takes the clean denoised latent and reconstructs a full 512×512 RGB image.

The VAE is trained separately on image reconstruction, then frozen during diffusion training and inference. It's not involved in the denoising loop — only at the start (if conditioning on an image) and end.

</details>

---

<br>

**Q4: What does the 4-channel latent in Stable Diffusion represent?**

<details>
<summary>💡 Show Answer</summary>

A: The 4 channels are not RGBA. They are 4 learned feature channels in the VAE's latent space that the encoder found to be the most efficient way to represent image content for reconstruction. Channel 1 might broadly correlate with brightness, others with color and texture, but there's no clean human-readable interpretation. What matters is that the 4 channels together contain enough information to reconstruct a high-quality image when decoded.

</details>

---

## Intermediate Level

**Q5: Explain the img2img process in Stable Diffusion.**

<details>
<summary>💡 Show Answer</summary>

A: img2img starts with a real input image and uses it as a conditioning signal:
1. Encode the input image to latent space using the VAE encoder
2. Add noise to the latent up to timestep t_start (where t_start < T controls the "denoising strength" — higher t_start = more change)
3. Run the reverse denoising loop from t_start to 0, guided by the new text prompt
4. Decode the result with the VAE decoder

At denoising strength 0.5, you start from a moderately noisy version of the input. The output will preserve the rough composition of the input while changing details. At denoising strength 1.0, you add maximum noise (like generating from scratch) and the input is largely ignored.

</details>

---

<br>

**Q6: Why does Stable Diffusion have a VAE scale factor of 0.18215?**

<details>
<summary>💡 Show Answer</summary>

A: The VAE's encoder doesn't produce latents with unit standard deviation — empirically, the latents have std ≈ 5.5 (for SD 1.5). If you feed these into the noise schedule directly, the Gaussian noise (std=1) would be negligible compared to the latent values, and the diffusion process would be miscalibrated. The scale factor 0.18215 ≈ 1/5.5 normalizes the latents to approximately unit standard deviation before diffusion. Without it, the model would behave as if it were at very low noise levels even at t=T. This constant is baked into the pipeline and must be applied in any custom implementation.

</details>

---

<br>

**Q7: How does CLIP's 77-token limit affect long prompts?**

<details>
<summary>💡 Show Answer</summary>

A: CLIP was trained with a maximum context length of 77 tokens (including start and end tokens, so effectively 75 for the prompt). Tokens are subword units — most English words are 1-2 tokens, but complex or rare words may be more. For prompts longer than 75 tokens, standard SD implementations truncate, silently dropping the end of the prompt. Techniques for handling longer prompts:
1. Chunking: split into 77-token chunks and average the embeddings (used in A1111 WebUI)
2. Multiple conditioning: some pipelines accept 2-3 prompt chunks and concatenate
3. Use SDXL which supports 77×2 tokens via two encoders
Key practical lesson: put the most important concepts at the beginning of your prompt.

</details>

---

<br>

**Q8: What is the difference between a base model and a fine-tuned model in the SD ecosystem?**

<details>
<summary>💡 Show Answer</summary>

A: A base model (like SD 1.5 or SDXL) is trained on hundreds of millions of images and can generate diverse content across many domains. A fine-tuned model is further trained on a curated dataset to specialize in a style or subject — for example:
- **Realistic Vision** — fine-tuned on photorealistic human portraits
- **DreamShaper** — fine-tuned on fantasy and painterly art
- **Juggernaut XL** — fine-tuned on SDXL for photorealism

Fine-tuning is done via full fine-tuning (rare, expensive), DreamBooth (teaches the model a specific subject), or LoRA (teaches a style/subject with small weight matrices). The base model weights remain the reference architecture; all community models are fine-tunes on top.

</details>

---

## Advanced Level

**Q9: How does cross-attention in the U-Net actually implement text conditioning?**

<details>
<summary>💡 Show Answer</summary>

A: In each cross-attention layer, the image latent feature map (shape: (B, H×W, C_image)) is projected to queries Q, while the CLIP text embeddings (shape: (B, 77, 768)) are projected to keys K and values V:

```
Attention = softmax(QKᵀ / √d) · V
```

Each spatial position in the image (each query) computes attention weights over all 77 text tokens (keys), then takes a weighted sum of the value vectors. Positions that are semantically related to a particular text token will attend to it highly. This allows "the beach area should have the texture and color associated with the word beach" to emerge naturally from the optimization. The attention maps can be visualized and manipulated — which is the basis for techniques like Prompt-to-Prompt (Hertz et al., 2022).

</details>

---

<br>

**Q10: Explain the difference between the VAE's role in training vs. inference for Latent Diffusion Models.**

<details>
<summary>💡 Show Answer</summary>

A: During **training**, the VAE encoder is used to pre-process all training images into latents. These latents are cached on disk, and the diffusion model is trained on them. The VAE encoder is frozen — its weights don't change during diffusion training. The diffusion model never sees pixels directly.

During **inference**, the VAE encoder is only needed for img2img (to encode the starting image). For text-to-image generation from scratch, the process starts directly in latent space with sampled Gaussian noise — the VAE encoder is never called. The VAE decoder is always called at the end to convert the final denoised latent back to pixels.

This separation of concerns is a key design choice: the VAE is trained to be a good perceptual compressor, independently of the diffusion process.

</details>

---

<br>

**Q11: What is CLIP vs. OpenCLIP and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

A: OpenAI's CLIP (ViT-L/14) is proprietary, trained on 400M image-text pairs, and used in SD 1.5. OpenCLIP is an open-source reimplementation by LAION, trained on 2 billion+ pairs with larger model variants (ViT-H, ViT-G). OpenCLIP has:
- Larger vocabulary of visual concepts (more training data)
- Better understanding of complex compositional descriptions
- Fully open weights — no API restrictions

SD 2.x switched to OpenCLIP ViT-H. SDXL uses both CLIP ViT-L and OpenCLIP ViT-G simultaneously — their outputs are concatenated (768+1280=2048 dims total) giving the model richer text conditioning.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Generate images with diffusers |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full SD architecture diagram |

⬅️ **Prev:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md)
