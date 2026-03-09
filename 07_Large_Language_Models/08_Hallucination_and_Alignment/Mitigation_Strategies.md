# Hallucination Mitigation Strategies

A practical guide to reducing hallucination in production LLM applications. For each strategy: what it does, when to use it, limitations, and implementation notes.

---

## Overview: choose your strategy

| Strategy | Best for | Complexity | Effectiveness |
|----------|---------|-----------|---------------|
| RAG | Factual Q&A, document-based tasks | Medium | High |
| Lower temperature | Structured/factual output | Low | Moderate |
| Chain-of-thought | Reasoning tasks | Low | Medium-High |
| Citation grounding | Any factual claim | Low | High |
| Self-consistency | Complex reasoning, math | Medium | High |
| Human review checkpoints | High-stakes outputs | Low (process) | Very High |
| Confidence elicitation | All uses | Low | Moderate |
| Iterative refinement | Long-form content | Medium | Medium |

---

## Strategy 1: RAG (Retrieval-Augmented Generation)

### What it does
Instead of having the model answer from memory (parametric knowledge), retrieve relevant documents and insert them into the context. The model extracts answers from actual source material rather than generating from statistical patterns.

### The setup
```
User query → Embedding model → Vector database search → Top-k documents
                                                          ↓
                              LLM context = [System prompt + Documents + Query]
                                                          ↓
                                               Grounded response
```

### System prompt for RAG grounding
```
You are a helpful assistant. Answer questions based ONLY on the information
provided in the context documents below.

If the answer is not contained in the provided documents, say:
"I don't have information about this in my available documents."

Do not use information from outside the provided context.

Context documents:
[RETRIEVED DOCUMENTS]

User question: {question}
```

### When to use
- Your application requires factual accuracy on specific domain knowledge
- You have a well-maintained knowledge base or document store
- Questions are about the contents of specific documents
- The domain changes frequently (current events, product updates, policies)

### Limitations
- Retrieval can fail (semantic mismatch, paraphrase, multi-hop questions)
- Models can still hallucinate details not in retrieved documents
- Quality depends on knowledge base quality — garbage in, garbage out
- Adds latency (retrieval step + larger context = slower generation)
- Expensive to build and maintain the vector database

### Effectiveness boost: source citations
```
Answer the question below using only the provided documents.
For every factual claim you make, cite the specific document and passage:
Format: [Source: Document N, paragraph X]

If you are not sure, say "I'm not confident about this based on the provided sources."
```

---

## Strategy 2: Lower Temperature

### What it does
Temperature controls sampling randomness. At temperature=0 (greedy), the model always picks the highest-probability token. This makes outputs more deterministic and typically more conservative.

### When to use
- Generating structured data: JSON, CSV, code
- Factual Q&A where exact phrasing doesn't matter
- Tasks where consistency is important
- Medical or legal contexts where accuracy > creativity

### How to implement
```python
# API call with low temperature
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    temperature=0.1,   # Low temperature for factual output
    messages=[{"role": "user", "content": your_prompt}]
)
```

### Why it's limited
Lower temperature doesn't prevent hallucination — it makes hallucinations more consistent. If the model's most probable completion is wrong, it will be confidently and consistently wrong. Temperature=0 on "Who won the 1987 World Series?" will confidently give the wrong answer if the model doesn't know it — every single time.

Use low temperature to reduce creative variability, not as a hallucination fix.

---

## Strategy 3: Chain-of-Thought Prompting

### What it does
Forces the model to reason step-by-step before giving a final answer. This makes intermediate reasoning visible, catchable, and correctable. It improves accuracy on complex tasks by preventing the model from jumping to the most statistically likely conclusion.

### Implementation
```
Basic CoT trigger:
"Think through this step by step before answering."

Zero-shot CoT:
"Let's think step by step."  (add this to any prompt)

Few-shot CoT (include reasoning examples):
Q: If a train leaves at 9 AM and arrives at 2 PM, how long is the journey?
A: Let me work through this step by step.
   Start time: 9 AM
   End time: 2 PM
   From 9 AM to 12 PM = 3 hours
   From 12 PM to 2 PM = 2 hours
   Total: 3 + 2 = 5 hours
   The journey is 5 hours.

Q: [your question]
A: Let me work through this step by step.
```

