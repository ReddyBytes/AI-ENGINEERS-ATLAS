# Project 5 — Starter Code

Copy this to `analyzer.py`. Fill in every `# TODO:` section.

This is the most complex starter code in the series — take time to understand each prompt before filling in the TODOs.

---

```python
"""
Project 5 — Intelligent Document Analyzer
==========================================
Analyzes text documents using Claude with 4 capabilities:
  1. Summarize the document
  2. Extract structured entities as JSON
  3. Answer questions about the document
  4. Generate a 5-question comprehension quiz

Usage:
    python analyzer.py path/to/document.txt

Setup:
    export ANTHROPIC_API_KEY="sk-ant-your-key-here"
    pip install anthropic pydantic
"""

import anthropic
import json
import argparse
import os
from pydantic import BaseModel, ValidationError
from typing import List


# ============================================================
# SECTION 1 — PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================

class DocumentEntities(BaseModel):
    """Structured schema for extracted entities."""
    people: List[str]
    organizations: List[str]
    dates: List[str]
    key_topics: List[str]


class QuizQuestion(BaseModel):
    """A single multiple-choice question."""
    question: str
    choices: List[str]      # ["A) ...", "B) ...", "C) ...", "D) ..."]
    correct_answer: str     # "A", "B", "C", or "D"
    explanation: str        # Why this answer is correct


class Quiz(BaseModel):
    """A collection of quiz questions."""
    questions: List[QuizQuestion]


# ============================================================
# SECTION 2 — DOCUMENT LOADING
# ============================================================

def load_document(filepath: str, max_chars: int = 100_000) -> str:
    """
    Read a text file and return its contents.
    Prints a warning and truncates if the document exceeds max_chars.
    """
    # TODO: Open filepath with encoding='utf-8' and read its contents
    # If content > max_chars, print a warning and truncate to max_chars
    # Print a line like: f"Document loaded: {filepath} ({len(content):,} characters)\n"
    # Return the content string

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # TODO: Check if content is longer than max_chars and truncate if needed
    # Hint: if len(content) > max_chars: content = content[:max_chars]

    print(f"Document loaded: {filepath} ({len(content):,} characters)\n")
    return content


# ============================================================
# SECTION 3 — PROMPT BUILDERS
# ============================================================

def build_summary_prompt(document: str) -> str:
    """
    Build a prompt that instructs the model to summarize the document
    in 3–5 sentences using only information from the document.

    Key prompt requirements:
    - Specify 3–5 sentences explicitly
    - Instruct the model to focus on main topic, key findings, context
    - Add an anti-hallucination instruction: only use the document

    Returns a complete prompt string ending with "SUMMARY:"
    """
    # TODO: Write the summary prompt
    # Structure: system instructions + DOCUMENT: {document} + SUMMARY:
    # See Step_by_Step.md Stage 2 for the full prompt template
    prompt = f"""You are a document summarization assistant.

Summarize the following document in 3 to 5 sentences. Focus on:
- The main topic or argument
- The key findings or conclusions
- Any important context

Only include information that is explicitly stated in the document.
Do not add outside knowledge or speculation.

DOCUMENT:
{document}

SUMMARY:"""
    return prompt


def build_entity_prompt(document: str) -> str:
    """
    Build a prompt that instructs the model to return entity extraction
    results as a JSON object matching the DocumentEntities schema.

    Key prompt requirements:
    - Show the exact JSON schema in the prompt
    - Say "Return ONLY valid JSON with no other text"
    - Instruct: return empty list [] if no entities found in a category
    - Anti-hallucination: "Do not add entities not mentioned in the document"

    Returns a complete prompt string ending with "JSON:"
    """
    # TODO: Write the entity extraction prompt
    # Include the exact JSON schema structure as a string example in the prompt
    # See Step_by_Step.md Stage 3 for the full prompt template
    prompt = None  # TODO: replace with your prompt string
    return prompt


def build_qa_prompt(document: str, question: str) -> str:
    """
    Build a prompt for answering a specific question about the document.

    Key prompt requirements:
    - Instruction to only use the document (not external knowledge)
    - Three-case rule:
        1. Answer is explicit → answer with citation
        2. Answer is implied → state it's an inference
        3. Document doesn't have enough info → say exactly that
    - Anti-hallucination: explicit "do not use outside knowledge" instruction

    Returns a complete prompt string ending with "ANSWER:"
    """
    # TODO: Write the Q&A prompt incorporating the question and document
    # See Step_by_Step.md Stage 4 for the full prompt template
    prompt = None  # TODO: replace with your prompt string
    return prompt


def build_quiz_prompt(document: str) -> str:
    """
    Build a prompt that generates 5 multiple-choice questions
    as JSON matching the Quiz schema.

    Key prompt requirements:
    - Show the exact nested JSON schema for Quiz/QuizQuestion
    - Specify: exactly 5 questions, exactly 4 choices per question (A–D)
    - All questions based on the document content
    - "Return ONLY valid JSON with no other text"

    Returns a complete prompt string ending with "JSON:"
    """
    # TODO: Write the quiz generation prompt
    # Include the full JSON schema with nested structure
    # See Step_by_Step.md Stage 5 for the full prompt template
    prompt = None  # TODO: replace with your prompt string
    return prompt


# ============================================================
# SECTION 4 — API CALL HELPERS
# ============================================================

def call_api(client: anthropic.Anthropic, prompt: str, max_tokens: int = 500) -> str:
    """
    Make a single API call and return the text response.

    Args:
        client:     Anthropic client
        prompt:     the full prompt string
        max_tokens: maximum tokens in the response

    Returns:
        response text as a string (stripped of whitespace)
    """
    # TODO: Call client.messages.create with:
    #   model="claude-opus-4-6"
    #   max_tokens=max_tokens
    #   messages=[{"role": "user", "content": prompt}]
    # Return response.content[0].text.strip()
    response = None  # TODO: replace
    return response


def clean_json_response(raw_text: str) -> str:
    """
    Remove markdown code fences (```json ... ```) from a response if present.
    LLMs sometimes wrap their JSON in markdown code blocks even when told not to.

    Args:
        raw_text: the raw string from the API response

    Returns:
        the JSON string with any surrounding markdown removed
    """
    # TODO: If raw_text contains "```", extract just the JSON portion
    # Hint: split on "```", look for a part starting with "json" or "{"
    # See Step_by_Step.md Stage 3 Step 10 for the approach
    if "```" not in raw_text:
        return raw_text.strip()

    # TODO: Extract JSON from between the backticks
    cleaned = raw_text  # TODO: replace with your extraction logic
    return cleaned.strip()


