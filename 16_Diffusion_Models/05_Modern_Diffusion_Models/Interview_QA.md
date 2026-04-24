# Modern Diffusion Models — Interview Q&A

## Beginner Level

**Q1: What are the main improvements in SDXL over SD 1.5?**

<details>
<summary>💡 Show Answer</summary>

A: SDXL (Stable Diffusion XL) improved on SD 1.5 in four key ways:
1. **Higher native resolution**: 1024×1024 instead of 512×512 — less tiling artifacts, better detail at large sizes
2. **Dual text encoders**: Uses both CLIP ViT-L/14 and OpenCLIP ViT-bigG/14 in parallel, giving richer text understanding and better vocabulary coverage
3. **Larger U-Net**: 2.6B parameters (vs 860M), with transformer blocks throughout, enabling more complex scene understanding
4. **Multi-aspect training**: Trained on diverse aspect ratios, making it better at portrait (9:16), landscape (16:9), and square formats

</details>

---

**Q2: What is FLUX and how is it different from Stable Diffusion?**

<details>
<summary>💡 Show Answer</summary>

A: FLUX.1 (by Black Forest Labs, 2024) represents a different architectural paradigm:
- **Architecture**: Uses a Diffusion Transformer (DiT) instead of a U-Net — image patches are processed as tokens in a transformer sequence
- **Training objective**: Uses flow matching (rectified flow) instead of DDPM noise prediction
- **Text encoding**: Uses T5-XXL (4.9B parameter language model) alongside CLIP, enabling much better understanding of complex prompts and text-in-image generation
- **Scale**: 12B parameters — significantly larger than SD 1.5 (860M) or SDXL (2.6B)
- **Quality**: Generally superior, especially for photorealism, complex compositions, and text rendering

The practical cost: FLUX requires significantly more VRAM (24GB ideal, 12GB with quantization).

</details>

---

**Q3: What is flow matching and why is it better than DDPM?**

<details>
<summary>💡 Show Answer</summary>

A: DDPM adds noise along a curved, non-linear path between clean images and Gaussian noise. Flow matching (specifically rectified flow as used in FLUX) instead uses a straight-line interpolation:
```
xₜ = (1-t)·x₀ + t·ε
```
The advantages of straight paths:
1. **Simpler ODE**: Numerical solvers approximate the reverse path more accurately with fewer steps
2. **Fewer inference steps**: FLUX.1-schnell can generate quality images in 1-4 steps vs 20-50 for DDPM
3. **Better scaling**: Straight trajectories are easier for the model to learn at scale
4. **Consistent velocity**: The velocity field is more uniform, giving the model a cleaner learning target

</details>

---

## Intermediate Level

**Q4: Explain the SDXL two-stage pipeline (base + refiner). When should you use the refiner?**

<details>
<summary>💡 Show Answer</summary>

A: The SDXL pipeline optionally uses two models in sequence:
1. **Base model** (SDXL-base-1.0): Generates the initial latent at 1024×1024 for the full denoising trajectory (typically all 20-50 steps)
2. **Refiner model** (SDXL-refiner-1.0): Specializes in adding high-frequency detail at low noise levels (typically the last 20-30% of steps)

The split: you run base from T=1000 to T=200, then switch to refiner from T=200 to T=0.

When to use:
- High-quality outputs where fine texture and detail matter
- Portrait photography (skin texture, hair detail)
- When you have the VRAM (adds ~8GB)

When to skip:
- Fast prototyping
- VRAM-constrained environments
- When LoRA fine-tunes are used (refiner may conflict)

The refiner works because it was trained specifically on the low-noise regime where global structure is set and only fine details need improvement.

</details>

---

**Q5: What is a Diffusion Transformer (DiT) and what advantages does it have over U-Net?**

<details>
<summary>💡 Show Answer</summary>

A: A Diffusion Transformer (DiT) replaces the convolutional U-Net with a pure transformer architecture:

**U-Net approach:**
- Hierarchical encoder-decoder with skip connections
- Convolutions + attention at specific resolutions
- Implicit locality bias (nearby pixels communicate first)
- Complex hyperparameter choices (channel counts per level, which levels get attention)

**DiT approach:**
- Image is split into patches (e.g., 2×2 pixels → 1 patch token)
- All patches processed as a flat sequence with full self-attention
- Each patch sees every other patch at every layer
- Same scaling recipe as language model transformers

**Advantages of DiT:**
1. **Better scalability**: More parameters consistently → better quality (like GPT scaling)
2. **Long-range coherence**: Full attention = every part of the image is globally consistent
3. **Joint image+text attention** (FLUX): Text tokens in the same sequence as image tokens → more direct conditioning
4. **Architectural simplicity**: No complex resolution hierarchy decisions

