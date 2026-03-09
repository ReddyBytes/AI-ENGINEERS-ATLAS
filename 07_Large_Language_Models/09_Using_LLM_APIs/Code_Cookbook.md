# LLM API Code Cookbook

Ready-to-use code snippets for working with the Anthropic Claude API. Every snippet is heavily commented. Copy, adapt, and run.

## Prerequisites

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key-here"  # Get from console.anthropic.com
```

---

## Recipe 1: Basic API call

The simplest possible call — one question, one answer.

```python
import anthropic

# Initialize the client — reads ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic()

# Make the API call
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",    # Model to use
    max_tokens=1024,                        # Maximum tokens to generate
    messages=[                              # The conversation
        {
            "role": "user",
            "content": "What is the difference between RAM and storage?"
        }
    ]
)

# Extract the text from the response
answer = response.content[0].text
print(answer)

# Check token usage (for cost tracking)
print(f"\nTokens used — Input: {response.usage.input_tokens}, "
      f"Output: {response.usage.output_tokens}")

# Check why generation stopped
# "end_turn" = model finished naturally
# "max_tokens" = hit the token limit (increase max_tokens if this happens)
print(f"Stop reason: {response.stop_reason}")
```

---

## Recipe 2: Streaming response

Tokens appear as they're generated — much better UX for chat applications.

```python
import anthropic

client = anthropic.Anthropic()

print("Response: ", end="", flush=True)

# Use context manager for streaming
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Explain how neural networks learn in 3 paragraphs."
    }]
) as stream:

    # text_stream yields each text chunk as it arrives
    for text_chunk in stream.text_stream:
        print(text_chunk, end="", flush=True)  # Print without newline, flush immediately

print()  # Final newline after streaming complete

# Get the final complete response and usage stats
final_response = stream.get_final_message()
print(f"\nTotal tokens: {final_response.usage.input_tokens} in, "
      f"{final_response.usage.output_tokens} out")
```

---

## Recipe 3: Structured JSON output using tool use

Get reliable JSON output (not just "hope the model outputs JSON").

```python
import json
import anthropic

client = anthropic.Anthropic()

def extract_product_info(description: str) -> dict:
    """
    Extract product name, price, and category from a text description.
    Returns a Python dict with the structured data.
    """

    # Define the schema for the structured output
    # The model will fill in this schema
    tools = [{
        "name": "save_product",
        "description": "Save structured product information",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "The name of the product"
                },
                "price_usd": {
                    "type": "number",
                    "description": "Price in US dollars (number only, no $ sign)"
                },
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "food", "furniture", "other"],
                    "description": "Product category"
                },
                "in_stock": {
                    "type": "boolean",
                    "description": "Whether the product is currently in stock"
                }
            },
            "required": ["product_name", "price_usd", "category"]  # These must be filled
        }
    }]

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        tools=tools,
        tool_choice={"type": "tool", "name": "save_product"},  # Force tool use
        messages=[{
            "role": "user",
            "content": f"Extract product information from this text: {description}"
        }]
    )

    # Check that the model used the tool as expected
    if response.stop_reason != "tool_use":
        raise ValueError(f"Expected tool use, got: {response.stop_reason}")

    # Find the tool_use block in the response content
    tool_use_block = next(
        block for block in response.content
        if block.type == "tool_use"
    )

    # Return the structured data as a Python dict
    return tool_use_block.input


# Test it
products = [
    "The Sony WH-1000XM5 headphones are $348.00. Available now.",
    "Nike Air Max 90 running shoes, $110 in classic white. Currently out of stock.",
    "Organic avocados 4-pack, just $3.99. Limited supply.",
]

for description in products:
    data = extract_product_info(description)
    print(json.dumps(data, indent=2))
    print("---")
```

---

## Recipe 4: Multi-turn conversation

Build a simple chatbot that remembers the conversation.

```python
import anthropic
from typing import List, Dict

client = anthropic.Anthropic()

