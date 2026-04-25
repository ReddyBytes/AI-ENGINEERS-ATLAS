# Project 5 — Build Guide

## Overview

This is the most architecturally complex beginner project. You will build a pipeline of 4 LLM tasks, each with its own engineered prompt. The key skill is writing prompts that reliably return specific output formats.

**Total estimated time:** 4 to 6 hours. Spend extra time on prompt engineering — slight wording changes can dramatically change reliability.

---

## Before You Start

### Step 1: Set up your environment

```bash
mkdir -p ~/ai-projects/05_document_analyzer
cd ~/ai-projects/05_document_analyzer
python -m venv venv
source venv/bin/activate
pip install anthropic pydantic
```

### Step 2: Prepare a test document

Create a `test_document.txt` with any text content. Good options:
- A Wikipedia article (copy/paste)
- A short news article
- A README from a GitHub project
- A section from any textbook

The document should be 500 to 4000 words for best results.

### Step 3: Verify your API key is set

```bash
echo $ANTHROPIC_API_KEY  # Should print your key, not empty
```

---

## Stage 1 — Load and Prepare the Document

**Goal:** Load a text file and prepare it for sending to the API.

**Concept applied:** Context window management. You can send the entire document as part of the prompt, but only up to the model's limit. Claude has a 200K token context window — much larger than needed for most documents.

### Step 4: Implement the document loader

```python
def load_document(filepath: str, max_chars: int = 100_000) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) > max_chars:
        print(f"[Warning: Document truncated from {len(content):,} to {max_chars:,} characters]")
        content = content[:max_chars]

    print(f"Document loaded: {filepath} ({len(content):,} characters)\n")
    return content
```

<details><summary>💡 Hint — why truncate at 100,000 characters?</summary>

100,000 characters is roughly 25,000 tokens. With 200K token context limit and some overhead for the prompt and output, this leaves comfortable headroom. Very long documents (books, large codebases) would need a chunking strategy instead — covered in the Advanced projects.

</details>

---

## Stage 2 — Summarizer

**Goal:** Generate a 3 to 5 sentence summary using a focused prompt.

**Concept applied:** Prompt specificity. A vague prompt ("summarize this") gives inconsistent results. A specific prompt with explicit output constraints ("in 3 to 5 sentences, using only information in the document") is far more reliable.

### Step 5: Write the summary prompt

```python
def build_summary_prompt(document: str) -> str:
    return f"""You are a document summarization assistant.

Summarize the following document in 3 to 5 sentences. Focus on:
- The main topic or argument
- The key findings or conclusions
- Any important context

Only include information that is explicitly stated in the document.
Do not add outside knowledge or speculation.

DOCUMENT:
{document}

SUMMARY:"""
```

### Step 6: Make the API call

```python
def summarize(client, document: str) -> str:
    prompt = build_summary_prompt(document)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
```

<details><summary>💡 Hint — why max_tokens=300?</summary>

A 3 to 5 sentence summary should never need more than about 300 tokens. Setting a low limit prevents runaway responses and controls cost. If you find the summary gets cut off, increase this value slightly — but resist the urge to set it to 1024 by default.

</details>

---

## Stage 3 — Entity Extractor with Structured Output

**Goal:** Extract entities as validated JSON using pydantic.

**Concept applied:** Structured output. LLMs naturally produce prose. To get machine-readable JSON reliably, you need:
1. A prompt that explains the exact JSON schema you want
2. An instruction to return only JSON (no surrounding text)
3. Pydantic validation to catch malformed output

### Step 7: Define your pydantic model

```python
from pydantic import BaseModel, ValidationError
from typing import List

class DocumentEntities(BaseModel):
    people: List[str]
    organizations: List[str]
    dates: List[str]
    key_topics: List[str]
```

### Step 8: Write the entity extraction prompt

```python
def build_entity_prompt(document: str) -> str:
    return f"""You are an information extraction assistant.

Extract entities from the following document and return them as JSON.
Return ONLY valid JSON matching this exact schema, with no other text:

{{
  "people": ["list of person names mentioned"],
  "organizations": ["list of organizations, companies, or institutions mentioned"],
  "dates": ["list of dates or time periods mentioned"],
  "key_topics": ["list of 3 to 7 key topics or concepts in the document"]
}}

If no entities of a category are found, return an empty list [].
Do not add entities that are not explicitly mentioned in the document.

DOCUMENT:
{document}

JSON:"""
```

<details><summary>💡 Hint — why use double curly braces in the f-string?</summary>

In Python f-strings, a single `{` is interpreted as the start of a substitution. To include a literal `{` in an f-string — as you need when showing a JSON example — you must escape it as `{{`. The output will contain single curly braces.

</details>

### Step 9: Make the call and validate

```python
import json

def extract_entities(client, document: str) -> DocumentEntities:
    prompt = build_entity_prompt(document)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code blocks if present (model sometimes adds ```json...```)
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
        return DocumentEntities(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Could not parse entity JSON: {e}]")
        return DocumentEntities(people=[], organizations=[], dates=[], key_topics=[])
```

<details><summary>✅ Answer — what to do when JSON parsing fails</summary>

1. Log the error and the raw output (this helps you debug your prompt)
2. Return a safe fallback (empty entities) so the application does not crash
3. Consider retrying with a more explicit prompt — e.g., add "Do not include any text before or after the JSON."

In production, you would add a retry loop with exponential backoff.

</details>

---

## Stage 4 — Document Q&A

**Goal:** Answer specific questions about the document while minimizing hallucination.

**Concept applied:** Hallucination grounding. LLMs have a tendency to fill in answers using their training knowledge rather than the provided document. The fix is to explicitly instruct the model to refuse to answer if the information is not in the document.

