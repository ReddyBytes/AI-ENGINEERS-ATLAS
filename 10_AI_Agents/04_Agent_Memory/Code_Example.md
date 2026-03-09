# Agent Memory — Code Example

Comparing ConversationBufferMemory vs ConversationSummaryMemory in long conversations.

---

## Setup

```bash
pip install langchain langchain-openai
```

```python
import os
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "your-key-here"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

## Part 1: ConversationBufferMemory

The simplest memory. Keeps everything verbatim.

```python
# Set up buffer memory
buffer_memory = ConversationBufferMemory()

buffer_chain = ConversationChain(
    llm=llm,
    memory=buffer_memory,
    verbose=True  # Shows what's in context each turn
)

# Simulate a multi-turn conversation
conversation_turns = [
    "Hi! My name is Alex and I'm learning Python.",
    "I'm specifically interested in building web apps with Django.",
    "My main struggle is understanding Django's ORM for database queries.",
    "Can you explain what a QuerySet is?",
    "What's the difference between filter() and get()?",
    "How do I do a JOIN in Django ORM?",
    "Can you show me how to filter by a related model field?",
    "What about aggregations like COUNT and SUM?",
    "Now, remembering what you know about me — what's the best next topic for me to learn?",
]

print("=== BUFFER MEMORY CONVERSATION ===\n")
for turn in conversation_turns:
    print(f"User: {turn}")
    response = buffer_chain.predict(input=turn)
    print(f"AI: {response[:200]}...\n")  # Truncate for display
```

**After the conversation, inspect the memory:**

```python
# See everything stored in memory
print("\n=== BUFFER MEMORY CONTENTS ===")
print(buffer_memory.load_memory_variables({}))

# Count tokens being used
messages = buffer_memory.chat_memory.messages
total_chars = sum(len(m.content) for m in messages)
print(f"\nTotal characters in memory: {total_chars}")
print(f"Number of messages: {len(messages)}")
print("Note: Every new turn sends ALL of this with the prompt")
```

**Output will show something like:**
```
Total characters in memory: 4,847
Number of messages: 18  (9 user + 9 AI)
Note: Every new turn sends ALL of this with the prompt
```

As the conversation grows, the cost grows linearly. Turn 100 sends 100 messages of context.

---

## Part 2: ConversationSummaryMemory

Summarizes the conversation as it goes. Keeps it compact.

```python
# Set up summary memory — needs an LLM to generate summaries
summary_memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=False  # Returns as text string, not messages
)

summary_chain = ConversationChain(
    llm=llm,
    memory=summary_memory,
    verbose=False
)

print("=== SUMMARY MEMORY CONVERSATION ===\n")
for turn in conversation_turns:
    print(f"User: {turn}")
    response = summary_chain.predict(input=turn)
    print(f"AI: {response[:200]}...\n")

# See the running summary
print("\n=== SUMMARY MEMORY CONTENTS ===")
print(summary_memory.load_memory_variables({}))
```

**Output will show a compact summary like:**
```
{'history': 'The human Alex is learning Python with a focus on Django web apps.
They are struggling with Django ORM for database queries. The AI explained
QuerySets (lazy evaluation collections), filter() vs get() (multiple vs single
result), JOIN operations using select_related() and prefetch_related() for
related models, filtering by related fields using double underscore notation
(e.g., author__name="Alex"), and aggregations using annotate() and aggregate()
with functions like Count() and Sum(). Alex should next focus on Django migrations
and database schema management.'}
```

The entire 9-turn conversation compressed into one paragraph.

---

## Part 3: Side-by-Side Comparison

```python
# Compare memory sizes after same conversation

print("=== MEMORY SIZE COMPARISON ===\n")

# Buffer memory size
buffer_text = str(buffer_memory.load_memory_variables({}))
print(f"Buffer Memory Size: {len(buffer_text)} characters")
print(f"Contains: Every single message, verbatim\n")

# Summary memory size
summary_text = str(summary_memory.load_memory_variables({}))
print(f"Summary Memory Size: {len(summary_text)} characters")
print(f"Contains: One compressed paragraph\n")

reduction = (1 - len(summary_text) / len(buffer_text)) * 100
print(f"Summary is {reduction:.0f}% smaller than buffer")
print(f"For long conversations (100+ turns), this difference becomes huge")
```

**Expected output:**
```
Buffer Memory Size: 5,234 characters
Contains: Every single message, verbatim

Summary Memory Size: 623 characters
Contains: One compressed paragraph

Summary is 88% smaller than buffer
For long conversations (100+ turns), this difference becomes huge
```

---

## Part 4: Testing Memory Recall

Does the agent still know who Alex is after summarization?

```python
# Test that summary memory preserved the key facts
print("=== TESTING MEMORY RECALL ===\n")

recall_questions = [
    "What's my name?",
    "What programming language am I learning?",
    "What's my main struggle with Django?",
]

print("--- Buffer Memory Recall ---")
for q in recall_questions:
    response = buffer_chain.predict(input=q)
    print(f"Q: {q}")
    print(f"A: {response}\n")

print("--- Summary Memory Recall ---")
for q in recall_questions:
    response = summary_chain.predict(input=q)
    print(f"Q: {q}")
    print(f"A: {response}\n")
```

Both should correctly answer "Alex", "Python/Django", and "ORM queries" — summary memory preserves the key facts even though it doesn't have the raw messages.

---

## Part 5: ConversationBufferWindowMemory (Bonus)

Only keeps the last N turns. A middle ground.

```python
from langchain.memory import ConversationBufferWindowMemory

# Only keep last 3 turns
window_memory = ConversationBufferWindowMemory(k=3)

window_chain = ConversationChain(
    llm=llm,
    memory=window_memory,
    verbose=False
)

# Run the same conversation
for turn in conversation_turns:
    window_chain.predict(input=turn)

# Memory only has the last 3 turns
print("=== WINDOW MEMORY (last 3 turns only) ===")
window_vars = window_memory.load_memory_variables({})
print(window_vars)
print("\nNote: Earlier context (like Alex's name) may be forgotten")
```

---

## Summary of What You Learned

```
ConversationBufferMemory:
+ Simple, exact, no information loss
+ Great for short conversations
- Grows without limit
- Expensive for long conversations

ConversationSummaryMemory:
+ Stays compact regardless of conversation length
+ Handles 100+ turns gracefully
- Requires extra LLM call to summarize
- Loses exact wording (usually fine)

ConversationBufferWindowMemory:
+ Simple and bounded
+ Good when only recent context matters
- Loses older context completely (not just compressed)
```

**Rule of thumb:**
- Under 20 turns → BufferMemory
- 20-100 turns → BufferWindowMemory or SummaryMemory
- 100+ turns → SummaryMemory
- Across sessions → VectorStoreRetrieverMemory

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Memory types comparison |

⬅️ **Prev:** [03 Tool Use](../03_Tool_Use/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Planning and Reasoning](../05_Planning_and_Reasoning/Theory.md)