# ============================================================
# SECTION 5 — ANALYSIS FUNCTIONS
# ============================================================

def summarize(client: anthropic.Anthropic, document: str) -> str:
    """Generate a 3–5 sentence summary of the document."""
    # TODO: Build the summary prompt using build_summary_prompt(document)
    # Call call_api with max_tokens=300
    # Return the result
    prompt = None  # TODO
    return None    # TODO: call_api(client, prompt, max_tokens=300)


def extract_entities(client: anthropic.Anthropic, document: str) -> DocumentEntities:
    """
    Extract structured entities from the document.
    Returns a validated DocumentEntities pydantic object.
    Returns empty entities on parse failure.
    """
    # TODO: Build the entity prompt using build_entity_prompt(document)
    prompt = None  # TODO

    # TODO: Call call_api with max_tokens=600
    raw_text = None  # TODO

    # TODO: Clean the response with clean_json_response(raw_text)
    raw_text = None  # TODO

    # TODO: Parse with json.loads(), then create DocumentEntities(**data)
    # Wrap in try/except for json.JSONDecodeError and ValidationError
    # On failure: print a warning and return DocumentEntities with empty lists
    try:
        data = None   # TODO: json.loads(raw_text)
        return None   # TODO: DocumentEntities(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Entity parsing failed: {e}]")
        print(f"[Raw output: {raw_text[:200] if raw_text else 'None'}]")
        return DocumentEntities(people=[], organizations=[], dates=[], key_topics=[])


def answer_question(client: anthropic.Anthropic,
                    document: str,
                    question: str) -> str:
    """Answer a specific question about the document."""
    # TODO: Build the Q&A prompt using build_qa_prompt(document, question)
    # Call call_api with max_tokens=400
    # Return the result
    prompt = None   # TODO
    return None     # TODO: call_api(client, prompt, max_tokens=400)


def generate_quiz(client: anthropic.Anthropic, document: str):
    """
    Generate a 5-question multiple-choice quiz about the document.
    Returns a validated Quiz pydantic object, or None on failure.
    """
    # TODO: Build the quiz prompt using build_quiz_prompt(document)
    prompt = None  # TODO

    # TODO: Call call_api with max_tokens=1500
    raw_text = None  # TODO

    # TODO: Clean with clean_json_response, then parse and validate
    # Return Quiz(**data) or None on failure
    raw_text = None  # TODO: clean_json_response(raw_text)

    try:
        data = None   # TODO: json.loads(raw_text)
        return None   # TODO: Quiz(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Quiz parsing failed: {e}]")
        print(f"[Raw output: {raw_text[:300] if raw_text else 'None'}]")
        return None


# ============================================================
# SECTION 6 — DISPLAY FUNCTIONS
# ============================================================

def display_entities(entities: DocumentEntities) -> None:
    """Print entities as formatted JSON."""
    print(entities.model_dump_json(indent=2))


def display_quiz(quiz) -> None:
    """Print quiz questions with choices, answers, and explanations."""
    if not quiz:
        print("[Quiz generation failed. Try again.]")
        return

    print(f"\nGenerated {len(quiz.questions)} questions:\n")
    for i, q in enumerate(quiz.questions, 1):
        print(f"Q{i}: {q.question}")
        for choice in q.choices:
            print(f"     {choice}")
        print(f"     Correct answer: {q.correct_answer}")
        print(f"     Explanation: {q.explanation}")
        print()


