# ControlNet and Adapters — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **ControlNet** | Architecture that adds structural conditioning (pose/depth/edges) to a frozen diffusion model |
| **Zero convolution** | 1×1 conv initialized to zero — ensures ControlNet starts without affecting original model |
| **OpenPose** | Human pose estimation producing 18-keypoint skeleton; used with ControlNet pose |
| **LoRA** | Low-Rank Adaptation — fine-tuning large models with tiny rank-decomposition matrices |
| **LoRA rank (r)** | Dimensionality of the factorization; higher = more expressive but more parameters |
| **LoRA scale/weight** | Strength of the LoRA at inference (0.0-2.0 typically; 0.7-1.0 is standard) |
| **IP-Adapter** | Plug-in that adds image-based conditioning alongside text via a second cross-attention stream |
| **DreamBooth** | Fine-tuning technique to teach a model a specific subject/concept from a few images |
| **PEFT** | Parameter-Efficient Fine-Tuning — the family of methods including LoRA |

---

## ControlNet Types at a Glance

| Type | Input | Best For |
|------|-------|----------|
| OpenPose | 18-keypoint skeleton | Body pose control |
| Canny | Edge-detected image | Shape/composition control |
| Depth (MiDaS) | Grayscale depth map | 3D spatial arrangement |
| HED (soft edge) | Soft contour image | Outline control, less strict |
| Segmentation | Color-coded mask | Control what's in each region |
| Normal map | RGB surface normals | Lighting and surface shape |
| Scribble | Rough hand-drawn lines | Loose layout from sketches |
| Line art | Clean line drawing | Character/illustration pose |

---

## LoRA Parameter Guide

| Rank (r) | Parameters | Use Case |
|----------|-----------|----------|
| r=1 | Minimal | Abstract concept/style |
| r=4 | Small (~3MB) | Style, color palette |
| r=8 | Medium (~6MB) | Style with some detail |
| r=16 | Large (~12MB) | Complex style or character |
| r=32+ | Very large | High-fidelity character/face |

**Alpha (α):** Usually set equal to r or r/2. Higher α = stronger LoRA effect.

**Training images needed:** 5-30 for style, 10-20 for character/face.

---

## LoRA Stacking

Multiple LoRAs can be combined at inference:
```python
# diffusers example
pipe.load_lora_weights("style_lora.safetensors", adapter_name="style")
pipe.load_lora_weights("character_lora.safetensors", adapter_name="char")
pipe.set_adapters(["style", "char"], adapter_weights=[0.6, 0.8])
```

Tip: Sum of weights should generally stay ≤ 1.5 to avoid artifacts.

---

## ControlNet Conditioning Scale

The `controlnet_conditioning_scale` parameter (0.0-2.0, default 1.0) controls how strictly the structural input is followed:

| Scale | Effect |
|-------|--------|
| 0.0 | ControlNet has no effect |
| 0.5 | Loose structural guidance; more creative freedom |
| 1.0 | Standard — good balance |
| 1.5 | Strict structural adherence |
| 2.0 | Very strict; may cause visual artifacts |

---

## Quick Decision Guide

```
Need to control structure/composition?
├── Body pose control → OpenPose ControlNet
├── Match 3D depth of reference → Depth ControlNet
├── Match shape/outline of reference → Canny ControlNet
└── Rough layout from sketch → Scribble ControlNet

Need to customize model style/subject?
├── Specific art style → Style LoRA (r=4-8)
├── Specific character/concept → Character LoRA (r=8-16)
├── Specific person's face → DreamBooth or Face LoRA (r=16-32)
└── Reference image style → IP-Adapter

Need image as style reference?
└── IP-Adapter (base for general, Plus for fidelity, FaceID for identity)
```

---

## IP-Adapter Variants

| Variant | Fidelity | Best For |
|---------|----------|----------|
| IP-Adapter | Medium | General style/content transfer |
| IP-Adapter-Plus | High | Detailed style matching |
| IP-Adapter-Plus-Face | High | Face preservation |
| IP-Adapter-FaceID | Very high | Identity-preserving generation |

---

## ControlNet Pipeline Summary

```
Control image (photo) → Preprocessor (e.g., OpenPose detector)
                      → Control map (skeleton)
                      ↓
Text prompt           → U-Net with ControlNet branch
Control map           → ControlNet encoder → zero convolutions → U-Net decoder
                      ↓
                      Generated image respecting both text and structure
```

---

## Golden Rules

1. **ControlNets are model-specific** — SD 1.5 ControlNets won't work with SDXL; use the right version.
2. **Start at conditioning scale 1.0** — adjust to 0.5-1.5 based on how strictly you need structure.
3. **LoRA weight 0.7-1.0 is the sweet spot** — higher causes over-stylization; lower may not activate.
4. **Stack max 2-3 LoRAs** — more gets complex; reduce individual weights when stacking.
5. **IP-Adapter + text prompt together** — text controls content/description, IP-Adapter provides visual style.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | ControlNet code with pose |

⬅️ **Prev:** [Modern Diffusion Models](../05_Modern_Diffusion_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Diffusion vs GANs](../07_Diffusion_vs_GANs/Theory.md)