The downside: attention over full-resolution patches is expensive. FLUX uses 64×64 tokens (4096 patches for 1024px images) — manageable but more expensive than U-Net's hierarchical approach.

</details>

---

**Q6: How does T5-XXL improve FLUX's text understanding compared to CLIP?**

<details>
<summary>💡 Show Answer</summary>

A: CLIP was trained on image-text pairs to align visual and linguistic representations. This makes it excellent at understanding visual concepts but limited in linguistic understanding:
- Maximum 77 tokens
- Struggles with complex grammar, negation, and compositional relationships
- Doesn't understand "the woman to the LEFT of the man" reliably
- Poor at generating text within images

T5-XXL is a language model encoder trained on massive text corpora with span-corruption objectives. It:
- Handles arbitrary length prompts (no 77-token limit in theory)
- Understands complex grammatical structures
- Captures spatial relationships ("to the left of," "behind," "smaller than")
- Handles negation ("without glasses," "not wearing red")
- Enables text-in-image generation by truly understanding character sequences

FLUX uses both: T5-XXL for semantic/linguistic richness and CLIP for image-aligned visual concepts. They provide complementary information.

</details>

---

## Advanced Level

**Q7: Explain the MM-DiT architecture used in Stable Diffusion 3.**

<details>
<summary>💡 Show Answer</summary>

A: Stable Diffusion 3 uses a Multimodal Diffusion Transformer (MM-DiT). Unlike FLUX's sequential approach, MM-DiT maintains separate streams for image and text tokens with a specific interaction pattern:

- **Separate streams**: Image tokens and text tokens have their own parameter matrices in attention layers
- **Joint attention**: Despite separate parameters, they attend to each other in the same attention operation
- **Bidirectional**: Both modalities can influence each other at every layer

The separate parameter matrices allow each modality to develop its own internal representations while still enabling cross-modal interaction. This is different from FLUX's "single sequence" approach where both modalities share the same attention weights.

SD3 also uses three text encoders simultaneously: CLIP-L, OpenCLIP-bigG, and T5-XXL — the outputs are concatenated and used throughout the transformer. This gives it strong text conditioning and text-in-image generation capabilities.

</details>

---

**Q8: What is guidance distillation and how do FLUX.1-schnell and SDXL-Turbo use it?**

<details>
<summary>💡 Show Answer</summary>

A: Guidance distillation bakes the effect of CFG into model weights so inference requires only one forward pass per step (instead of two):

**Training procedure:**
1. Use a "teacher" model with standard CFG at a fixed guidance scale w
2. Train a "student" to produce the same output in a single forward pass
3. The student acts as if it always has guidance scale w active

**Combined with step distillation (FLUX.1-schnell, SDXL-Turbo):**
- Also trains the model to take large steps in denoising
- Combines consistency distillation (few steps) + guidance distillation (single pass)
- Result: 1-4 total U-Net/DiT calls to generate an image (instead of 20-50 × 2)

**Tradeoffs:**
- Fixed guidance scale (cannot change at inference)
- Slightly lower quality ceiling than full FLUX.1-dev with 20 steps
- ~10-20× faster inference
- FLUX.1-schnell (Apache 2.0) is commercially usable without restrictions

</details>

---

**Q9: How do you decide between SDXL and FLUX for a production system?**

<details>
<summary>💡 Show Answer</summary>

A: This is a practical trade-off question:

**Choose SDXL when:**
- VRAM budget < 16GB per GPU
- Existing LoRA/ControlNet ecosystem is critical
- Commercial licensing flexibility needed (SDXL is CreativeML OpenRAIL-M)
- Inference latency must be minimized on commodity hardware
- Team is familiar with the ecosystem and needs maintainable pipelines

**Choose FLUX when:**
- Quality is the top priority, especially for complex prompts
- Text rendering in images is required
- Long, detailed prompts are the norm
- 24GB+ VRAM or quantization is acceptable
- Schnell's Apache 2.0 license fits commercial needs
- Fine-tuning custom FLUX LoRAs is feasible for your team

**Technical considerations:**
- FLUX requires a different scheduler (FlowMatchEulerDiscreteScheduler)
- FLUX's T5-XXL encoder alone is 9.4GB — this must be loaded separately
- FLUX LoRA training requires more compute than SD/SDXL LoRA training
- ComfyUI and HuggingFace diffusers both support FLUX natively

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Model comparison table |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Detailed model comparison |

⬅️ **Prev:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [ControlNet and Adapters](../06_ControlNet_and_Adapters/Theory.md)