# ============================================================
# SECTION 7 — INTERACTIVE Q&A SESSION
# ============================================================

def run_qa_session(client: anthropic.Anthropic, document: str) -> None:
    """
    Run an interactive question-answering session about the document.
    User types questions; type 'done' to exit.
    """
    print("\n--- Q&A Mode (type 'done' to exit) ---")
    while True:
        question = input("Your question: ").strip()
        if not question or question.lower() in ("done", "quit", "exit"):
            break

        # TODO: Call answer_question(client, document, question) and print the result
        answer = None  # TODO
        print(f"\nAnswer: {answer}\n")


# ============================================================
# SECTION 8 — MAIN MENU LOOP
# ============================================================

def run_analyzer(filepath: str) -> None:
    """
    Main application: load document, present menu, execute chosen tasks.
    """
    # TODO: Create the Anthropic client (same as Project 4: anthropic.Anthropic())
    client = None  # TODO

    # TODO: Load the document using load_document(filepath)
    document = None  # TODO

    print("=" * 52)
    print("  Intelligent Document Analyzer")
    print(f"  Powered by Claude claude-opus-4-6")
    print("=" * 52)

    options = {
        "1": "Summarize",
        "2": "Extract Entities",
        "3": "Ask a Question",
        "4": "Generate Quiz",
        "5": "Run All (1–4)",
    }

    while True:
        print()
        for key, label in options.items():
            print(f"[{key}] {label}")
        print("[q] Quit")

        choice = input("\n> ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        elif choice == "1":
            print("\n--- SUMMARY ---")
            # TODO: Call summarize(client, document) and print the result
            print(None)  # TODO

        elif choice == "2":
            print("\n--- ENTITIES ---")
            # TODO: Call extract_entities(client, document) and display_entities()
            pass  # TODO

        elif choice == "3":
            # TODO: Call run_qa_session(client, document)
            pass  # TODO

        elif choice == "4":
            print("\n--- QUIZ ---")
            # TODO: Call generate_quiz(client, document) and display_quiz()
            pass  # TODO

        elif choice == "5":
            print("\n--- [1] SUMMARY ---")
            # TODO: Run all 4 analyses in sequence
            # 1. summarize and print
            # 2. extract_entities and display_entities
            # 3. run_qa_session
            # 4. generate_quiz and display_quiz
            pass  # TODO

        else:
            print("[Invalid choice. Please enter 1–5 or q.]")


# ============================================================
# MAIN — CLI Entry Point
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Intelligent Document Analyzer powered by Claude"
    )
    parser.add_argument(
        "filepath",
        help="Path to the text file to analyze"
    )
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"Error: File not found: {args.filepath}")
        exit(1)

    run_analyzer(args.filepath)
```

---

## What You Need to Fill In

| Function | What to implement | Difficulty |
|---|---|---|
| `load_document()` | Truncate if > max_chars | Easy |
| `build_summary_prompt()` | 3–5 sentence constraint + anti-hallucination | Medium |
| `build_entity_prompt()` | JSON schema in prompt + "ONLY JSON" instruction | Medium |
| `build_qa_prompt()` | 3-case instruction + anti-hallucination | Medium |
| `build_quiz_prompt()` | Nested JSON schema + 5 questions + 4 choices each | Hard |
| `call_api()` | `client.messages.create()` call | Easy |
| `clean_json_response()` | Strip markdown code fences from response | Medium |
| `summarize()` | Build prompt, call API, return text | Easy |
| `extract_entities()` | Call API, clean JSON, parse with pydantic | Medium |
| `answer_question()` | Build Q&A prompt, call API, return answer | Easy |
| `generate_quiz()` | Call API, clean JSON, validate Quiz model | Hard |
| `run_qa_session()` | Input loop calling answer_question | Easy |
| `run_analyzer()` | Wire client, document, menu, all tasks | Medium |

---

## How to Run

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Install dependencies
pip install anthropic pydantic

# Run with a text file
python analyzer.py test_document.txt

# Or with any text file:
python analyzer.py /path/to/some/article.txt
```

---

## Debugging Tips

| Problem | Likely cause | Fix |
|---|---|---|
| JSON parse error | Model added text around JSON | Use `clean_json_response()`, check your "ONLY JSON" instruction |
| Pydantic ValidationError | Model returned wrong field names | Print raw_text, compare to your schema in the prompt |
| Summary is too long | max_tokens too high | Set max_tokens=300 for summary |
| Model "invents" facts | Missing anti-hallucination instruction | Add "Do not use outside knowledge" to prompt |
| Empty entity lists | Prompt schema formatting wrong | Print the prompt and verify the JSON example is valid |

---

## 📂 Navigation

| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | Overview and objectives |
| [Step_by_Step.md](./Step_by_Step.md) | Detailed build instructions |
| **Starter_Code.md** | You are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |
