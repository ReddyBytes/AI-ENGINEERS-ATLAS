"""
Project 23 — Codebase Review Agent
Starter skeleton with function contracts.

Your job: implement every function marked TODO.
The contracts (inputs, outputs, types) are defined. Do not change them.

Run: python starter.py /path/to/your/codebase
"""

import os
import ast
import json
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import anthropic

load_dotenv()

# TODO: Initialize the Anthropic client
client = None  # Replace with real client

MODEL = "claude-opus-4-5"


# ---------------------------------------------------------------------------
# TYPE ALIASES (for documentation purposes)
# ---------------------------------------------------------------------------
# FileManifest:      list of dicts (see Agent 1 contract in Architecture file)
# QualityFindings:   list of dicts (see Agent 2 contract)
# SecurityFindings:  list of dicts (see Agent 3 contract)
# ArchFindings:      single dict  (see Agent 4 contract)


# ---------------------------------------------------------------------------
# AGENT 1 — FILE DISCOVERY (no Claude)
# ---------------------------------------------------------------------------

def find_python_files(codebase_path: str) -> list:
    """
    Walk the directory tree and return all .py file paths.

    TODO: Use pathlib.Path.rglob("*.py") to find all Python files.
    Exclude __pycache__ directories.
    Return sorted list of Path objects.
    """
    pass


def analyze_file_with_ast(filepath: Path, root: Path) -> Optional[dict]:
    """
    Parse a single Python file with ast and return its manifest entry.

    TODO: Return a dict with keys:
      path (str), relative_path (str), lines (int), source (str),
      functions (list of str), classes (list of str),
      imports (list of str), has_docstrings (bool)

    - Use ast.parse() to build the tree
    - Walk tree nodes to extract FunctionDef, ClassDef, Import, ImportFrom
    - has_docstrings = True if at least one class or function has a docstring
    - If ast.parse() raises SyntaxError, print warning and return None
    - Truncate source to 6000 chars for Claude safety (keep full source in dict as "source_full")
    """
    pass


def run_file_discovery(codebase_path: str) -> list:
    """
    Agent 1 entry point. Returns FileManifest.

    TODO: Call find_python_files(), then analyze_file_with_ast() for each.
    Skip None results. Print summary stats.
    """
    pass


# ---------------------------------------------------------------------------
# AGENT 2 — CODE QUALITY (Claude, one call per file)
# ---------------------------------------------------------------------------

def review_file_quality(file_entry: dict) -> dict:
    """
    Claude reviews one file for code quality. Returns one QualityFindings entry.

    TODO: Build the quality review prompt (see Architecture file).
    Call Claude. Parse JSON response.
    On failure, return {"file": file_entry["relative_path"], "issues": [], "positives": []}
    """
    pass


def run_quality_review(manifest: list) -> list:
    """
    Agent 2 entry point. Calls review_file_quality() for each file.
    Returns list of QualityFindings entries.

    TODO: Iterate, print progress per file, collect results.
    """
    pass


# ---------------------------------------------------------------------------
# AGENT 3 — SECURITY SCAN (Claude, one call per file)
# ---------------------------------------------------------------------------

def scan_file_security(file_entry: dict) -> dict:
    """
    Claude scans one file for security issues. Returns one SecurityFindings entry.

    TODO: Build the security scan prompt (see Architecture file).
    Call Claude. Parse JSON response.
    On failure, return {"file": file_entry["relative_path"], "issues": []}
    """
    pass


def run_security_scan(manifest: list) -> list:
    """
    Agent 3 entry point. Returns list of SecurityFindings entries.
    Only report files that have at least one issue in the output summary.
    """
    pass


# ---------------------------------------------------------------------------
# AGENT 4 — ARCHITECTURE ANALYSIS (Claude, one call total)
# ---------------------------------------------------------------------------

def build_module_map(manifest: list) -> list:
    """
    Build a compact module map from FileManifest for the architecture prompt.

    TODO: Return list of dicts:
      [{"file": relative_path, "imports": [...], "classes": [...], "functions": [...]}]
    Do NOT include source code — this is a structural summary only.
    """
    pass


def find_cycles(import_graph: dict) -> list:
    """
    DFS-based cycle detection in the import graph.

    import_graph: {relative_path: [list of imported relative_paths that exist in manifest]}

    TODO: Implement DFS. Return list of cycle paths (each path is a list of strings).
    """
    pass


def build_import_graph(manifest: list) -> dict:
    """
    Build the import adjacency graph from manifest.
    Keys: relative_path. Values: list of other manifest files this one imports.

    TODO: For each file, check its imports list. If an import name maps to
    another file in the manifest (convert dots to path separators), add an edge.
    """
    pass


def run_architecture_analysis(manifest: list) -> dict:
    """
    Agent 4 entry point.

    TODO:
    1. Build module map (no Claude)
    2. Build import graph and detect cycles (no Claude)
    3. Call Claude with module map + confirmed cycles for God class / abstraction analysis
    4. Merge Claude's output with cycle findings
    5. Return ArchFindings dict
    """
    pass


# ---------------------------------------------------------------------------
# AGENT 5 — REPORT SYNTHESIS (Claude, one call total)
# ---------------------------------------------------------------------------

def run_report_synthesis(manifest: list, quality: list,
                         security: list, arch: dict,
                         output_path: str) -> str:
    """
    Agent 5 entry point. Returns the Markdown report string and writes to output_path.

    TODO:
    1. Compute summary stats (total files, lines, functions, classes, critical issues, etc.)
    2. Build the synthesis prompt with all findings as JSON
    3. Call Claude with max_tokens=4096
    4. Write result to output_path
    5. Return the Markdown string
    """
    pass


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def run_review(codebase_path: str, output_path: str,
               skip_security: bool = False) -> None:
    print("\nCodebase Review Agent")
    print("=" * 40)
    print(f"Target: {codebase_path}\n")

    print("[Agent 1] File Discovery...")
    manifest = run_file_discovery(codebase_path)
    if not manifest:
        print("No Python files found.")
        return

    print(f"\n[Agent 2] Code Quality Review...")
    quality_findings = run_quality_review(manifest)

    if not skip_security:
        print(f"\n[Agent 3] Security Scan...")
        security_findings = run_security_scan(manifest)
    else:
        security_findings = []
        print("[Agent 3] Security scan skipped.")

    print(f"\n[Agent 4] Architecture Analysis...")
    arch_findings = run_architecture_analysis(manifest)

    print(f"\n[Agent 5] Synthesizing report...")
    report = run_report_synthesis(
        manifest, quality_findings, security_findings, arch_findings, output_path
    )

    print(f"\nReport written to: {output_path}")
    print("\nReview complete.")


def main():
    parser = argparse.ArgumentParser(description="Codebase Review Agent")
    parser.add_argument("codebase_path", help="Path to the codebase directory")
    parser.add_argument("--output", default="code_review_report.md",
                        help="Output report path (default: code_review_report.md)")
    parser.add_argument("--skip-security", action="store_true",
                        help="Skip security scan")
    parser.add_argument("--model", default="claude-opus-4-5",
                        help="Claude model to use")
    args = parser.parse_args()

    global MODEL
    MODEL = args.model

    if not os.path.isdir(args.codebase_path):
        print(f"Error: {args.codebase_path} is not a directory.")
        return

    run_review(args.codebase_path, args.output, args.skip_security)


if __name__ == "__main__":
    main()
