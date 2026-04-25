"""
Project 23 — Codebase Review Agent
Complete working solution.

Usage:
    python solution.py /path/to/codebase
    python solution.py /path/to/codebase --output ./reports/review.md
    python solution.py /path/to/codebase --skip-security
    python solution.py /path/to/codebase --model claude-haiku-4-5

Requirements:
    pip install anthropic python-dotenv
    ANTHROPIC_API_KEY in .env
"""

import os
import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Optional
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"

# Max chars sent to Claude per file to avoid context overflow
MAX_SOURCE_CHARS = 6000


# ---------------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------------

def _claude_json(prompt: str, max_tokens: int = 1024, default=None):
    """Call Claude and parse JSON response. Return default on failure."""
    if default is None:
        default = {}
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        return json.loads(text)
    except json.JSONDecodeError:
        return default
    except Exception as e:
        print(f"      API error: {e}")
        return default


# ---------------------------------------------------------------------------
# AGENT 1 — FILE DISCOVERY (pure Python + AST)
# ---------------------------------------------------------------------------

def find_python_files(codebase_path: str) -> list:
    """Find all .py files recursively, excluding __pycache__."""
    root = Path(codebase_path).resolve()
    files = [
        p for p in sorted(root.rglob("*.py"))
        if "__pycache__" not in str(p)
    ]
    return files


def analyze_file_with_ast(filepath: Path, root: Path) -> Optional[dict]:
    """Parse one Python file and extract structural metadata."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"      Warning: could not read {filepath}: {e}")
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"      Warning: syntax error in {filepath.name}: {e}")
        return None

    functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)
    ]
    classes = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    ]
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Check if any docstrings exist
    has_docstrings = any(
        ast.get_docstring(node) is not None
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module))
    )

    relative = str(filepath.relative_to(root))
    lines = source.count("\n") + 1

    return {
        "path": str(filepath),
        "relative_path": relative,
        "lines": lines,
        "source": source[:MAX_SOURCE_CHARS],
        "source_truncated": len(source) > MAX_SOURCE_CHARS,
        "functions": functions,
        "classes": classes,
        "imports": list(set(imports)),
        "has_docstrings": has_docstrings,
    }


def run_file_discovery(codebase_path: str) -> list:
    """Agent 1: Walk directory, parse all Python files. Returns FileManifest."""
    root = Path(codebase_path).resolve()
    files = find_python_files(codebase_path)

    if not files:
        return []

    manifest = []
    for fp in files:
        entry = analyze_file_with_ast(fp, root)
        if entry:
            manifest.append(entry)

    total_lines = sum(e["lines"] for e in manifest)
    total_functions = sum(len(e["functions"]) for e in manifest)
    total_classes = sum(len(e["classes"]) for e in manifest)
    all_imports = {imp for e in manifest for imp in e["imports"]}

    print(f"          Found {len(manifest)} Python files ({total_lines:,} lines total)")
    print(f"          {total_functions} functions, {total_classes} classes, "
          f"{len(all_imports)} unique imports")

    return manifest


# ---------------------------------------------------------------------------
# AGENT 2 — CODE QUALITY
# ---------------------------------------------------------------------------

def review_file_quality(file_entry: dict) -> dict:
    """Claude reviews one file for code quality. Returns one findings entry."""
    default = {
        "file": file_entry["relative_path"],
        "issues": [],
        "positives": [],
    }

    truncation_note = ""
    if file_entry.get("source_truncated"):
        truncation_note = f"\nNote: file was truncated to {MAX_SOURCE_CHARS} chars for review."

    prompt = f"""You are a senior software engineer conducting a code review.
Be specific. Reference actual function names and patterns you observe.
Return ONLY valid JSON — no markdown, no explanation.

File: {file_entry['relative_path']}
Lines: {file_entry['lines']}
Functions: {json.dumps(file_entry['functions'])}
Classes: {json.dumps(file_entry['classes'])}
Has docstrings: {file_entry['has_docstrings']}{truncation_note}

<source>
{file_entry['source']}
</source>

Review for:
1. Function length (>40 lines is a concern, >80 is a problem)
2. Naming conventions (PEP 8 compliance)
3. Docstring coverage (classes and public functions should have docstrings)
4. Obvious code duplication
5. Complexity (deeply nested conditions, long parameter lists)
6. Pythonic patterns (prefer list comprehensions, context managers, etc.)