### When to use
- Math word problems
- Multi-step reasoning
- Code generation (reason about the algorithm before writing)
- Tasks where common-sense shortcuts lead to wrong answers
- Any task where the answer requires more than simple recall

### Limitations
- Doesn't help with pure factual recall (step-by-step doesn't reveal facts the model doesn't have)
- Increases token count and cost
- Model can produce plausible-sounding but incorrect reasoning steps
- On simple tasks, CoT adds overhead without benefit

---

## Strategy 4: Citation Grounding

### What it does
Require the model to quote specific passages from provided documents for every factual claim. Makes hallucination detectable: either the quote exists in the source, or it doesn't.

### System prompt template
```
You are a research assistant. Your role is to answer questions about the
provided documents.

Rules:
1. Every factual claim MUST be supported by a direct quote from the documents
2. Format quotes as: "Quote text" [Document: {doc_name}, Page/Section: {location}]
3. If you cannot find a direct quote to support a claim, do not make the claim
4. If the documents don't answer the question, say: "The provided documents
   don't contain information about this."

Documents:
{documents}

Question: {question}
```

### When to use
- Legal document review
- Medical literature summarization
- Contract analysis
- Any high-stakes domain where verifiability matters
- Compliance workflows where traceability is required

### Limitations
- Only works when documents are in context (RAG or direct insertion)
- Model can misquote or slightly alter quotes (still verify the source!)
- Increases output length significantly
- Works poorly for synthesis tasks that require combining information

---

## Strategy 5: Self-Consistency

### What it does
Generate the same question multiple times (usually 5–10 times) with sampling enabled (temperature > 0). For each generation, extract the final answer. Take the majority vote.

The insight: hallucinations are errors — they're unlikely to be the same error every time. Correct answers, being grounded in something, are more likely to be consistent across samples.

### Implementation
```python
import anthropic
from collections import Counter

client = anthropic.Anthropic()

def self_consistent_answer(question, n_samples=5):
    answers = []

    for i in range(n_samples):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            temperature=0.8,    # Some temperature to get variation
            messages=[{
                "role": "user",
                "content": f"{question}\n\nThink step by step. End with 'Final answer: [answer]'"
            }]
        )

        text = response.content[0].text
        # Extract the final answer
        if "Final answer:" in text:
            answer = text.split("Final answer:")[-1].strip()
            answers.append(answer)

    # Take majority vote
    if answers:
        vote_counts = Counter(answers)
        majority_answer = vote_counts.most_common(1)[0][0]
        confidence = vote_counts[majority_answer] / len(answers)
        return majority_answer, confidence
    return None, 0.0

answer, confidence = self_consistent_answer(
    "What is 15% of $340? Show your work."
)
print(f"Answer: {answer}")
print(f"Confidence: {confidence:.0%}")
```

### When to use
- Math problems where exact answers are expected
- Yes/no questions where hallucination rate matters
- Multiple choice questions
- Any task where you can extract a discrete answer

### Limitations
- Expensive: n times the cost and latency
- Doesn't work for open-ended generation (no "majority" for free-form text)
- Majority vote is still wrong if all paths lead to the same hallucination
- Diminishing returns — 5 samples usually captures most of the benefit

---

## Strategy 6: Human Review Checkpoints

### What it does
Insert human review steps at critical points in the LLM pipeline. The LLM generates; a human verifies before the output goes anywhere consequential.

### When to use
- Medical diagnosis support tools
- Legal document generation
- Financial analysis and recommendations
- Customer-facing content for regulated industries
- Any output that can cause real harm if wrong

