# Project 5 — Step-by-Step Build Guide

## Overview

This is the most architecturally complex beginner project. You'll build a pipeline of 4 LLM tasks, each with its own engineered prompt. The key skill is writing prompts that reliably return specific output formats.

**Total estimated time:** 4–6 hours. Spend extra time on prompt engineering — slight wording changes can dramatically change reliability.

---

## Before You Start — Environment Setup

### Step 1: Set up your environment

```bash
mkdir -p ~/ai-projects/05_document_analyzer
cd ~/ai-projects/05_document_analyzer
python -m venv venv
source venv/bin/activate
pip install anthropic pydantic
```

### Step 2: Prepare a test document

Create a `test_document.txt` with any text content. Some good options:
- A Wikipedia article (copy/paste)
- A short news article
- A README from a GitHub project
- A section from any textbook

The document should be 500–4000 words for best results.

### Step 3: Verify your API key is set

```bash
echo $ANTHROPIC_API_KEY  # Should print your key, not empty
```

---

## Stage 1 — Load and Prepare the Document

**Goal:** Load a text file and prepare it for sending to the API.

**Concept applied:** Context window management. You can send the entire document as part of the prompt, but only up to the model's limit. Claude has a 200K token context window — much larger than needed for most documents. For this project, we'll truncate to a safe limit and log a warning for very long documents.

### Step 4: Implement the document loader

```python
def load_document(filepath: str, max_chars: int = 100_000) -> str:
    """
    Read a text file and return its contents.
    Truncates to max_chars if the document is very long.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) > max_chars:
        print(f"[Warning: Document truncated from {len(content):,} to {max_chars:,} characters]")
        content = content[:max_chars]

    print(f"Document loaded: {filepath} ({len(content):,} characters)\n")
    return content
```

### Step 5: Test the loader

```python
document = load_document("test_document.txt")
print(document[:200])  # First 200 chars
```

---

## Stage 2 — Summarizer

**Goal:** Generate a 3–5 sentence summary using a focused prompt.

**Concept applied:** Prompt engineering — specificity. A vague prompt ("summarize this") gives inconsistent results. A specific prompt with explicit output constraints ("in 3 to 5 sentences, using only information in the document") is far more reliable.

### Step 6: Write the summary prompt

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

### Step 7: Make the API call

```python
import anthropic

def summarize(client: anthropic.Anthropic, document: str) -> str:
    """Generate a summary of the document."""
    prompt = build_summary_prompt(document)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
```

**Why `max_tokens=300`?** A 3–5 sentence summary should never need more than ~300 tokens. Setting a low limit prevents runaway responses and controls cost.

---

## Stage 3 — Entity Extractor with Structured Output

**Goal:** Extract entities as validated JSON using pydantic.

**Concept applied:** Structured output. LLMs naturally produce prose. To get machine-readable JSON reliably, you need:
1. A prompt that explains the exact JSON schema you want
2. An instruction to return only JSON (no surrounding text)
3. Pydantic validation to catch malformed output

### Step 8: Define your pydantic model

```python
from pydantic import BaseModel, ValidationError
from typing import List

class DocumentEntities(BaseModel):
    people: List[str]
    organizations: List[str]
    dates: List[str]
    key_topics: List[str]
```

This model defines exactly what fields you expect and their types. If the LLM returns something that doesn't match, pydantic raises a `ValidationError` you can catch.

### Step 9: Write the entity extraction prompt

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

**Key prompt techniques:**
- "Return ONLY valid JSON with no other text" — prevents the model from adding explanations around the JSON
- Showing the exact schema — gives the model a template to follow
- "Do not add entities not mentioned" — anti-hallucination instruction

### Step 10: Make the call and validate

```python
import json

def extract_entities(client: anthropic.Anthropic, document: str) -> DocumentEntities:
    """Extract structured entities from the document."""
    prompt = build_entity_prompt(document)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
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
        entities = DocumentEntities(**data)  # Pydantic validates the structure
        return entities
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Could not parse entity JSON: {e}]")
        print(f"Raw output: {raw_text[:200]}")
        # Return empty entities as fallback
        return DocumentEntities(people=[], organizations=[], dates=[], key_topics=[])
```

