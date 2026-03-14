# Vision-Language Models — Architecture Deep Dive

## CLIP Architecture

### Overview

CLIP learns a shared embedding space for images and text by training two separate encoders with a contrastive objective. After training, any image and any text description can be compared directly by measuring the cosine similarity of their embeddings.

```mermaid
flowchart TB
    subgraph Input ["Training Input (one batch)"]
        P1["(img₁, 'a photo of a dog')"]
        P2["(img₂, 'a sunset over water')"]
        PN["(imgₙ, 'a red sports car')"]
    end

    subgraph ImagePath ["Image Processing Path"]
        IP[Image Patches\n16×16 pixel grid]
        PE[Positional\nEmbeddings added]
        VIT[Vision Transformer\nViT-B/32 or ViT-L/14]
        CLS[CLS Token\n= image embedding]
        IP --> PE --> VIT --> CLS
    end

    subgraph TextPath ["Text Processing Path"]
        TOK[BPE Tokenizer\n77-token max]
        TE[Transformer\nEncoder\n12 layers]
        EOT[EOT Token\n= text embedding]
        TOK --> TE --> EOT
    end

    subgraph Alignment ["Embedding Alignment"]
        IL[Linear projection\n→ 512-dim space]
        TL[Linear projection\n→ 512-dim space]
        NORM[L2 Normalize]
    end

    subgraph Loss ["Contrastive Loss"]
        SIM["N×N Similarity Matrix\ncosine_similarity(img_i, txt_j)"]
        TARGET["Target: diagonal = 1\noff-diagonal = 0"]
        CE["Cross-entropy loss\n(both row-wise and column-wise)"]
        SIM --> TARGET --> CE
    end

    Input --> ImagePath
    Input --> TextPath
    CLS --> IL --> NORM --> SIM
    EOT --> TL --> NORM --> SIM
```

### CLIP Zero-Shot Classification

```mermaid
flowchart LR
    subgraph Inference
        IMG[New Image\nnever seen before]
        LABELS["Label set:\n'a photo of a cat'\n'a photo of a dog'\n'a photo of a car'"]

        IE2[Image Encoder]
        TE2[Text Encoder\n× 3 labels]

        IV[Image Vector\n512-dim]
        TV["Text Vectors\n[cat_vec, dog_vec, car_vec]"]

        COS["Cosine Similarity\n[0.87, 0.12, 0.04]"]
        PRED["Prediction: 'cat'\n(highest similarity)"]

        IMG --> IE2 --> IV --> COS
        LABELS --> TE2 --> TV --> COS
        COS --> PRED
    end
```

### Key CLIP Variants

| Model | Image encoder | Embedding dim | Params | Notes |
|-------|--------------|---------------|--------|-------|
| ViT-B/32 | ViT-Base, 32×32 patches | 512 | 151M | Fastest |
| ViT-B/16 | ViT-Base, 16×16 patches | 512 | 150M | Better detail |
| ViT-L/14 | ViT-Large, 14×14 patches | 768 | 428M | Most accurate |
| ViT-L/14@336 | ViT-Large, higher res | 768 | 428M | Higher resolution |

---

## LLaVA Architecture

### LLaVA-1.0: The Minimal Bridge

The original LLaVA paper showed that a single linear projection layer is sufficient to connect a visual encoder to an LLM effectively — you don't need a complex cross-attention mechanism.

```mermaid
flowchart TB
    subgraph Stage1 ["Stage 1: Projection Pre-training (feature alignment)"]
        I1[Image\n224×224]
        VE1[CLIP ViT-L/14\nFROZEN]
        FV1["Visual Features\n256 × 1024-dim"]
        LP1[Linear Projection W\nTRAINED\n1024 → 4096-dim]
        VT1["Visual Tokens\n256 × 4096-dim\n(matches LLaMA token dim)"]
        LLM1[LLaMA/Vicuna\nFROZEN]

        I1 --> VE1 --> FV1 --> LP1 --> VT1
        VT1 --> LLM1
        LLM1 --> OUT1["Caption output\n(image-text pairs from CC3M)"]
    end
```

```mermaid
flowchart TB
    subgraph Stage2 ["Stage 2: Visual Instruction Tuning"]
        I2[Image]
        VE2[CLIP ViT-L/14\nFROZEN]
        LP2[Linear Projection\nTRAINED]
        LLM2[LLaMA/Vicuna\nFINE-TUNED]

        I2 --> VE2 --> LP2
        Q["User instruction:\n'What is in this image?'\n'Describe what's unusual here'\n'Read the text visible in the image'"]
        Q --> LLM2
        LP2 --> LLM2
        LLM2 --> ANS[Instruction-following response]
    end
```

### LLaVA-1.5 Improvements

LLaVA-1.5 upgraded the projection layer from a single linear layer to a 2-layer MLP and used a better base LLM (Vicuna 1.5 / Mistral), significantly improving performance while keeping the same elegant architecture.

```mermaid
flowchart LR
    VE[CLIP ViT-L/14\n336px\nFROZEN] --> FV["Visual features\n576 patches × 1024-dim"]
    FV --> MLP["2-layer MLP\nGELU activation\nTRAINED\n1024 → 4096"]
    MLP --> VT[Visual tokens]
    TK[Text tokens] --> CONCAT[Concatenated\nsequence]
    VT --> CONCAT
    CONCAT --> LLM2["Vicuna-7B or 13B\nor Mistral-7B\nFINE-TUNED with LoRA"]
    LLM2 --> RESP[Response]
```

### LLaVA-1.6 (LLaVA-NeXT): High-Resolution Support

LLaVA-1.6 added a dynamic resolution scheme: instead of downscaling all images to 336px, images are split into tiles at the native resolution, allowing much better reading of fine text and small details.

```mermaid
flowchart TB
    HighRes[High-res image\ne.g. 1344×336]
    Tile["Split into tiles\n+ 1 low-res overview"]
    T1[Tile 1\n336×336] --> CLIP1[CLIP Encoder]
    T2[Tile 2\n336×336] --> CLIP2[CLIP Encoder]
    T3[Tile 3\n336×336] --> CLIP3[CLIP Encoder]
    T4[Tile 4\n336×336] --> CLIP4[CLIP Encoder]
    Overview[Low-res\noverview] --> CLIPS[CLIP Encoder]
    CLIP1 & CLIP2 & CLIP3 & CLIP4 & CLIPS --> Concat[Concatenate all\nvisual tokens]
    HighRes --> Tile
    Tile --> T1 & T2 & T3 & T4 & Overview
    Concat --> LLM3[LLM → response]
```

---

## CLIP vs LLaVA Side-by-Side

```mermaid
flowchart LR
    subgraph CLIP_box ["CLIP"]
        direction TB
        C_IE[Image Encoder] --> C_IV[512-dim vector]
        C_TE[Text Encoder] --> C_TV[512-dim vector]
        C_IV & C_TV --> C_SIM[Cosine similarity score]
        C_SIM --> C_OUT["0.87 (high = match)"]
    end

    subgraph LLaVA_box ["LLaVA"]
        direction TB
        L_IE[CLIP Image Encoder\nfrozen] --> L_IV[Visual patch tokens]
        L_IV --> L_PL[Projection Layer]
        L_PL --> L_LLM[Language Model]
        L_TQ[Text prompt] --> L_LLM
        L_LLM --> L_OUT["'This image shows a golden\nretriever running on a beach...'"]
    end
```

---

## BLIP-2: An Alternative Connector Architecture

BLIP-2 uses a **Q-Former** (Querying Transformer) instead of a simple projection layer. The Q-Former has learned query tokens that attend to the visual encoder's output and extract the most task-relevant visual features. This provides a more expressive bridge than a linear projection.

```mermaid
flowchart TB
    IMG3[Image] --> FE[Frozen Image Encoder\ne.g. ViT-G/14]
    FE --> VF[Visual Features\n1408-dim × 257 tokens]

    subgraph QFormer ["Q-Former (32 learnable query tokens)"]
        QT[Query Tokens\n32 × 768-dim] --> SA[Self-Attention\namong queries]
        SA --> CA2[Cross-Attention\nqueries attend to\nvisual features]
        CA2 --> QOut[Enriched query\nrepresentations\n32 × 768-dim]
    end

    VF --> CA2
    QOut --> LP3[Linear projection\n768 → LLM dim]
    LP3 --> FLM[Frozen LLM\nOPT / FlanT5]
    FLM --> RESP3[Response]
```

The advantage: only 32 query tokens go to the LLM (vs 256 in LLaVA), drastically reducing the visual token count and thus computational cost.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |

⬅️ **Prev:** [01 — Multimodal Fundamentals](../01_Multimodal_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — Image Understanding](../03_Image_Understanding/Theory.md)