Return JSON:
{{
  "file": "{file_entry['relative_path']}",
  "issues": [{{"severity": "low|medium|high", "description": "..."}}],
  "positives": ["..."]
}}

If no issues found, return empty "issues" list. Always include at least one positive."""

    result = _claude_json(prompt, max_tokens=800, default=default)
    # Ensure required keys exist
    result.setdefault("file", file_entry["relative_path"])
    result.setdefault("issues", [])
    result.setdefault("positives", [])
    return result


def run_quality_review(manifest: list) -> list:
    """Agent 2: Review each file for code quality."""
    findings = []
    for entry in manifest:
        print(f"          Reviewing {entry['relative_path']} ({entry['lines']} lines)...")
        result = review_file_quality(entry)
        findings.append(result)
    return findings


# ---------------------------------------------------------------------------
# AGENT 3 — SECURITY SCAN
# ---------------------------------------------------------------------------

def scan_file_security(file_entry: dict) -> dict:
    """Claude scans one file for security issues."""
    default = {"file": file_entry["relative_path"], "issues": []}

    prompt = f"""You are a security engineer doing an OWASP-based code review.
Be precise. Quote the vulnerable line or pattern when you find one.
Return ONLY valid JSON — no markdown, no explanation.

File: {file_entry['relative_path']}

<source>
{file_entry['source']}
</source>

Scan for:
1. Hardcoded secrets: passwords, API keys, tokens in string literals
2. SQL injection: string formatting or % used to build SQL queries
3. Command injection: subprocess with shell=True combined with user-controlled input
4. Dangerous functions: eval(), exec(), pickle.loads(), yaml.load() without Loader argument
5. Insecure deserialization
6. Missing input validation on data from os.environ, sys.argv, request objects
7. Debug mode enabled: debug=True, DEBUG=True in configuration
8. Broad exception handlers that silently swallow all exceptions

Return JSON:
{{
  "file": "{file_entry['relative_path']}",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "category": "hardcoded_secret|sql_injection|command_injection|dangerous_function|insecure_deserialization|missing_validation|debug_mode|silent_exception",
      "description": "...",
      "line_hint": null,
      "recommendation": "..."
    }}
  ]
}}

If no issues are found, return {{"file": "...", "issues": []}}
Do not report issues that are clearly not vulnerabilities (e.g. variable named 'password' in a test)."""

    result = _claude_json(prompt, max_tokens=800, default=default)
    result.setdefault("file", file_entry["relative_path"])
    result.setdefault("issues", [])
    return result


def run_security_scan(manifest: list) -> list:
    """Agent 3: Scan each file for security issues."""
    findings = []
    issue_count = 0
    for entry in manifest:
        result = scan_file_security(entry)
        findings.append(result)
        n = len(result.get("issues", []))
        issue_count += n
        if n > 0:
            print(f"          {entry['relative_path']}: {n} issue(s) found")
    if issue_count == 0:
        print("          No security issues detected.")
    return findings


# ---------------------------------------------------------------------------
# AGENT 4 — ARCHITECTURE ANALYSIS
# ---------------------------------------------------------------------------

def build_module_map(manifest: list) -> list:
    """Build compact structural summary (no source code)."""
    return [
        {
            "file": e["relative_path"],
            "imports": e["imports"],
            "classes": e["classes"],
            "functions": e["functions"],
        }
        for e in manifest
    ]


def build_import_graph(manifest: list) -> dict:
    """Build import adjacency graph: {relative_path: [imported relative_paths]}."""
    # Build a lookup: module-style name -> relative path
    path_to_module = {}
    for e in manifest:
        # Convert "src/models.py" -> "src.models" and "models"
        rp = e["relative_path"].replace(os.sep, ".").replace("/", ".").rstrip(".py")
        if rp.endswith(".py"):
            rp = rp[:-3]
        # Also store the stem only
        stem = Path(e["relative_path"]).stem
        path_to_module[rp] = e["relative_path"]
        path_to_module[stem] = e["relative_path"]

    graph = {e["relative_path"]: [] for e in manifest}
    for e in manifest:
        for imp in e["imports"]:
            # Check full import and stem
            for key in [imp, imp.split(".")[0]]:
                if key in path_to_module:
                    target = path_to_module[key]
                    if target != e["relative_path"] and target not in graph[e["relative_path"]]:
                        graph[e["relative_path"]].append(target)
    return graph


def find_cycles(graph: dict) -> list:
    """DFS-based cycle detection. Returns list of cycle paths."""
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: list):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle = path[cycle_start:] + [neighbor]
                # Avoid duplicate cycles
                if cycle not in cycles:
                    cycles.append(cycle)

        rec_stack.discard(node)

    for node in graph:
        if node not in visited:
            dfs(node, [node])

    return cycles


def run_architecture_analysis(manifest: list) -> dict:
    """Agent 4: Analyze module structure."""
    module_map = build_module_map(manifest)
    import_graph = build_import_graph(manifest)
    confirmed_cycles = find_cycles(import_graph)

    if confirmed_cycles:
        print(f"          Circular imports detected: {len(confirmed_cycles)}")
    else:
        print("          No circular imports detected.")

    default = {
        "circular_imports": confirmed_cycles,
        "god_classes": [],
        "missing_abstractions": [],
        "tight_coupling": [],
        "module_observations": [],
    }

    prompt = f"""You are a software architect reviewing a Python codebase's structure.
Analyze module-level patterns only — not line-level issues.
Return ONLY valid JSON.

<module_map>
{json.dumps(module_map, indent=2)}
</module_map>

<confirmed_circular_imports>
{json.dumps(confirmed_cycles)}
</confirmed_circular_imports>

Analyze for:
1. God classes: classes with many methods that appear to span multiple responsibilities
2. Missing abstraction layers: e.g., DB queries mixed into route handlers
3. Tight coupling: modules with an unusually high number of internal imports
4. Single Responsibility Principle violations at the module level

Return JSON:
{{
  "circular_imports": {json.dumps(confirmed_cycles)},
  "god_classes": [{{"class": "...", "file": "...", "method_count": 0, "description": "..."}}],
  "missing_abstractions": ["..."],
  "tight_coupling": ["..."],
  "module_observations": ["...positive or neutral structural observations..."]
}}

Use the confirmed_circular_imports exactly as provided in your response.
Be specific — reference actual class and file names from the module map."""

    result = _claude_json(prompt, max_tokens=1200, default=default)
    # Ensure confirmed cycles are included even if Claude missed them
    result["circular_imports"] = confirmed_cycles
    result.setdefault("god_classes", [])
    result.setdefault("missing_abstractions", [])
    result.setdefault("tight_coupling", [])
    result.setdefault("module_observations", [])
    return result


# ---------------------------------------------------------------------------
# AGENT 5 — REPORT SYNTHESIS
# ---------------------------------------------------------------------------

def count_by_severity(findings_list: list, findings_key: str) -> dict:
    """Count issues by severity across all files."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings_list:
        for issue in f.get(findings_key, []):
            sev = issue.get("severity", "low").lower()
            if sev in counts:
                counts[sev] += 1
    return counts


def run_report_synthesis(manifest: list, quality: list,
                         security: list, arch: dict,
                         output_path: str) -> str:
    """Agent 5: Synthesize all findings into a Markdown report."""
    total_lines = sum(e["lines"] for e in manifest)
    total_functions = sum(len(e["functions"]) for e in manifest)
    total_classes = sum(len(e["classes"]) for e in manifest)

    quality_severity = count_by_severity(quality, "issues")
    security_severity = count_by_severity(security, "issues")

    total_critical = security_severity["critical"] + security_severity["high"]
    total_quality_issues = sum(quality_severity.values())

    stats = {
        "total_files": len(manifest),
        "total_lines": total_lines,
        "total_functions": total_functions,
        "total_classes": total_classes,
        "quality_issues": quality_severity,
        "security_issues": security_severity,
        "circular_imports": len(arch.get("circular_imports", [])),
        "god_classes": len(arch.get("god_classes", [])),
    }

    prompt = f"""You are a technical lead writing a formal code review report.
Be direct. Prioritize by impact. No filler sentences.
Return the complete Markdown report — nothing else.

<file_stats>
{json.dumps(stats, indent=2)}
</file_stats>

<quality_findings>
{json.dumps(quality, indent=2)}
</quality_findings>

<security_findings>
{json.dumps(security, indent=2)}
</security_findings>

<architecture_findings>
{json.dumps(arch, indent=2)}
</architecture_findings>

Write a Markdown report with EXACTLY these sections in this order:

# Code Review Report
**Codebase reviewed:** [infer from findings context]
**Date:** {date.today().isoformat()}
**Files reviewed:** {len(manifest)} | **Lines:** {total_lines:,} | **Functions:** {total_functions} | **Classes:** {total_classes}

---

## Executive Summary
One paragraph. State the overall quality score (1-10) and justify it in 2-3 sentences.
Use this scale:
  9-10: Production-ready, minor style issues only
  7-8:  Good quality, a few medium issues, no critical issues
  5-6:  Functional but needs work, multiple medium issues
  3-4:  Significant problems, high-severity bugs or security issues
  1-2:  Critical issues, not safe to deploy

---

## Critical Issues
Security vulnerabilities and correctness bugs only. Must fix before deployment.
For each issue: file path, description, and a specific recommendation.
If none, write "No critical issues found."

---

## Improvement Suggestions
Ranked highest impact first. Include code quality and architecture issues.
For each: what the issue is, which file(s), and a concrete recommendation.

---

## Architecture Observations
Module-level patterns, structural issues, design recommendations.
Reference specific file names and class names.

---

## Positive Patterns
What is done well. Be specific — name the files or patterns.
At least 3 positives. If the code is genuinely poor, note good intentions or isolated good patterns.

---

Write clean, readable Markdown. Use bullet points and sub-headers within sections.
Include short code snippets only when they make a finding clearer."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        report = response.content[0].text.strip()
    except Exception as e:
        print(f"      Warning: report synthesis failed: {e}")
        report = f"# Code Review Report\n\nError generating report: {e}"

    # Write to file
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"          {report.count(chr(10))+1} lines written.")

    # Extract quality score for summary
    score_line = ""
    for line in report.split("\n"):
        if "/10" in line and ("score" in line.lower() or "quality" in line.lower()):
            score_line = line.strip()
            break

    print(f"\nReview complete.")
    if score_line:
        print(f"  {score_line}")
    print(f"  Critical security issues: {total_critical}")
    print(f"  Quality issues: {total_quality_issues}")

    return report


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def run_review(codebase_path: str, output_path: str,
               skip_security: bool = False) -> None:
    print("\nCodebase Review Agent")
    print("=" * 40)
    print(f"Target: {Path(codebase_path).resolve()}\n")

    print("[Agent 1] File Discovery...")
    manifest = run_file_discovery(codebase_path)
    if not manifest:
        print("No Python files found. Check the path.")
        return

    print(f"\n[Agent 2] Code Quality Review...")
    quality_findings = run_quality_review(manifest)

    if not skip_security:
        print(f"\n[Agent 3] Security Scan...")
        security_findings = run_security_scan(manifest)
    else:
        security_findings = []
        print("[Agent 3] Security scan skipped (--skip-security).")

    print(f"\n[Agent 4] Architecture Analysis...")
    arch_findings = run_architecture_analysis(manifest)

    print(f"\n[Agent 5] Synthesizing report...")
    run_report_synthesis(
        manifest, quality_findings, security_findings, arch_findings, output_path
    )

    print(f"\nReport: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Codebase Review Agent — multi-agent code review powered by Claude"
    )
    parser.add_argument("codebase_path", help="Path to the codebase directory to review")
    parser.add_argument(
        "--output", default="code_review_report.md",
        help="Output path for the review report (default: code_review_report.md)"
    )
    parser.add_argument(
        "--skip-security", action="store_true",
        help="Skip the security scan (faster, cheaper)"
    )
    parser.add_argument(
        "--model", default="claude-opus-4-5",
        help="Claude model ID (default: claude-opus-4-5)"
    )
    args = parser.parse_args()

    global MODEL
    MODEL = args.model

    if not os.path.isdir(args.codebase_path):
        print(f"Error: '{args.codebase_path}' is not a directory.")
        sys.exit(1)

    try:
        run_review(args.codebase_path, args.output, args.skip_security)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