### Step 10: Write the Q&A prompt

```python
def build_qa_prompt(document: str, question: str) -> str:
    return f"""You are a document Q&A assistant.
Answer the following question using ONLY information explicitly stated in the document below.

Rules:
- If the answer is directly stated in the document, answer it clearly and cite the relevant section.
- If the answer is implied but not explicit, state that it is an inference and explain your reasoning.
- If the document does not contain enough information to answer the question,
  say exactly: "The document does not contain enough information to answer this question."
- Do NOT use knowledge from outside the document to answer.

DOCUMENT:
{document}

QUESTION: {question}

ANSWER:"""
```

### Step 11: Implement the Q&A function and session

```python
def answer_question(client, document: str, question: str) -> str:
    prompt = build_qa_prompt(document, question)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def run_qa_session(client, document: str):
    print("\n--- Q&A Mode (type 'done' to exit) ---")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("done", "quit", "exit", ""):
            break
        answer = answer_question(client, document, question)
        print(f"\nAnswer: {answer}\n")
```

<details><summary>💡 Hint — why does the model still sometimes hallucinate?</summary>

These strategies reduce hallucination but cannot eliminate it. The model was trained on vast amounts of text and has strong priors. Even with strict grounding instructions, it may occasionally produce plausible-sounding but incorrect answers. For high-stakes applications, always verify against source material.

</details>

---

## Stage 5 — Quiz Generator

**Goal:** Generate 5 multiple-choice questions as structured JSON.

**Concept applied:** Structured output with a nested schema. The quiz output has a nested structure (questions contain choices which are strings). This is harder JSON extraction than Stage 3.

### Step 12: Define the pydantic schema for quiz questions

```python
class QuizQuestion(BaseModel):
    question: str
    choices: List[str]   # ["A) ...", "B) ...", "C) ...", "D) ..."]
    correct_answer: str  # "A", "B", "C", or "D"
    explanation: str

class Quiz(BaseModel):
    questions: List[QuizQuestion]  # Exactly 5 questions
```

### Step 13: Write the quiz generation prompt

```python
def build_quiz_prompt(document: str) -> str:
    return f"""You are an educational quiz generator.

Generate exactly 5 multiple-choice questions to test comprehension of the document below.
Return ONLY valid JSON matching this schema, with no other text:

{{
  "questions": [
    {{
      "question": "The question text",
      "choices": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
      "correct_answer": "A",
      "explanation": "Why A is correct based on the document"
    }}
  ]
}}

Requirements:
- Each question must have exactly 4 choices labeled A through D
- All questions and answers must be based on content in the document
- Questions should test different aspects of the document

DOCUMENT:
{document}

JSON:"""
```

<details><summary>✅ Answer — full generate_quiz implementation</summary>

```python
def generate_quiz(client, document: str):
    prompt = build_quiz_prompt(document)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()

    if "```" in raw_text:
        parts = raw_text.split("```")
        for part in parts:
            if part.startswith("json"):
                raw_text = part[4:].strip()
                break
            elif "{" in part:
                raw_text = part.strip()
                break

    try:
        data = json.loads(raw_text)
        return Quiz(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Quiz parsing failed: {e}]")
        return None
```

</details>

---

## Stage 6 — Main Menu and CLI

### Step 14: Build the main menu

```python
def run_analyzer(filepath: str) -> None:
    client = anthropic.Anthropic()
    document = load_document(filepath)

    print("=" * 52)
    print("  Intelligent Document Analyzer")
    print(f"  Powered by Claude claude-opus-4-6")
    print("=" * 52)

    options = {"1": "Summarize", "2": "Extract Entities",
               "3": "Ask a Question", "4": "Generate Quiz", "5": "Run All"}

    while True:
        print()
        for key, label in options.items():
            print(f"[{key}] {label}")
        print("[q] Quit")
        choice = input("\n> ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            print("\n--- SUMMARY ---")
            print(summarize(client, document))
        elif choice == "2":
            print("\n--- ENTITIES ---")
            entities = extract_entities(client, document)
            print(entities.model_dump_json(indent=2))
        elif choice == "3":
            run_qa_session(client, document)
        elif choice == "4":
            quiz = generate_quiz(client, document)
            display_quiz(quiz)
        elif choice == "5":
            print("\n--- [1] SUMMARY ---")
            print(summarize(client, document))
            print("\n--- [2] ENTITIES ---")
            entities = extract_entities(client, document)
            print(entities.model_dump_json(indent=2))
            run_qa_session(client, document)
            print("\n--- [4] QUIZ ---")
            quiz = generate_quiz(client, document)
            display_quiz(quiz)
```

### Step 15: Add CLI entry point

```python
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligent Document Analyzer")
    parser.add_argument("filepath", help="Path to the text file to analyze")
    args = parser.parse_args()
    run_analyzer(args.filepath)
```

Run it:

```bash
python analyzer.py test_document.txt
```

---

## Debugging Tips

| Problem | Likely cause | Fix |
|---|---|---|
| JSON parse error | Model added text around JSON | Use `clean_json_response()`, check your "ONLY JSON" instruction |
| Pydantic ValidationError | Model returned wrong field names | Print `raw_text`, compare to your schema in the prompt |
| Summary is too long | `max_tokens` too high | Set `max_tokens=300` for summary |
| Model invents facts | Missing anti-hallucination instruction | Add "Do not use outside knowledge" to prompt |
| Empty entity lists | Prompt schema formatting wrong | Print the prompt and verify the JSON example is valid |

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| **03_GUIDE.md** | You are here |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |
