# Hallucination and Alignment — Cheatsheet

**One-liner:** Hallucination is when LLMs confidently generate false information because they're pattern-matchers not fact-checkers; alignment is the challenge of making AI reliably helpful, safe, and honest.

---

## Key terms

| Term | What it means |
|------|---------------|
| Hallucination | Generating false information presented with the same confidence as true information |
| Factual hallucination | Incorrect facts stated as true |
| Entity hallucination | Making up names, papers, URLs, people, organizations |
| Attribution hallucination | Inventing or misattributing quotes and sources |
| Grounding | Anchoring model outputs to verified source documents |
| Alignment | Making AI behavior match human values: helpful, harmless, honest |
| HHH | Helpful, Harmless, Honest — Anthropic's alignment framework |
| Calibration | Model's uncertainty claims should match its actual accuracy |
| Sycophancy | Model agrees with user even when user is wrong |
| Constitutional AI | Anthropic's approach: align using written principles + AI feedback |
| RLHF | Alignment via reinforcement learning from human preference comparisons |
| RAG | Retrieval-Augmented Generation — ground answers in retrieved documents |
| Chain-of-thought | Force model to reason step-by-step; reduces hallucination on complex tasks |
| Self-consistency | Sample multiple times, take majority vote — errors don't all go same direction |
| Citation grounding | Require the model to cite specific documents for every claim |

---

## Types of hallucination

| Type | Example | How to detect |
|------|---------|---------------|
| Factual | "Einstein won Nobel Prize in 1912" (was 1921) | Fact-check with reliable source |
| Entity | Made-up paper title, fake URL | Google the citation |
| Attribution | Wrong person quoted | Verify quote origin |
| Logical | Flawed reasoning leading to wrong conclusion | Step-by-step verification |
| Temporal | Using outdated info as if current | Check dates against current sources |
| Self | Model wrong about itself | Check model card / documentation |

---

## Why models hallucinate

| Root cause | Explanation |
|------------|-------------|
| Pattern matching, not lookup | Models generate probable text, not verified facts |
| No uncertainty signal | Training doesn't teach "I don't know" well |
| Training data ambiguity | If training data was contradictory, model may average or pick randomly |
| Fluency bias | Confident, fluent text had higher reward than hedged text during RLHF |
| Knowledge gaps | Topics underrepresented in training data → model fills gaps |

---

## Mitigation strategies at a glance

| Strategy | How it helps | Complexity |
|----------|-------------|-----------|
| RAG | Ground answers in retrieved docs | Medium |
| Lower temperature | More predictable, less creative outputs | Low |
| Chain-of-thought prompting | Forces explicit reasoning steps | Low |
| Citation grounding | Require document quotes | Low-Medium |
| Self-consistency | Vote across multiple samples | Medium |
| Fine-tune on factual tasks | Improves calibration | High |
| Human review checkpoints | Catches errors before deployment | Low (process) |
| Confidence elicitation | Ask model to rate its own certainty | Low |

---

## The alignment challenge

```
Helpfulness ←────────────────→ Harmlessness
     ↑                              ↑
  "Tell me how                  "I cannot
  to do X"                      provide that"

     Both extremes are failures.
     Alignment is finding the right balance.
```

---

## Constitutional AI principles (example subset)

```
1. Choose the response least likely to contain harmful content
2. Choose the response that is most honest
3. Choose the response that is most helpful to the user
4. Choose the response that is not sycophantic
5. Choose the response a thoughtful person would be proud of
```

---

## Golden rules

1. LLMs are fluent, not factual. Never trust an LLM answer on high-stakes facts without verification.
2. Hallucination is not a bug to fix — it's a fundamental property of the architecture. Mitigate, don't eliminate.
3. RAG is the best practical mitigation. Ground responses in documents you trust.
4. Temperature=0 doesn't prevent hallucination. Low temp just makes hallucinations more consistent.
5. Asking "are you sure?" can reduce hallucination on some models (forces reconsideration).
6. Alignment is a spectrum, not a binary. Every model has alignment strengths and weaknesses.
7. The only way to know if a model hallucinates on your use case is to test systematically.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Mitigation_Strategies.md](./Mitigation_Strategies.md) | Hallucination mitigation strategies |

⬅️ **Prev:** [07 Context Windows and Tokens](../07_Context_Windows_and_Tokens/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Using LLM APIs](../09_Using_LLM_APIs/Theory.md)
