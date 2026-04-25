"""
Project 5 — Intelligent Document Analyzer  [SOLUTION]
======================================================
Analyzes text documents using Claude with 4 capabilities:
  1. Summarize the document
  2. Extract structured entities as JSON
  3. Answer questions about the document
  4. Generate a 5-question comprehension quiz

Usage:
    python solution.py path/to/document.txt

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
    people: List[str]           # ← person names mentioned in the document
    organizations: List[str]    # ← companies, institutions, groups
    dates: List[str]            # ← dates and time periods
    key_topics: List[str]       # ← 3 to 7 main concepts


class QuizQuestion(BaseModel):
    """A single multiple-choice question."""
    question: str
    choices: List[str]      # ← ["A) ...", "B) ...", "C) ...", "D) ..."]
    correct_answer: str     # ← "A", "B", "C", or "D"
    explanation: str        # ← Why this answer is correct


class Quiz(BaseModel):
    """A collection of quiz questions."""
    questions: List[QuizQuestion]  # ← exactly 5 questions


# ============================================================
# SECTION 2 — DOCUMENT LOADING
# ============================================================

def load_document(filepath: str, max_chars: int = 100_000) -> str:
    """
    Read a text file and return its contents.
    Prints a warning and truncates if the document exceeds max_chars.

    Why truncate? Claude has a 200K token context window. 100,000 chars
    is roughly 25,000 tokens — safely within limits with room for the
    prompt text and output.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) > max_chars:
        print(f"[Warning: Document truncated from {len(content):,} to {max_chars:,} characters]")
        content = content[:max_chars]  # ← keep only the first max_chars characters

    print(f"Document loaded: {filepath} ({len(content):,} characters)\n")
    return content


# ============================================================
# SECTION 3 — PROMPT BUILDERS
# ============================================================

def build_summary_prompt(document: str) -> str:
    """
    Build a prompt that instructs the model to summarize the document
    in 3 to 5 sentences using only information from the document.
    """
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
    """
    # Double braces {{ }} in f-strings produce literal { } in the output
    prompt = f"""You are an entity extraction assistant.

Extract entities from the document and return ONLY valid JSON with no other text.
Use exactly this structure:

{{
  "people": ["list of person names"],
  "organizations": ["list of companies, institutions, or groups"],
  "dates": ["list of dates and time periods"],
  "key_topics": ["list of 3 to 7 main concepts or themes"]
}}

Rules:
- Return ONLY valid JSON — no markdown, no explanation, no extra text
- Use empty lists [] if a category has no entries
- Do not add entities not mentioned in the document

DOCUMENT:
{document}

JSON:"""
    return prompt


def build_qa_prompt(document: str, question: str) -> str:
    """
    Build a prompt for answering a specific question about the document.
    """
    prompt = f"""You are a document question-answering assistant.

Answer the question based ONLY on information in the document below.
Follow these rules strictly:
1. If the answer is explicitly stated: answer it and cite the relevant part.
2. If the answer can be inferred but is not explicit: state it is an inference.
3. If there is not enough information: say exactly "The document does not contain enough information to answer this question."

Do NOT use knowledge from outside the document.

DOCUMENT:
{document}

QUESTION: {question}

ANSWER:"""
    return prompt


def build_quiz_prompt(document: str) -> str:
    """
    Build a prompt that generates 5 multiple-choice questions
    as JSON matching the Quiz/QuizQuestion schema.
    """
    # Nested schema shown inline so the model has a concrete template to follow
    prompt = f"""You are a quiz generation assistant.

Generate exactly 5 multiple-choice questions based on the document below.
Return ONLY valid JSON with no other text, using exactly this structure:

