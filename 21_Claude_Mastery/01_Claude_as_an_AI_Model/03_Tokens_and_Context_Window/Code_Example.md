# Tokens and Context Window — Code Examples

Practical code for token counting, context management, and handling at-limit behavior using the Anthropic Python SDK.

---

## Setup

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
```

---

## 1 — Count tokens before making a call

Use `count_tokens` to pre-flight check before an expensive generation request.

```python
def count_tokens_before_call(system_prompt: str, messages: list[dict]) -> int:
    """Count tokens without generating output."""
    response = client.messages.count_tokens(
        model="claude-sonnet-4-6",
        system=system_prompt,
        messages=messages
    )
    return response.input_tokens


# Example
system = "You are a helpful assistant specializing in Python."
messages = [
    {"role": "user", "content": "Explain list comprehensions with examples."}
]

token_count = count_tokens_before_call(system, messages)
print(f"Input tokens: {token_count}")

# Pre-flight guard
MAX_INPUT = 180_000  # leave room for output
if token_count > MAX_INPUT:
    raise ValueError(f"Input too large: {token_count} tokens (limit: {MAX_INPUT})")
```

---

## 2 — Check stop_reason after every call

Never ignore stop_reason — truncated output is a silent failure.

```python
def safe_generate(system: str, messages: list[dict], max_tokens: int = 2048) -> str:
    """Generate and handle truncation."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        system=system,
        messages=messages,
        max_tokens=max_tokens
    )
    
    if response.stop_reason == "max_tokens":
        # Output was truncated
        partial = response.content[0].text
        print(f"WARNING: Output truncated at {max_tokens} tokens.")
        print(f"Partial output ({len(partial)} chars): {partial[:100]}...")
        # Option 1: raise an error
        # raise RuntimeError("Response truncated — increase max_tokens")
        # Option 2: continue generation
        return _continue_generation(system, messages, partial, max_tokens)
    
    return response.content[0].text


def _continue_generation(system: str, messages: list[dict], 
                          partial: str, max_tokens: int) -> str:
    """Continue a truncated generation."""
    # Add the partial response as an assistant turn
    new_messages = messages + [
        {"role": "assistant", "content": partial},
        {"role": "user", "content": "Please continue exactly where you left off."}
    ]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        system=system,
        messages=new_messages,
        max_tokens=max_tokens
    )
    return partial + response.content[0].text
```

---

## 3 — Token-aware conversation history management

Keep conversation history from overflowing the context window.

```python
class TokenAwareConversation:
    """Manages a conversation that stays within token limits."""
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        context_limit: int = 200_000,
        max_output: int = 4_096,
        safety_buffer: int = 5_000
    ):
        self.model = model
        self.limit = context_limit - max_output - safety_buffer
        self.messages: list[dict] = []
        self.system = ""
    
    def set_system(self, system_prompt: str):
        self.system = system_prompt
    
    def _count_current_tokens(self) -> int:
        if not self.messages:
            return 0
        r = client.messages.count_tokens(
            model=self.model,
            system=self.system,
            messages=self.messages
        )
        return r.input_tokens
    
    def _compress_history(self):
        """Summarize old turns to free up context."""
        if len(self.messages) < 4:
            return  # nothing to compress
        
        # Keep only last 2 turns, summarize the rest
        old_turns = self.messages[:-4]
        recent_turns = self.messages[-4:]
        
        summary_resp = client.messages.create(
            model="claude-haiku-4-5",  # cheap model for summarization
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize this conversation in 2-3 sentences, "
                        "capturing the key facts and decisions:\n\n"
                        + "\n".join(
                            f"{m['role'].upper()}: {m['content']}"
                            for m in old_turns
                        )
                    )
                }
            ]
        )
        summary = summary_resp.content[0].text
        
        # Replace old turns with summary
        self.messages = [
            {"role": "user", "content": f"[Previous conversation summary: {summary}]"},
            {"role": "assistant", "content": "Understood. I have the context from our previous discussion."},
            *recent_turns
        ]
        print(f"History compressed. {len(old_turns)} turns → 1 summary.")
    
    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        
        # Compress if approaching limit
        current_tokens = self._count_current_tokens()
        if current_tokens > self.limit * 0.8:
            print(f"Approaching limit ({current_tokens}/{self.limit}). Compressing...")
            self._compress_history()
        
        response = client.messages.create(
            model=self.model,
            system=self.system,
            messages=self.messages,
            max_tokens=4_096
        )
        
        assistant_reply = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply


# Usage
conv = TokenAwareConversation()
conv.set_system("You are a helpful coding assistant.")
print(conv.chat("What is a Python decorator?"))
print(conv.chat("Can you show me a practical example?"))
```

---

## 4 — Chunk a large document for processing

Split documents that exceed the context window into manageable pieces.

```python
def chunk_document_by_tokens(
    text: str,
    max_tokens_per_chunk: int = 50_000,
    overlap_tokens: int = 500,
    model: str = "claude-haiku-4-5"
) -> list[str]:
    """
    Split text into chunks that fit within token limits.
    Uses word boundaries for splitting, then validates with token count.
    """
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        # Estimate initial chunk size from word count
        estimated_words = int(max_tokens_per_chunk * 0.75)
        end = min(start + estimated_words, len(words))
        chunk = " ".join(words[start:end])
        
        # Validate and adjust with actual token count
        while end > start:
            actual_tokens = client.messages.count_tokens(
                model=model,
                messages=[{"role": "user", "content": chunk}]
            ).input_tokens
            
            if actual_tokens <= max_tokens_per_chunk:
                break
            # Too long: reduce by 10%
            end = int(start + (end - start) * 0.9)
            chunk = " ".join(words[start:end])
        
        chunks.append(chunk)
        
        # Overlap: step back by overlap_tokens worth of words
        overlap_words = int(overlap_tokens * 0.75)
        start = end - overlap_words
    
    return chunks


def process_large_document(document: str, question: str) -> str:
    """Process a document larger than the context window."""
    chunks = chunk_document_by_tokens(document)
    print(f"Split into {len(chunks)} chunks.")
    
    # Get a partial answer from each chunk
    partial_answers = []
    for i, chunk in enumerate(chunks):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"Document chunk {i+1}/{len(chunks)}:\n\n{chunk}\n\n"
                    f"Question: {question}\n\n"
                    "Answer based only on this chunk. If the answer isn't here, say 'Not in this chunk'."
                )
            }]
        )
        partial_answers.append(response.content[0].text)
    
    # Synthesize all partial answers
    synthesis_prompt = (
        "I asked the same question about different sections of a long document. "
        "Here are the partial answers:\n\n"
        + "\n\n---\n\n".join(
            f"Chunk {i+1}: {ans}" 
            for i, ans in enumerate(partial_answers)
        )
        + f"\n\nOriginal question: {question}\n\n"
        "Please synthesize a complete answer from all the relevant information above."
    )
    
    final = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )
    return final.content[0].text
```

---

## 5 — Token cost estimator

Estimate API call cost before making expensive requests.

```python
# Approximate pricing (mid-2025) per million tokens
PRICING = {
    "claude-haiku-4-5": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-opus-4": {"input": 15.00, "output": 75.00},
}

def estimate_cost(
    model: str,
    input_tokens: int,
    expected_output_tokens: int
) -> float:
    """Estimate cost in USD for a Claude API call."""
    rates = PRICING.get(model, PRICING["claude-sonnet-4-6"])
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (expected_output_tokens / 1_000_000) * rates["output"]
    return input_cost + output_cost


def compare_model_costs(input_tokens: int, output_tokens: int):
    """Compare cost across all Claude models."""
    print(f"\nCost comparison for {input_tokens:,} input + {output_tokens:,} output tokens:")
    print("-" * 55)
    for model in PRICING:
        cost = estimate_cost(model, input_tokens, output_tokens)
        print(f"  {model:<30} ${cost:.4f}")
    print()


# Example: analyzing a 50-page document (~20k tokens) with 500-token response
compare_model_costs(input_tokens=20_000, output_tokens=500)

# Example: daily cost estimate for a chatbot
# 1000 users × 20 turns × (avg 500 in + 200 out tokens per turn)
daily_users = 1000
turns_per_user = 20
avg_input = 500
avg_output = 200
total_input = daily_users * turns_per_user * avg_input
total_output = daily_users * turns_per_user * avg_output
daily_cost = estimate_cost("claude-haiku-4-5", total_input, total_output)
print(f"Estimated daily cost (Haiku): ${daily_cost:.2f}")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [02 How Claude Generates Text](../02_How_Claude_Generates_Text/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Transformer Architecture](../04_Transformer_Architecture/Theory.md)
