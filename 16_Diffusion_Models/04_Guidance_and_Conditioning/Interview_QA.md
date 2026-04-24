# Guidance and Conditioning — Interview Q&A

## Beginner Level

**Q1: What is Classifier-Free Guidance in simple terms?**

<details>
<summary>💡 Show Answer</summary>

A: CFG is a technique that makes a diffusion model follow a text prompt more closely. It works by running the model twice at every denoising step: once with your text prompt and once without (or with a negative prompt). It then computes the difference — "how much does having this prompt change the prediction?" — and amplifies that difference by the guidance scale w. A higher w means the model pushes harder in the direction the prompt suggests.

</details>

---

**Q2: What does the guidance scale (CFG scale) actually control?**

<details>
<summary>💡 Show Answer</summary>

A: The guidance scale w controls the tradeoff between creativity/quality and prompt adherence:
- At w=1: the output is exactly the conditioned prediction, without amplification. The model follows the prompt but not forcefully.
- At w=7.5: the default. Strong prompt adherence with minimal quality degradation.
- At w=15+: over-amplification. The model exaggerates prompt-related features to the point of saturation and distortion.

Think of it as: "how literally should the model take my description?" — 1 is loosely, 7.5 is carefully, 20 is obsessively.

</details>

---

**Q3: How do negative prompts work?**

<details>
<summary>💡 Show Answer</summary>

A: Negative prompts replace the empty string in the "unconditional" run of CFG. Normally, the baseline prediction uses an empty text (no instruction). When you provide a negative prompt like "blurry, low quality," the baseline prediction instead uses those words as its guidance. The CFG formula then pushes the output *away from* the negative prompt direction as well as *toward* the positive prompt. The model doesn't "avoid" concepts in a hard rule sense — it just gets pushed directionally away from the vector associated with those words.

</details>

---

## Intermediate Level

**Q4: Explain the CFG formula and what each term represents.**

<details>
<summary>💡 Show Answer</summary>

A: The formula is:
```
ε_guided = ε_uncond + w × (ε_text − ε_uncond)
```
- `ε_uncond` — noise prediction with no text (or negative prompt). This is the "what would the model do with no instructions?" baseline.
- `ε_text` — noise prediction with the positive text prompt.
- `(ε_text − ε_uncond)` — the prompt direction vector: which way is the text pulling, relative to the unconditioned baseline?
- `w` — how far to walk in that direction. At w=1, you just use ε_text. At w=7.5, you go 6.5 steps beyond ε_text in the same direction.

This is a form of extrapolation: you identify the direction the prompt is pulling and amplify it.

</details>

---

**Q5: Why does high CFG scale cause image quality degradation?**

<details>
<summary>💡 Show Answer</summary>

A: CFG extrapolates beyond the model's natural prediction range. The model was trained to produce noise predictions ε that are roughly normalized — values staying within a reasonable range. When you multiply the deviation (ε_text - ε_uncond) by a large w, the guided prediction can have values far outside the trained range. This causes:
- Over-saturation of colors (extreme pixel values)
- Sharpening artifacts at edges
- Distortion of fine details (especially faces)
- Loss of natural texture variety

The model is essentially being told to follow the prompt beyond what it naturally produces, leading it outside its training distribution.

</details>

---

**Q6: How does cross-attention implement text conditioning in the U-Net?**

<details>
<summary>💡 Show Answer</summary>

A: In each cross-attention layer:
1. The image feature map (shape: B × H×W × C) is projected to queries Q
2. The CLIP text embeddings (shape: B × 77 × 768) are projected to keys K and values V
3. Attention scores: softmax(QKᵀ / √d) gives weights over 77 text tokens for each spatial position
4. Output: weighted sum of V — each spatial position gets a blend of value vectors weighted by how much it attends to each word

The attention weight maps are what make cross-attention interpretable: if you visualize them, you can see "which word influenced which region of the image." This is the foundation of Prompt-to-Prompt editing.

</details>

---

**Q7: What is the difference between CFG and Classifier Guidance?**

<details>
<summary>💡 Show Answer</summary>

A: **Classifier Guidance** (Dhariwal & Nichol, 2021) uses a separate noise-robust classifier p_φ(y|x_t) to compute gradients that steer the denoising:
```
ε_guided = ε_θ(xₜ, t) - √(1-ᾱₜ) · ∇_xₜ log p_φ(y | xₜ)
```
Requires: training a special classifier that works on noisy images at all noise levels.

**Classifier-Free Guidance** (Ho & Salimans, 2022) uses the model's own unconditional prediction as a proxy for the classifier gradient:
```
ε_guided = ε_uncond + w × (ε_cond - ε_uncond)
```
Requires: no separate classifier; just training the diffusion model to also accept empty conditioning.

CFG won because it's simpler, works with arbitrary text (not just class labels), requires no extra model, and produces comparable or better quality.

</details>

---

## Advanced Level

**Q8: Explain CFG Distillation (as used in FLUX and SDXL-Turbo) and why it matters.**

<details>
<summary>💡 Show Answer</summary>

A: Standard CFG requires two U-Net forward passes per denoising step, doubling inference cost. CFG Distillation (sometimes called "guidance distillation") trains a new model to produce the guided output in a single forward pass:

1. Train a "teacher" with standard CFG at a fixed guidance scale
2. Train a "student" to match the teacher's *guided* outputs in a single pass
3. The student bakes the guidance behavior directly into its weights

The student model acts as if guidance is always active at the distillation scale, using only one U-Net call per step. FLUX.1-dev and FLUX.1-schnell use this approach. SDXL-Lightning and SDXL-Turbo combine guidance distillation with consistency distillation (fewer steps). The tradeoff: the guidance scale is fixed at distillation time — you lose the ability to vary CFG at inference.

</details>

---

**Q9: How does InstructPix2Pix extend CFG to image editing?**

<details>
<summary>💡 Show Answer</summary>

A: InstructPix2Pix (Brooks et al., 2022) conditions on both a source image and a text instruction (e.g., "make the sky sunset colors"). It uses two-dimensional CFG with two separate guidance scales:

```
ε_guided = ε_∅∅ + s_I · (ε_c_I∅ - ε_∅∅) + s_T · (ε_c_Ic_T - ε_c_I∅)
```

Where:
- ε_∅∅ = no image, no text
- ε_c_I∅ = image-only, no text
- ε_c_Ic_T = image + text instruction
- s_I = image guidance scale (how much to preserve the image)
- s_T = text guidance scale (how strongly to follow the instruction)

This allows independent control over "how much does the output look like the input image" and "how faithfully does it follow the text instruction."

</details>

---

**Q10: What is Prompt-to-Prompt and how does it relate to cross-attention?**

<details>
<summary>💡 Show Answer</summary>

A: Prompt-to-Prompt (Hertz et al., 2022) is an image editing technique that operates by swapping or modifying cross-attention maps between a source and edited generation. The key insight: the cross-attention maps in the U-Net determine the spatial layout of objects. If you keep those maps from the original generation while changing the tokens, you preserve structure while editing content.

For example:
- Generate "a dog sitting on the beach" — save all cross-attention maps
- Generate "a cat sitting on the beach" — but inject the saved maps from the "dog" run
- The cat will appear in the same position and pose as the dog, because the attention maps (spatial layout) are shared

This works because cross-attention attention weights encode "which word goes where in the image" — they are the structural blueprint of the scene, independent of the specific content.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | CFG guide + negative prompt tips |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | CFG scale comparison code |

⬅️ **Prev:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Modern Diffusion Models](../05_Modern_Diffusion_Models/Theory.md)
