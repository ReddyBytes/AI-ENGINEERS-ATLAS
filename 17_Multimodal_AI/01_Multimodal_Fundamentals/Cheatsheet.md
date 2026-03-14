# Multimodal AI Fundamentals — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Modality** | A type of data: text, image, audio, video, structured |
| **Multimodal AI** | AI that processes or generates more than one modality |
| **Encoder** | Neural network that converts raw input into a vector embedding |
| **Fusion** | The step where embeddings from different modalities are combined |
| **Early fusion** | Combine raw inputs before encoding |
| **Late fusion** | Combine final predictions after separate encoding |
| **Cross-attention fusion** | Text tokens attend to image tokens (most powerful approach) |
| **Contrastive loss** | Training objective: push matching pairs together, mismatched apart |
| **Projection layer** | Small network that maps one embedding space to another |
| **Joint training** | Training both encoders together so their spaces align |
| **CLIP** | OpenAI's model: shared image+text embedding space via contrastive learning |
| **VLM** | Vision-Language Model: processes both image and text |
| **ViT** | Vision Transformer: encodes images as sequences of patches |

---

## Modality Types at a Glance

| Modality | Input format | Key encoder | Key use |
|----------|-------------|-------------|---------|
| Text | Tokens | BERT, GPT | Reasoning, generation |
| Image | Patches | ViT, CLIP | Visual Q&A, classification |
| Audio | Spectrogram | Whisper encoder | Speech-to-text, music |
| Video | Frame sequence | Video transformer | Summarization, detection |
| Structured | Rows/columns | Tabular encoder | Data analysis |

---

## Three Fusion Strategies

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| Early fusion | Concat raw inputs | Simple | Loses modality structure |
| Late fusion | Combine predictions | Easy, modular | Modalities can't interact |
| Cross-attention | Queries from one attend to keys/values of other | Most powerful | Complex, expensive |

---

## Real Systems Quick Reference

| System | In | Out | Made by |
|--------|-----|-----|---------|
| Claude Vision | Image + text | Text | Anthropic |
| GPT-4V | Image + text | Text | OpenAI |
| Gemini 1.5 Pro | Image/audio/video/text | Text | Google |
| DALL-E 3 | Text | Image | OpenAI |
| Whisper | Audio | Text | OpenAI |
| ElevenLabs TTS | Text | Audio | ElevenLabs |
| Stable Diffusion | Text (+image) | Image | Stability AI |
| LLaVA | Image + text | Text | Open source |

---

## When to Use vs When NOT to Use Vision

| Use vision when | Skip vision when |
|-----------------|-----------------|
| Input literally contains an image | All information is in text already |
| You need to read text from a document/screenshot | Adding vision just for novelty |
| Visual features (layout, color, shape) matter | Latency or cost is critical |
| User uploads a photo with their question | Task is purely mathematical or logical |

---

## Cost Rule of Thumb

- Text tokens: ~$0.003 per 1K tokens (varies by model)
- Image tokens: ~$0.01–0.04 per image depending on resolution and model
- Vision calls are typically **3–10x more expensive** than text-only
- Always estimate cost before building vision-heavy pipelines

---

## Golden Rules

1. Always preprocess images (resize, normalize) before sending to a model
2. Match the resolution to the task — high detail costs more tokens
3. Late fusion for independent tasks; cross-attention for tasks needing interaction
4. Test edge cases: small text, dark images, diagrams, charts
5. When in doubt, describe the image in text and compare — if text is enough, skip vision

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [Section 16 — Deployment](../../16_Deployment/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Vision Language Models](../02_Vision_Language_Models/Theory.md)
