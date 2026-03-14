# Stable Diffusion — Full Architecture Deep Dive

## The Big Picture

Stable Diffusion is a composition of four independently trained components, connected into a single inference pipeline. Understanding which component does what is essential for debugging, customizing, and fine-tuning.

```mermaid
flowchart TD
    subgraph INPUTS["User Inputs"]
        PROMPT["Text prompt\n'a red fox in a snowy forest'"]
        NEGPROMPT["Negative prompt\n'blurry, low quality'"]
        SEED["Random seed"]
        PARAMS["Inference steps: 30\nGuidance scale: 7.5\nSize: 512×512"]
    end

    subgraph TEXTENC["① CLIP Text Encoder (frozen)"]
        TOK["Tokenizer\n(BPE, max 77 tokens)"]
        CLIPMODEL["CLIP Transformer\n(12 layers, ViT-L/14)\n123M params"]
        TEXTOUT["Text embeddings\n(77, 768)"]
        TOK --> CLIPMODEL --> TEXTOUT
    end

    subgraph LATENTNOISE["② Latent Noise"]
        GAUSSIAN["Sample z_T ~ N(0,I)\nshape: (1, 4, 64, 64)"]
    end

    subgraph DIFFUSION["③ Diffusion Denoising Loop (runs N times)"]
        UNET["U-Net\n860M params\n(encoder + bottleneck + decoder\nwith skip connections + cross-attention)"]
        CFG["Classifier-Free Guidance\nε_guided = ε_uncond + w(ε_text - ε_uncond)"]
        STEP["Scheduler step\n(DDIM / DPM++ / Euler)"]
        UNET --> CFG --> STEP
    end

    subgraph VAEDEC["④ VAE Decoder (runs once)"]
        DECODE["Convolutional decoder\n8 blocks, skip connections\n84M params"]
        PIXELS["Output image\n(512, 512, 3) RGB"]
        DECODE --> PIXELS
    end

    PROMPT --> TOK
    NEGPROMPT --> TOK
    TEXTOUT --> UNET
    SEED --> GAUSSIAN
    GAUSSIAN --> UNET
    PARAMS --> DIFFUSION
    STEP --> UNET
    STEP -->|"Final x₀ latent\n(1, 4, 64, 64)"| DECODE

    style PIXELS fill:#1b4332,color:#fff
    style UNET fill:#4a0e8f,color:#fff
```

---

## Component 1: CLIP Text Encoder

```mermaid
flowchart LR
    TEXT["'a red fox in snowy forest'"] --> TOKENIZE

    subgraph TOKENIZE["Tokenization (BPE)"]
        TOK1["[SOT]"]
        TOK2["'a'"]
        TOK3["'red'"]
        TOK4["'fox'"]
        TOK5["'in'"]
        TOK6["'sn'"]
        TOK7["'owy'"]
        TOK8["'forest'"]
        TOK9["[EOT]"]
        TOKNPAD["[PAD] × 68"]
    end

    TOKENIZE --> EMBED["Token embeddings\n(77, 768)"]
    EMBED --> TRANSFORMER["Transformer\n12 layers\nself-attention\n768 hidden dim"]
    TRANSFORMER --> CONTEXT["Text context\n(77, 768)\nOne vector per token"]

    style CONTEXT fill:#1a3a5c,color:#fff
```

Key points:
- Maximum 77 tokens including [SOT] and [EOT] markers = 75 usable tokens for prompt
- Output shape: (77, 768) — not a single vector, but 77 vectors, one per token position
- The full sequence is used, not just the final [EOT] token — this preserves per-word information
- CLIP was trained on image-text alignment; it understands visual-semantic relationships

---

## Component 2: U-Net Architecture Detail

The U-Net in SD 1.5 has a specific structure with 4 resolution levels:

```mermaid
flowchart TD
    subgraph INPUT_PROC["Input Processing"]
        NOISEIN["Noisy latent\n(1, 4, 64, 64)"] --> INCONV["Conv 3×3\n→ 320 channels\n(1, 320, 64, 64)"]
        TEMBRAW["Timestep t\n(scalar)"] --> SINUSOIDAL["Sinusoidal\nembedding\n(320,)"]
        SINUSOIDAL --> LINEAR1["Linear 320→1280"]
        LINEAR1 --> LINEAR2["Linear 1280→1280"]
        LINEAR2 --> TEMB["Timestep embed\n(1280,)"]
    end

    subgraph ENCODER["Encoder"]
        E1["Level 1: 64×64\n320 ch, 2× ResBlock\n(no attention)"]
        E2["Level 2: 32×32\n640 ch, 2× ResBlock\n+ cross-attention"]
        E3["Level 3: 16×16\n1280 ch, 2× ResBlock\n+ cross-attention"]
        E4["Level 4: 8×8\n1280 ch, 2× ResBlock\n+ cross-attention"]
        E1 -->|"Downsample ×2"| E2
        E2 -->|"Downsample ×2"| E3
        E3 -->|"Downsample ×2"| E4
    end

    subgraph BOTTLENECK["Bottleneck (8×8)"]
        BOT["ResBlock + Self-Attn\n+ Cross-Attn\n1280 ch"]
    end

    subgraph DECODER["Decoder"]
        D4["Level 4: 8×8\n1280 ch + skip"]
        D3["Level 3: 16×16\n1280 ch + skip\n+ cross-attention"]
        D2["Level 2: 32×32\n640 ch + skip\n+ cross-attention"]
        D1["Level 1: 64×64\n320 ch + skip"]
        D4 -->|"Upsample ×2"| D3
        D3 -->|"Upsample ×2"| D2
        D2 -->|"Upsample ×2"| D1
    end

    OUTPUT["Output conv\n→ 4 channels\n(1, 4, 64, 64)"]

    INCONV --> E1
    E4 --> BOT --> D4
    D1 --> OUTPUT

    E1 -.->|skip| D1
    E2 -.->|skip| D2
    E3 -.->|skip| D3
    E4 -.->|skip| D4

    TEMB --> E1
    TEMB --> E2
    TEMB --> E3
    TEMB --> E4
    TEMB --> BOT
    TEMB --> D4
    TEMB --> D3
    TEMB --> D2
    TEMB --> D1

    style BOT fill:#4a0e8f,color:#fff
    style OUTPUT fill:#1a3a5c,color:#fff
```

### Cross-Attention in Detail (how text guides image)

Inside each cross-attention block in the U-Net:

```mermaid
flowchart LR
    subgraph IMAGE["Image features (queries)"]
        IMGF["Feature map\n(1, 64, H×W)"]
        IMGF --> Q["Linear → Q\n(1, H×W, 64)"]
    end

    subgraph TEXT_INPUT["Text context (keys + values)"]
        TEXTF["CLIP embeddings\n(1, 77, 768)"]
        TEXTF --> K["Linear → K\n(1, 77, 64)"]
        TEXTF --> V["Linear → V\n(1, 77, 64)"]
    end

    Q --> SCORES["QKᵀ / √64\n(1, H×W, 77)\n— each pixel attends to\n   all 77 text tokens —"]
    K --> SCORES
    SCORES --> SM["Softmax over 77 tokens\n(attention weights)"]
    SM --> WV["Weighted sum × V\n(1, H×W, 64)"]
    V --> WV
    WV --> OUTPROJ["Output linear\n→ (1, H×W, ch)"]
```

This is how "red" goes into the fox and "snowy" goes into the background — spatial positions that "should be fox" attend strongly to the "red" and "fox" tokens.

---

## Component 3: VAE Architecture

The VAE encoder compresses and the decoder expands. Both use residual blocks and attention at the bottleneck:

```mermaid
flowchart LR
    subgraph ENC["VAE Encoder"]
        E_IN["Image\n512×512×3"] --> E1["Conv + 2× ResBlock\n64ch, 512×512"]
        E1 --> E2["Conv + 2× ResBlock\n128ch, 256×256"]
        E2 --> E3["Conv + 2× ResBlock\n256ch, 128×128"]
        E3 --> E4["Conv + 2× ResBlock\n512ch, 64×64"]
        E4 --> E_MID["Self-Attention\n+ ResBlock"]
        E_MID --> E_OUT["Conv → μ, logσ²\n8ch, 64×64\n(sample to get z, 4ch)"]
    end

    subgraph DEC["VAE Decoder"]
        D_IN["Latent z\n64×64×4"] --> D_CONV["Conv → 512ch\n64×64"]
        D_CONV --> D_MID["ResBlock + Self-Attn\n+ ResBlock"]
        D_MID --> D1["Upsample + 3× ResBlock\n512ch → 256ch, 128×128"]
        D1 --> D2["Upsample + 3× ResBlock\n256ch → 128ch, 256×256"]
        D2 --> D3["Upsample + 3× ResBlock\n128ch → 64ch, 512×512"]
        D3 --> D_OUT["GroupNorm + SiLU\n+ Conv → 3ch RGB\n512×512×3"]
    end

    style E_OUT fill:#4a0e8f,color:#fff
    style D_OUT fill:#1b4332,color:#fff
```

---

## Classifier-Free Guidance — The Math

During inference, the U-Net is called twice per step:

```mermaid
flowchart TD
    XN["Noisy latent xₜ"] --> UNET1["U-Net\n(text condition)"]
    XN --> UNET2["U-Net\n(empty / negative prompt)"]

    UNET1 --> ECOND["ε_text"]
    UNET2 --> EUNCOND["ε_uncond"]

    ECOND --> CFG["ε_guided = ε_uncond + w × (ε_text - ε_uncond)"]
    EUNCOND --> CFG

    CFG --> STEP["Scheduler step → xₜ₋₁"]

    style CFG fill:#7f1d1d,color:#fff
```

The guidance scale w controls how far to "push" toward the text condition:
- w=1: no guidance (same as using text condition without CFG)
- w=7.5: strong adherence to prompt (SD default)
- w=15+: over-adherence — artifacts, over-saturation

---

## Inference Timeline

```mermaid
sequenceDiagram
    participant USER as User
    participant CLIP as CLIP Encoder
    participant SCHED as Scheduler
    participant UNET as U-Net
    participant VAE as VAE Decoder

    USER->>CLIP: Tokenize prompt + negative prompt
    CLIP-->>UNET: Text embeddings (77, 768) × 2

    USER->>SCHED: Initialize noise z_T ~ N(0,I) [shape 64×64×4]

    loop 30 denoising steps (t = T → 0)
        SCHED->>UNET: z_t + timestep t
        UNET->>UNET: Predict ε (text-conditioned)
        UNET->>UNET: Predict ε (unconditioned)
        UNET-->>SCHED: ε_guided (after CFG)
        SCHED->>SCHED: Compute z_{t-1}
    end

    SCHED->>VAE: Final clean latent z_0 (64×64×4)
    VAE-->>USER: Decoded image (512×512×3)
```

---

## Total Compute Budget (per inference)

| Component | When | # Calls | Cost |
|-----------|------|---------|------|
| CLIP text encoder | Once | 1-2 | Tiny (123M params, fast) |
| U-Net forward pass | Every step | 30 × 2 = 60 (with CFG) | Heavy (860M params) |
| VAE decoder | Once | 1 | Medium (84M params) |
| VAE encoder | Only for img2img | 0-1 | Medium |

The U-Net is responsible for 95%+ of the total compute in a standard generation.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Conceptual overview |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Generate images with diffusers |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |

⬅️ **Prev:** [How Diffusion Works](../02_How_Diffusion_Works/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Guidance and Conditioning](../04_Guidance_and_Conditioning/Theory.md)