### Process design
```
Level 1 — Spot check:
  Random sample (5-10%) of outputs reviewed by domain expert
  Track accuracy rate; alert when it drops below threshold

Level 2 — Critical path review:
  All high-stakes outputs reviewed before delivery
  e.g., medical records, legal filings, financial reports

Level 3 — Expert audit:
  Periodic systematic audit of all outputs in a category
  Structured feedback fed back into prompt improvements or fine-tuning
```

### Limitations
- Expensive and slow (human time)
- Doesn't scale with output volume
- Humans have their own biases and miss errors too
- Not feasible for real-time applications

Used for high-stakes, low-volume applications where the cost of a mistake is very high.

---

## Strategy 7: Confidence Elicitation

### What it does
Prompt the model to explicitly rate its own confidence, then act differently based on that rating.

### System prompt approach
```
After providing your answer, add:
- CONFIDENCE: [HIGH / MEDIUM / LOW]
- REASON: [brief explanation of why you're confident or uncertain]

HIGH = you're very sure this is correct and would stake your reputation on it
MEDIUM = you believe this is correct but would recommend verification
LOW = you're guessing based on limited information; definitely verify
```

### Decision logic
```python
def handle_response_with_confidence(response_text):
    if "CONFIDENCE: HIGH" in response_text:
        return response_text  # Use directly
    elif "CONFIDENCE: MEDIUM" in response_text:
        # Add disclaimer or route to verification
        return response_text + "\n\n[Note: Recommend verifying this information]"
    elif "CONFIDENCE: LOW" in response_text:
        # Route to human review or return "I don't know"
        return "I'm not confident in my answer on this topic. Please consult a specialist."
```

### Limitations
- Models are poorly calibrated — they may say HIGH confidence while being wrong
- Models may say HIGH confidence for everything (sycophancy)
- Requires careful few-shot examples to calibrate the confidence scale
- Not reliable as a standalone solution; use as one signal among many

---

## Strategy 8: Iterative Refinement

### What it does
Generate a draft, then run a separate check/critique pass, then refine. Breaks the single-pass generation into generate → verify → revise.

### Implementation pattern
```python
def generate_with_refinement(question, context_docs):
    # Step 1: Initial answer
    initial_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Based on these documents, answer: {question}\n\nDocuments: {context_docs}"
        }]
    )

    draft = initial_response.content[0].text

    # Step 2: Self-critique
    critique_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""
Review this answer for factual accuracy and identify any claims that might be wrong or unsupported:

Question: {question}
Answer: {draft}
Source documents: {context_docs}

List any potential errors or unsupported claims. If everything looks correct, say "No issues found."
"""
        }]
    )

    critique = critique_response.content[0].text

    # Step 3: Revise if issues found
    if "No issues found" not in critique:
        final_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""
Original answer: {draft}
Issues identified: {critique}

Please revise the answer to fix the identified issues.
Only make claims that are clearly supported by the source documents.

Source documents: {context_docs}
"""
            }]
        )
        return final_response.content[0].text

    return draft
```

### When to use
- Long-form content where multiple rounds of review are worth the cost
- High-stakes outputs where cost of error is very high
- When you have time and budget for multi-pass generation

### Limitations
- 2-3x more expensive and slower
- The critique pass can also hallucinate
- Diminishing returns after 2-3 refinement rounds
- Not suitable for real-time applications

---

## Combining strategies: production recommendations

**For a customer-facing Q&A bot:**
```
RAG + citation grounding + lower temperature + confidence elicitation
```

**For a code generation tool:**
```
Chain-of-thought + lower temperature + unit test execution (run the code!)
```

**For a medical or legal assistant:**
```
RAG + citation grounding + human review checkpoints + iterative refinement
```

**For a math tutoring app:**
```
Chain-of-thought + self-consistency + show your work
```

**The most important principle**: The only way to know if your mitigation is working is to test systematically. Build a hallucination test suite for your specific domain and run it regularly.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Mitigation_Strategies.md** | ← you are here |

⬅️ **Prev:** [07 Context Windows and Tokens](../07_Context_Windows_and_Tokens/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Using LLM APIs](../09_Using_LLM_APIs/Theory.md)