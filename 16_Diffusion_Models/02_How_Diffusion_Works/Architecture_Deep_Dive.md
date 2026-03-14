# U-Net Architecture — Deep Dive

## Why U-Net?

The denoiser in a diffusion model faces a unique challenge: it needs to understand an image at multiple levels of abstraction simultaneously.

- **Global structure** (is this a face or a landscape?) — needs high-level, compressed representations
- **Local detail** (is this a wrinkle or a hair strand?) — needs high-resolution spatial maps

A plain CNN loses spatial information as you go deeper. A plain transformer treats everything as patches without explicit resolution hierarchy. The **U-Net** solves this by having a symmetric encoder-decoder with skip connections that explicitly preserve spatial information at every scale.

---

## The U-Net Family Tree

The U-Net was originally designed for biomedical image segmentation (Ronneberger et al., 2015). It was adopted for diffusion models in DDPM (Ho et al., 2020) because its architecture naturally handles the denoising task at multiple resolutions.

```mermaid
flowchart TD
    subgraph ORIG["Original U-Net (2015)"]
        direction LR
        A1[Medical image segmentation]
    end
    subgraph DDPM["DDPM U-Net (2020)"]
        direction LR
        A2[+ Timestep embedding\n+ Group normalization\n+ Self-attention at 16x16]
    end
    subgraph SD["Stable Diffusion U-Net (2022)"]
        direction LR
        A3[+ Cross-attention for text\n+ Larger capacity\n+ Operates on 64x64 latents]
    end

    ORIG --> DDPM --> SD
```

---

## U-Net Architecture Overview

The U-Net has three sections: the **encoder** (downsampling path), the **bottleneck**, and the **decoder** (upsampling path). Skip connections link encoder and decoder at each resolution.

```mermaid
flowchart TD
    IN["Input: xₜ\n(noisy image + timestep)"] --> E1

    subgraph ENCODER["Encoder (Downsampling)"]
        E1["ResBlock 256×256\n64 channels"] -->|"Downsample ×2"| E2
        E2["ResBlock 128×128\n128 channels"] -->|"Downsample ×2"| E3
        E3["ResBlock 64×64\n256 channels + Self-Attention"] -->|"Downsample ×2"| E4
        E4["ResBlock 32×32\n512 channels + Self-Attention"] -->|"Downsample ×2"| BOT
    end

    subgraph BOTTLENECK["Bottleneck"]
        BOT["ResBlock 16×16\n1024 channels\n+ Self-Attention\n+ Cross-Attention (text)"]
    end

    subgraph DECODER["Decoder (Upsampling)"]
        BOT -->|"Upsample ×2"| D1
        D1["ResBlock 32×32\n512 ch"] -->|"Upsample ×2"| D2
        D2["ResBlock 64×64\n256 ch + Self-Attention"] -->|"Upsample ×2"| D3
        D3["ResBlock 128×128\n128 ch"] -->|"Upsample ×2"| D4
        D4["ResBlock 256×256\n64 ch"]
    end

    D4 --> OUT["Output: ε_pred\n(predicted noise)"]

    E1 -.->|"skip connection"| D4
    E2 -.->|"skip connection"| D3
    E3 -.->|"skip connection"| D2
    E4 -.->|"skip connection"| D1

    style IN fill:#1a1a2e,color:#fff
    style OUT fill:#1a1a2e,color:#fff
    style BOT fill:#4a0e8f,color:#fff
```

---

## The Key Building Blocks

### ResBlock (Residual Block)

Each "ResBlock" in the U-Net contains:

```mermaid
flowchart LR
    X["Input features"] --> GN1["GroupNorm"]
    GN1 --> SILU1["SiLU activation"]
    SILU1 --> CONV1["Conv 3×3"]
    CONV1 --> GN2["GroupNorm"]
    GN2 --> SILU2["SiLU"]
    SILU2 --> CONV2["Conv 3×3"]
    CONV2 --> ADD["+ (residual add)"]
    X --> ADD
    TEMB["Timestep embedding\n(sinusoidal → linear)"] --> ADD
    ADD --> OUT["Output features"]
```

The **timestep embedding** is projected via a linear layer and added to the feature maps after the first normalization. This is how the model knows what noise level it's working at — the embedding modulates every ResBlock throughout the entire network.

### Self-Attention Block

Self-attention (the same mechanism from transformers) is applied at the lower-resolution feature maps (e.g., 16×16, 32×32):

```mermaid
flowchart LR
    F["Feature map\n(B, C, H, W)"] --> RESHAPE["Reshape to\n(B, H×W, C)"]
    RESHAPE --> Q["Query projection"]
    RESHAPE --> K["Key projection"]
    RESHAPE --> V["Value projection"]
    Q --> ATTN["Attention scores\nQKᵀ / √d"]
    K --> ATTN
    ATTN --> SOFTMAX["Softmax"]
    SOFTMAX --> MUL["× V"]
    V --> MUL
    MUL --> PROJ["Output projection"]
    PROJ --> RESHAPE2["Reshape back\n(B, C, H, W)"]
    RESHAPE2 --> OUT["+ residual"]
```

Self-attention is expensive at high resolutions (O(n²) complexity where n = H×W). That's why it's only used in the lower-resolution (spatially smaller) parts of the network.

### Cross-Attention Block (Text Conditioning)

In text-conditioned models (like Stable Diffusion), cross-attention layers are added to every ResBlock:

```mermaid
flowchart LR
    F["Image features\n(queries)"] --> Q["Q projection"]
    TEXT["Text embeddings\n(keys and values)"] --> K["K projection"]
    TEXT --> V["V projection"]
    Q --> ATTN["Attention QKᵀ/√d"]
    K --> ATTN
    ATTN --> SM["Softmax"]
    SM --> MUL["× V"]
    V --> MUL
    MUL --> OUT["Conditioned features"]
```

The text embeddings act as keys and values. The image features act as queries. This allows each spatial location in the image to "attend to" relevant parts of the text description — that's how "a red apple on a white table" gets the red color into the right region.

---

## Downsampling and Upsampling

**Downsampling (encoder):** Typically strided convolution or average pooling. Reduces spatial dimensions by 2× while increasing channel count.

**Upsampling (decoder):** Nearest-neighbor or bilinear interpolation followed by convolution. Restores spatial dimensions by 2×.

**Skip connections:** The output of each encoder ResBlock is concatenated channel-wise with the input of the corresponding decoder ResBlock. This doubles the channel count at the concatenation point, which is why decoder blocks typically have a convolution to reduce channels back down.

---

## U-Net Dimensions in Stable Diffusion

For Stable Diffusion 1.5, the U-Net operates on 64×64×4 latent tensors (not pixel space):

| Stage | Spatial Size | Channels | Has Attention? |
|-------|-------------|----------|----------------|
| Input | 64×64 | 4 (latent) | — |
| Encoder block 1 | 64×64 | 320 | No |
| Encoder block 2 | 32×32 | 640 | Yes |
| Encoder block 3 | 16×16 | 1280 | Yes |
| Bottleneck | 8×8 | 1280 | Yes + cross-attn |
| Decoder block 3 | 16×16 | 1280 | Yes |
| Decoder block 2 | 32×32 | 640 | Yes |
| Decoder block 1 | 64×64 | 320 | No |
| Output | 64×64 | 4 (latent) | — |

Total parameters: ~860M for SD 1.5's U-Net.

---

## Why Skip Connections Are Critical

Without skip connections: the decoder must reconstruct all fine-grained spatial information from the bottleneck alone. This is a massive information bottleneck — the 8×8 representation at the bottleneck must contain enough information to reconstruct sharp 64×64 features. It can't.

With skip connections: the decoder at each resolution has direct access to the encoder's high-resolution feature maps from the same scale. The bottleneck handles semantics; the skip connections handle spatial precision.

In denoising, this means: the bottleneck determines the overall structure of the scene, while the skip connections allow the decoder to precisely predict where each noise pixel is.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Simplified math walkthrough |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |

⬅️ **Prev:** [Diffusion Fundamentals](../01_Diffusion_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Stable Diffusion](../03_Stable_Diffusion/Theory.md)
