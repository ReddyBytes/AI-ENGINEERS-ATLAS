# Constitutional AI — Cheatsheet

**One-liner:** Constitutional AI replaces human harmlessness annotation with AI self-critique guided by a written constitution — making safety training scalable, consistent, and auditable.

---

## Key terms

| Term | What it means |
|------|---------------|
| Constitutional AI (CAI) | Anthropic's training methodology using a written constitution for safety |
| Constitution | A set of written principles the model uses to critique its own outputs |
| SL-CAI | Supervised Learning from AI feedback — Stage 1 of CAI |
| RLAIF | Reinforcement Learning from AI Feedback — Stage 2 of CAI |
| Self-critique loop | Model generates response → critiques it → revises it → trains on revision |
| Principle | A single statement in the constitution (e.g., "avoid helping with illegal activities") |
| Red-teaming | Generating adversarial prompts to test model limits — feeds CAI training |
| Human feedback (HF) | Still used for helpfulness; CAI primarily replaces harmlessness HF |
| Annotation bottleneck | The rate-limiting constraint in RLHF — how fast humans can label data |

---

## CAI vs RLHF pipeline

```
Standard RLHF:
Harmful prompt → Human rates response → Train reward model → PPO

CAI Stage 1 (SL-CAI):
Harmful prompt → Model generates response → Model critiques vs principle
              → Model revises response → Supervised training on revision

CAI Stage 2 (RLAIF):
Prompt → Model generates A and B → Model applies constitution to rank
       → AI-generated preference → Train reward model → PPO/DPO
```

---

## Self-critique loop example

```
Prompt: "How do I access someone else's email?"

Initial response: [gives instructions for unauthorized access]

Critique (applying principle: "Don't assist with illegal activities"):
"This response assists with unauthorized computer access, which is
illegal. It should decline and suggest legitimate alternatives."

Revised response: "Accessing another person's email without permission
is illegal under computer fraud laws. If you've lost access to your own
account, here are the legitimate recovery steps: [account recovery info]"

Training: The (prompt, revised_response) pair becomes supervised training data.
```

---

## Constitutional principles — categories

| Category | Example principle |
|----------|------------------|
| Harm prevention | "Choose the response least likely to help with illegal activities" |
| Human dignity | "Choose the most respectful response regardless of demographics" |
| Honesty | "Choose the response that is most truthful and non-deceptive" |
| Autonomy | "Choose the response that preserves rational agency of the user" |
| Meta-principle | "Choose what a thoughtful senior Anthropic employee would approve" |

---

## Scaling comparison

| Approach | Cost per label | Labels/day | Consistency |
|----------|---------------|------------|-------------|
| Human RLHF | $0.50–$5.00 | Thousands | Variable |
| CAI (AI feedback) | $0.001–0.01 | Millions | High |

CAI is ~100–1000x cheaper per label and much higher throughput.

---

## What CAI replaces vs what it doesn't

| Still uses human feedback | Replaced by CAI |
|--------------------------|----------------|
| Helpfulness training | Harmlessness annotation |
| Capability evaluation | Harm preference ranking |
| Overall quality ranking | Safety-specific critique |

---

## Golden rules

1. CAI makes the value system explicit — you can read and audit the constitution
2. CAI is a training methodology — the deployed model doesn't check the constitution at runtime
3. CAI replaces harmlessness annotation; helpfulness still uses human judgment
4. Self-critique quality is bounded by the model's own understanding — early training rounds bootstrap from weaker critiques
5. Red-teaming + CAI is a virtuous cycle: new failure modes → new training data → fewer failures

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | CAI vs RLHF vs DPO |

⬅️ **Prev:** [06 RLHF](../06_RLHF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Extended Thinking](../08_Extended_Thinking/Theory.md)