{{
  "questions": [
    {{
      "question": "The question text here",
      "choices": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
      "correct_answer": "A",
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Rules:
- Generate exactly 5 questions
- Each question must have exactly 4 choices labeled A through D
- correct_answer must be a single letter: "A", "B", "C", or "D"
- All questions and answers must come directly from the document
- Return ONLY valid JSON — no markdown, no preamble

DOCUMENT:
{document}

JSON:"""
    return prompt


# ============================================================
# SECTION 4 — API CALL HELPERS
# ============================================================

def call_api(client: anthropic.Anthropic, prompt: str, max_tokens: int = 500) -> str:
    """
    Make a single API call and return the text response.

    All 4 analysis tasks use this same function with different
    prompts and max_tokens values.
    """
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()  # ← content[0] is the first (and only) content block


def clean_json_response(raw_text: str) -> str:
    """
    Remove markdown code fences from a response if present.

    LLMs sometimes wrap JSON in ```json...``` blocks even when told not to.
    This function extracts just the JSON portion.

    Example input:
        ```json
        {"key": "value"}
        ```
    Example output:
        {"key": "value"}
    """
    if "```" not in raw_text:
        return raw_text.strip()

    # Split on ``` to isolate the content between the fences
    parts = raw_text.split("```")
    for part in parts:
        stripped = part.strip()
        # The fenced block either starts with "json\n" or directly with "{"
        if stripped.startswith("json"):
            return stripped[len("json"):].strip()  # ← strip the "json" language tag
        if stripped.startswith("{") or stripped.startswith("["):
            return stripped  # ← already clean JSON
    return raw_text.strip()  # ← fallback: return as-is and let JSON parser handle it


# ============================================================
# SECTION 5 — ANALYSIS FUNCTIONS
# ============================================================

def summarize(client: anthropic.Anthropic, document: str) -> str:
    """Generate a 3 to 5 sentence summary of the document."""
    prompt = build_summary_prompt(document)
    return call_api(client, prompt, max_tokens=300)  # ← 3-5 sentences fits comfortably in 300 tokens


def extract_entities(client: anthropic.Anthropic, document: str) -> DocumentEntities:
    """
    Extract structured entities from the document.
    Returns a validated DocumentEntities pydantic object.
    Returns empty entities on parse failure.
    """
    prompt   = build_entity_prompt(document)
    raw_text = call_api(client, prompt, max_tokens=600)  # ← entity lists can be long
    raw_text = clean_json_response(raw_text)              # ← strip any accidental code fences

    try:
        data = json.loads(raw_text)          # ← parse JSON string to Python dict
        return DocumentEntities(**data)       # ← pydantic validates the shape and types
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Entity parsing failed: {e}]")
        print(f"[Raw output: {raw_text[:200] if raw_text else 'None'}]")
        return DocumentEntities(people=[], organizations=[], dates=[], key_topics=[])


def answer_question(client: anthropic.Anthropic,
                    document: str,
                    question: str) -> str:
    """Answer a specific question about the document."""
    prompt = build_qa_prompt(document, question)
    return call_api(client, prompt, max_tokens=400)  # ← answers are a few sentences at most


def generate_quiz(client: anthropic.Anthropic, document: str):
    """
    Generate a 5-question multiple-choice quiz about the document.
    Returns a validated Quiz pydantic object, or None on failure.
    """
    prompt   = build_quiz_prompt(document)
    raw_text = call_api(client, prompt, max_tokens=1500)  # ← quiz JSON with 5 questions is ~1000 tokens
    raw_text = clean_json_response(raw_text)               # ← strip code fences if present

    try:
        data = json.loads(raw_text)  # ← parse JSON string to Python dict
        return Quiz(**data)           # ← pydantic validates all 5 questions have correct structure
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[Warning: Quiz parsing failed: {e}]")
        print(f"[Raw output: {raw_text[:300] if raw_text else 'None'}]")
        return None


# ============================================================
# SECTION 6 — DISPLAY FUNCTIONS
# ============================================================

def display_entities(entities: DocumentEntities) -> None:
    """Print entities as formatted JSON."""
    print(entities.model_dump_json(indent=2))  # ← pydantic's built-in JSON serializer


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

        answer = answer_question(client, document, question)
        # ← answer_question builds the grounded prompt and calls the API
        print(f"\nAnswer: {answer}\n")


# ============================================================
# SECTION 8 — MAIN MENU LOOP
# ============================================================

def run_analyzer(filepath: str) -> None:
    """
    Main application: load document, present menu, execute chosen tasks.
    """
    client   = anthropic.Anthropic()         # ← reads ANTHROPIC_API_KEY automatically
    document = load_document(filepath)        # ← read and optionally truncate the file

    print("=" * 52)
    print("  Intelligent Document Analyzer")
    print(f"  Powered by Claude claude-opus-4-6")
    print("=" * 52)

    options = {
        "1": "Summarize",
        "2": "Extract Entities",
        "3": "Ask a Question",
        "4": "Generate Quiz",
        "5": "Run All (1 to 4)",
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
            print(summarize(client, document))  # ← 3-5 sentence grounded summary

        elif choice == "2":
            print("\n--- ENTITIES ---")
            entities = extract_entities(client, document)
            display_entities(entities)  # ← prints formatted JSON with all entity types

        elif choice == "3":
            run_qa_session(client, document)  # ← interactive loop until user types "done"

        elif choice == "4":
            print("\n--- QUIZ ---")
            quiz = generate_quiz(client, document)
            display_quiz(quiz)  # ← shows all 5 questions with answers and explanations

        elif choice == "5":
            print("\n--- [1] SUMMARY ---")
            print(summarize(client, document))

            print("\n--- [2] ENTITIES ---")
            entities = extract_entities(client, document)
            display_entities(entities)

            # [3] — Q&A is interactive so it runs as its own session
            run_qa_session(client, document)

            print("\n--- [4] QUIZ ---")
            quiz = generate_quiz(client, document)
            display_quiz(quiz)

        else:
            print("[Invalid choice. Please enter 1 to 5 or q.]")


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
