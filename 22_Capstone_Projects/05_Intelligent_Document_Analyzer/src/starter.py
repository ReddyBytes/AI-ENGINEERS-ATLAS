"""
Project 5 — Intelligent Document Analyzer
==========================================
Analyzes text documents using Claude with 4 capabilities:
  1. Summarize the document
  2. Extract structured entities as JSON
  3. Answer questions about the document
  4. Generate a 5-question comprehension quiz

Usage:
    python starter.py path/to/document.txt

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

    # TODO: Check if content is longer than max_chars and truncate if needed.
    # If len(content) > max_chars:
    #   print a warning: f"[Warning: Document truncated from {len(content):,} to {max_chars:,} characters]"
    #   content = content[:max_chars]

    print(f"Document loaded: {filepath} ({len(content):,} characters)\n")
    return content


# ============================================================
# SECTION 3 — PROMPT BUILDERS
# ============================================================

def build_summary_prompt(document: str) -> str:
    """
    Build a prompt that instructs the model to summarize the document
    in 3 to 5 sentences using only information from the document.

    Key requirements:
    - Specify 3 to 5 sentences explicitly  ← controls output length
    - Focus areas: main topic, key findings, context
    - Anti-hallucination: "Only include information explicitly stated"
    - End with "SUMMARY:" so the model knows where to begin its response
    """
    # TODO: Write the summary prompt.
    # Use this structure:
    #   instructions
    #   DOCUMENT:
    #   {document}
    #   SUMMARY:
    # See 03_GUIDE.md Stage 2 for the full template.
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

    Key requirements:
    - Show the exact JSON schema in the prompt  ← model needs a template
    - "Return ONLY valid JSON with no other text"  ← prevents prose wrapping
    - "Do not add entities not mentioned"  ← anti-hallucination instruction
    - End with "JSON:" so the model knows what to produce

    Note: use {{ and }} (double braces) in f-strings to produce literal { }
    """
    # TODO: Write the entity extraction prompt.
    # Show the exact JSON schema inline.
    # See 03_GUIDE.md Stage 3 for the full template.
    prompt = None  # TODO: replace with your prompt string
    return prompt


def build_qa_prompt(document: str, question: str) -> str:
    """
    Build a prompt for answering a specific question about the document.

    Key requirements:
    - Three-case rule:
        1. Answer is explicit → answer with citation
        2. Answer is implied  → state it is an inference
        3. Not enough info    → say exactly "The document does not contain enough information..."
    - "Do NOT use knowledge from outside the document"  ← anti-hallucination
    - Embed both {document} and {question} in the prompt
    - End with "ANSWER:"
    """
    # TODO: Write the Q&A prompt.
    # See 03_GUIDE.md Stage 4 for the full template.
    prompt = None  # TODO: replace with your prompt string
    return prompt


def build_quiz_prompt(document: str) -> str:
    """
    Build a prompt that generates 5 multiple-choice questions
    as JSON matching the Quiz/QuizQuestion schema.

    Key requirements:
    - Show the exact nested JSON schema  ← harder than flat schema
    - "Generate exactly 5 questions"  ← enforces count
    - "Exactly 4 choices labeled A through D"  ← enforces structure
    - "Return ONLY valid JSON with no other text"
    - All questions must come from the document content
    - End with "JSON:"
    """
    # TODO: Write the quiz generation prompt.
    # Include the full nested JSON schema as an example.
    # See 03_GUIDE.md Stage 5 for the full template.
    prompt = None  # TODO: replace with your prompt string
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
    # TODO: Call client.messages.create with:
    #   model="claude-opus-4-6"
    #   max_tokens=max_tokens
    #   messages=[{"role": "user", "content": prompt}]
    # Return response.content[0].text.strip()
    response = None  # TODO: replace with the actual API call
    return response


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

    # TODO: Extract JSON from between the backtick fences.
    # Split on "```", find the part that starts with "json" or "{"
    # Strip the "json" prefix if present.
    cleaned = raw_text  # TODO: replace with your extraction logic
    return cleaned.strip()


# ============================================================
# SECTION 5 — ANALYSIS FUNCTIONS
# ============================================================

def summarize(client: anthropic.Anthropic, document: str) -> str:
    """Generate a 3 to 5 sentence summary of the document."""
    # TODO: Build prompt with build_summary_prompt(document)
    # Call call_api with max_tokens=300  ← 3-5 sentences fits in 300 tokens
    # Return the result
    prompt = None  # TODO: build_summary_prompt(document)
    return None    # TODO: call_api(client, prompt, max_tokens=300)


def extract_entities(client: anthropic.Anthropic, document: str) -> DocumentEntities:
    """
    Extract structured entities from the document.
    Returns a validated DocumentEntities pydantic object.
    Returns empty entities on parse failure.
    """
    # TODO: Build prompt with build_entity_prompt(document)
    prompt = None  # TODO

    # TODO: Call call_api with max_tokens=600
    raw_text = None  # TODO

    # TODO: Clean the response with clean_json_response(raw_text)
    raw_text = None  # TODO: clean_json_response(raw_text)

    # TODO: Parse with json.loads(), then DocumentEntities(**data)
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
    # TODO: Build prompt with build_qa_prompt(document, question)
    # Call call_api with max_tokens=400
    # Return the result
    prompt = None   # TODO
    return None     # TODO: call_api(client, prompt, max_tokens=400)


def generate_quiz(client: anthropic.Anthropic, document: str):
    """
    Generate a 5-question multiple-choice quiz about the document.
    Returns a validated Quiz pydantic object, or None on failure.
    """
    # TODO: Build prompt with build_quiz_prompt(document)
    prompt = None  # TODO

    # TODO: Call call_api with max_tokens=1500  ← quiz JSON is large
    raw_text = None  # TODO

    # TODO: Clean with clean_json_response, then parse and validate
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

        # TODO: Call answer_question(client, document, question) and print the result
        answer = None  # TODO: answer_question(client, document, question)
        print(f"\nAnswer: {answer}\n")


# ============================================================
# SECTION 8 — MAIN MENU LOOP
# ============================================================

def run_analyzer(filepath: str) -> None:
    """
    Main application: load document, present menu, execute chosen tasks.
    """
    # TODO: Create the Anthropic client
    client = None  # TODO: anthropic.Anthropic()

    # TODO: Load the document using load_document(filepath)
    document = None  # TODO: load_document(filepath)

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
            # TODO: Call summarize(client, document) and print the result
            print(None)  # TODO

        elif choice == "2":
            print("\n--- ENTITIES ---")
            # TODO: Call extract_entities(client, document) then display_entities()
            pass  # TODO

        elif choice == "3":
            # TODO: Call run_qa_session(client, document)
            pass  # TODO

        elif choice == "4":
            print("\n--- QUIZ ---")
            # TODO: Call generate_quiz(client, document) then display_quiz()
            pass  # TODO

        elif choice == "5":
            print("\n--- [1] SUMMARY ---")
            # TODO: Run all 4 analyses in sequence:
            # 1. summarize and print
            # 2. extract_entities and display_entities
            # 3. run_qa_session
            # 4. generate_quiz and display_quiz
            pass  # TODO

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