class SimpleChatbot:
    """
    A simple chatbot that maintains conversation history.
    The model has no built-in memory — we pass the full history every time.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict] = []

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Send the full conversation history to the API
        # Without this, the model wouldn't remember previous turns
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.system_prompt,       # Instructions for the model
            messages=self.conversation_history  # Full conversation history
        )

        # Extract the response text
        assistant_message = response.content[0].text

        # Add the model's response to history for next turn
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def get_token_count(self) -> int:
        """Rough estimate of history size (important for context window management)."""
        total_chars = sum(len(m["content"]) for m in self.conversation_history)
        return total_chars // 4  # Very rough: ~4 chars per token

    def reset(self):
        """Clear conversation history to start fresh."""
        self.conversation_history = []


# Demo usage
bot = SimpleChatbot(
    system_prompt="You are a helpful Python tutor. Keep explanations simple and practical."
)

# Multi-turn conversation
questions = [
    "What is a list comprehension in Python?",
    "Can you show me an example?",
    "When should I NOT use list comprehensions?",
    "What was the first thing I asked you?",  # Tests memory
]

for question in questions:
    print(f"\nUser: {question}")
    response = bot.chat(question)
    print(f"Bot: {response[:200]}...")  # Print first 200 chars
    print(f"(History size: ~{bot.get_token_count()} tokens)")
```

---

## Recipe 5: Error handling with retry logic

Production-ready API calls that handle rate limits and server errors gracefully.

```python
import time
import anthropic
import logging

# Set up logging so we can see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

client = anthropic.Anthropic()


def api_call_with_retry(
    messages: list,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1024,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> anthropic.types.Message:
    """
    Make an API call with automatic retry on transient errors.

    Retries on:
    - 429 Rate limit (too many requests) — wait and retry
    - 500/502/503 Server errors — wait and retry

    Does NOT retry on:
    - 400 Bad request — your prompt is malformed, fix it
    - 401 Unauthorized — fix your API key
    - 413 Payload too large — shorten your prompt
    """

    for attempt in range(max_retries):
        try:
            logger.info(f"API call attempt {attempt + 1}/{max_retries}")

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )

            logger.info(f"Success: {response.usage.input_tokens} input tokens, "
                        f"{response.usage.output_tokens} output tokens")
            return response

        except anthropic.RateLimitError as e:
            # 429: Too many requests per minute
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error("Rate limit exceeded after all retries")
                raise

        except anthropic.APIStatusError as e:
            if e.status_code in (500, 502, 503):
                # Server error — might be transient
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Server error {e.status_code}. "
                                   f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Server error after all retries: {e.status_code}")
                    raise
            else:
                # 400, 401, 413 etc. — don't retry, fix the request
                logger.error(f"Non-retryable error: {e.status_code} - {e.message}")
                raise

        except anthropic.APIConnectionError as e:
            # Network connection failed
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(f"Connection error. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise

    raise RuntimeError("Unexpected exit from retry loop")


# Usage
response = api_call_with_retry(
    messages=[{"role": "user", "content": "What is 2+2?"}],
    model="claude-3-5-haiku-20241022",
    max_tokens=50
)
print(response.content[0].text)
```

---

## Recipe 6: Batch processing with cost tracking

Process many items efficiently with cost monitoring.

```python
import anthropic
import time
from dataclasses import dataclass, field
from typing import List

client = anthropic.Anthropic()


@dataclass
class CostTracker:
    """Track API usage and costs across multiple calls."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_calls: int = 0
    failed_calls: int = 0

    # Approximate pricing (Claude Sonnet, as of 2024 — check for current prices)
    INPUT_COST_PER_MILLION = 3.00   # $3 per million input tokens
    OUTPUT_COST_PER_MILLION = 15.00  # $15 per million output tokens

    def add_usage(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_calls += 1

    @property
    def total_cost_usd(self) -> float:
        input_cost = (self.total_input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (self.total_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        return input_cost + output_cost

    def print_summary(self):
        print(f"\n=== Cost Summary ===")
        print(f"Total calls: {self.total_calls} ({self.failed_calls} failed)")
        print(f"Input tokens: {self.total_input_tokens:,}")
        print(f"Output tokens: {self.total_output_tokens:,}")
        print(f"Estimated cost: ${self.total_cost_usd:.4f}")


def classify_sentiment(texts: List[str], tracker: CostTracker) -> List[str]:
    """
    Classify sentiment for a list of texts.
    Uses Haiku (cheapest, fast) since sentiment classification is a simple task.
    """
    results = []

    for i, text in enumerate(texts):
        print(f"Processing {i+1}/{len(texts)}...", end="\r")

        try:
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use cheapest model for simple tasks
                max_tokens=10,                        # Very short output — just the label
                messages=[{
                    "role": "user",
                    "content": f"""Classify the sentiment of this text as exactly one of:
POSITIVE, NEGATIVE, or NEUTRAL.
Reply with ONLY the single word label.

Text: {text}"""
                }]
            )

            sentiment = response.content[0].text.strip().upper()
            results.append(sentiment)
            tracker.add_usage(response.usage.input_tokens, response.usage.output_tokens)

        except Exception as e:
            tracker.failed_calls += 1
            results.append("ERROR")
            print(f"\nError on item {i}: {e}")

        # Small delay to avoid rate limits on large batches
        time.sleep(0.1)

    return results


# Example usage
texts = [
    "This product is absolutely amazing! Best purchase I've ever made.",
    "Complete waste of money. Broke after one day.",
    "The package arrived on time. Standard product.",
    "I love everything about this! Highly recommend to everyone!",
    "Terrible customer service. Will never buy again.",
]

tracker = CostTracker()
sentiments = classify_sentiment(texts, tracker)

print("\n\nResults:")
for text, sentiment in zip(texts, sentiments):
    print(f"  [{sentiment}] {text[:60]}...")

tracker.print_summary()
```

---

## Recipe 7: System prompt engineering patterns

Common patterns for effective system prompts.

```python
import anthropic

client = anthropic.Anthropic()


def create_specialized_assistant(role: str, constraints: list, examples: list = None) -> str:
    """
    Build a well-structured system prompt.
    Returns the system prompt string.
    """

    prompt_parts = [
        f"You are {role}.",
        "",
        "## Rules",
    ]

    for i, constraint in enumerate(constraints, 1):
        prompt_parts.append(f"{i}. {constraint}")

    if examples:
        prompt_parts.extend(["", "## Examples"])
        for example in examples:
            prompt_parts.append(f"User: {example['user']}")
            prompt_parts.append(f"You: {example['assistant']}")
            prompt_parts.append("")

    return "\n".join(prompt_parts)


# Build different specialized assistants
code_reviewer_prompt = create_specialized_assistant(
    role="a senior Python code reviewer focused on clean code and security",
    constraints=[
        "Point out security vulnerabilities first, then code quality issues",
        "Be specific: quote the exact line of code with issues",
        "Suggest the fixed version for every issue you find",
        "Keep reviews under 300 words",
        "Do not praise the code — only point out problems",
    ]
)

customer_service_prompt = create_specialized_assistant(
    role="a friendly customer service agent for Acme Software",
    constraints=[
        "Always greet the customer by name if they provide it",
        "Acknowledge the customer's problem before offering a solution",
        "Never promise something you cannot guarantee",
        "If you cannot solve the problem, offer to escalate",
        "Do not discuss competitor products",
    ],
    examples=[
        {
            "user": "My software keeps crashing.",
            "assistant": "I'm really sorry to hear you're experiencing crashes — that's frustrating. To help you quickly, could you tell me which version you're running and what you were doing when it crashed?"
        }
    ]
)

# Use the code reviewer
code_to_review = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=500,
    system=code_reviewer_prompt,
    messages=[{
        "role": "user",
        "content": f"Please review this code:\n\n{code_to_review}"
    }]
)
print("Code Review:")
print(response.content[0].text)
```

---

## Quick reference: response object structure

```python
response = client.messages.create(...)

# Text content (most common)
text = response.content[0].text

# For tool use responses
for block in response.content:
    if block.type == "text":
        print("Text:", block.text)
    elif block.type == "tool_use":
        print("Tool called:", block.name)
        print("Tool input:", block.input)  # dict

# Usage stats
print(response.usage.input_tokens)   # tokens you sent
print(response.usage.output_tokens)  # tokens generated

# Why generation stopped
print(response.stop_reason)
# "end_turn"    = model finished naturally
# "max_tokens"  = hit your max_tokens limit
# "stop_sequence" = hit a stop sequence
# "tool_use"    = model wants to use a tool

# Model that was used
print(response.model)

# Unique ID for this request (useful for debugging with Anthropic support)
print(response.id)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Cookbook.md** | ← you are here |
| [📄 Cost_Guide.md](./Cost_Guide.md) | Cost optimization guide |

⬅️ **Prev:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Prompt Engineering](../../08_LLM_Applications/01_Prompt_Engineering/Theory.md)