# 06 — Transformers

In 2017, a Google paper called "Attention is All You Need" changed everything. Before it, NLP models processed text word by word, struggling to remember context from earlier in long sequences. The transformer threw out that approach entirely and replaced it with attention — the ability to look at any word in the sequence at any time.

## What this section covers

| Topic | What you'll learn |
|---|---|
| 01 Sequence Models Before Transformers | RNNs, LSTMs, and why they weren't enough |
| 02 Attention Mechanism | How attention lets models focus on relevant context |
| 03 Self-Attention | How words attend to each other in the same sequence |
| 04 Multi-Head Attention | Running multiple attention heads in parallel |
| 05 Positional Encoding | Giving the model a sense of word order |
| 06 Transformer Architecture | The full encoder-decoder picture |
| 07 Encoder-Decoder Models | BERT vs GPT vs T5 — which to use when |
| 08 BERT | Bidirectional encoding and masked language modeling |
| 09 GPT | Autoregressive generation and the GPT family |
| 10 Vision Transformers | Applying transformers to images |

## Why transformers replaced RNNs

RNNs processed sequences step by step. To understand word 100, you had to pass information through 99 steps — and gradients vanished along the way. LSTMs helped but still had limits.

Transformers process the entire sequence at once. Every word can directly attend to every other word in a single step. No sequential bottleneck. No vanishing gradient through time. Parallelizable on modern hardware.

Every major AI model today — GPT-4, Claude, Gemini, BERT, DALL-E, Stable Diffusion — is built on the transformer architecture.

## Prerequisites

- Complete 05_NLP_Foundations first
- Comfort with vectors and matrices helps (Section 01_Math_for_AI)