### Step 11: What to do when JSON parsing fails

If the model returns malformed JSON:
1. Log the error and the raw output (helps you debug the prompt)
2. Return a safe fallback (empty entities)
3. Consider retrying with a more explicit prompt

In production, you'd add a retry loop with exponential backoff.

---

## Stage 4 — Document Q&A

**Goal:** Answer specific questions about the document while minimizing hallucination.

**Concept applied:** Hallucination grounding. LLMs have a tendency to "fill in" answers using their training knowledge rather than the provided document. The anti-hallucination technique is to explicitly instruct the model to refuse to answer if the information isn't in the document.

### Step 12: Write the Q&A prompt

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

### Step 13: Implement the Q&A function

```python
def answer_question(client: anthropic.Anthropic, document: str, question: str) -> str:
    """Answer a question about the document."""
    prompt = build_qa_prompt(document, question)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
```

### Step 14: Run a Q&A session

```python
def run_qa_session(client, document):
    """Interactive Q&A loop about the document."""
    print("\n--- Q&A Mode (type 'done' to exit) ---")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("done", "quit", "exit", ""):
            break
        answer = answer_question(client, document, question)
        print(f"\nAnswer: {answer}\n")
```

---

## Stage 5 — Quiz Generator

**Goal:** Generate 5 multiple-choice questions as structured JSON.

**Concept applied:** Combining structured output with prompt chaining. The quiz output has a nested schema (questions → choices → answer). This is a harder JSON extraction challenge than Stage 3.

### Step 15: Define the pydantic schema for quiz questions

```python
class QuizQuestion(BaseModel):
    question: str
    choices: List[str]   # Exactly 4 choices, labeled A-D
    correct_answer: str  # The letter: "A", "B", "C", or "D"
    explanation: str     # Why the correct answer is right

class Quiz(BaseModel):
    questions: List[QuizQuestion]  # Exactly 5 questions
```

### Step 16: Write the quiz generation prompt

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
- Include a mix of factual recall and comprehension questions

DOCUMENT:
{document}

JSON:"""
```

### Step 17: Implement the quiz generator

```python
def generate_quiz(client: anthropic.Anthropic, document: str) -> Quiz:
    """Generate a 5-question quiz about the document."""
    prompt = build_quiz_prompt(document)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if present
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

### Step 18: Display the quiz

```python
def display_quiz(quiz: Quiz) -> None:
    """Print the quiz questions."""
    if not quiz:
        print("[Quiz generation failed]")
        return

    print("\n--- Quiz ---")
    for i, q in enumerate(quiz.questions, 1):
        print(f"\nQ{i}: {q.question}")
        for choice in q.choices:
            print(f"     {choice}")
        print(f"     Correct: {q.correct_answer}")
        print(f"     Why: {q.explanation}")
```

---

## Stage 6 — Main Menu and CLI

### Step 19: Build the main menu

```python
def run_analyzer(filepath: str) -> None:
    """Main application loop."""
    client = anthropic.Anthropic()
    document = load_document(filepath)

    print("=" * 52)
    print("  Intelligent Document Analyzer")
    print("  Powered by Claude claude-opus-4-6")
    print("=" * 52)

    options = {
        "1": "Summarize",
        "2": "Extract Entities",
        "3": "Ask a Question",
        "4": "Generate Quiz",
        "5": "Run All",
    }

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

### Step 20: Add the CLI entry point

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

## Extend the Project

### Extension 1 — Retry on JSON Failure

```python
def extract_entities_with_retry(client, document, max_retries=2):
    for attempt in range(max_retries):
        result = extract_entities(client, document)
        if result.people or result.key_topics:  # Got some results
            return result
        print(f"[Retry {attempt + 1}...]")
    return result  # Return last attempt even if empty
```

### Extension 2 — Stdin Support

```python
import sys
content = sys.stdin.read() if not sys.stdin.isatty() else None
if content:
    # User piped text: echo "some text" | python analyzer.py -
```

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| **Step_by_Step.md** | You are here |
| [Starter_Code.md](./Starter_Code.md) | Python starter code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
