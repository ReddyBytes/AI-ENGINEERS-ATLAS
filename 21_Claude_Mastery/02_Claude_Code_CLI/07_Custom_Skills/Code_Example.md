# Custom Skills — Code Examples

## Example 1: A debugging skill

```markdown
# File: ~/.claude/skills/debugger.md
---
description: Structured debugger for any backend service — pod failures, crashes, errors
usage: /debugger
when_to_use: When a service is failing, crashing, or producing unexpected results
allowed_tools:
  - Bash
  - Read
  - Grep
---

## Debugging Philosophy
Always read before acting. Never restart services before reading logs — you lose context.
Narrow from system → service → component → specific error.

## Approach
1. Establish what's happening (symptoms)
2. Establish what should be happening (expected behavior)
3. Narrow the scope (where is the divergence?)
4. Form a hypothesis
5. Verify the hypothesis with a targeted action
6. Fix and verify

## Information Gathering
Always collect before diagnosing:
- Service logs (last 200 lines)
- Recent changes (git log --oneline -20)
- Resource status (memory, disk, connections)
- Error messages (exact text, not paraphrase)

## Decision Framework
- If "connection refused": check if the target service is running, check network config
- If "permission denied": check file/directory permissions and user/group
- If "timeout": check if target is slow vs unreachable; check load
- If "not found": check if resource exists; check path/name spelling; check environment

## Anti-Patterns
- Do NOT restart before reading logs
- Do NOT assume the error message is the root cause
- Do NOT fix symptoms; find the cause
- Do NOT change multiple things at once; change one, verify, then the next

## Output Format
Organize findings as:
1. **Symptom:** [what's failing]
2. **Evidence:** [log lines, error messages]
3. **Root cause:** [diagnosis]
4. **Fix:** [proposed change]
5. **Verification:** [how to confirm the fix worked]
```

---

## Example 2: A learning skill

```markdown
# File: ~/.claude/skills/learn-topic.md
---
description: Interactively teach any topic and save learning files to a repo
usage: /learn-topic <topic>
when_to_use: When the user wants to learn a new technical concept interactively
---

## Teaching Philosophy
Story first, jargon second. Every concept gets a real-world analogy before
technical terms. The goal is understanding, not just information transfer.

## Teaching Flow
1. Start with a real-world analogy (2-3 sentences, no jargon)
2. Transition: "This is why we need X" — one sentence connecting analogy to concept
3. Formal definition with key terms bolded
4. How it works (with Mermaid diagram if architectural)
5. Where you see it in real systems (name actual tools/products)
6. Common mistakes and misconceptions
7. 3 questions at Beginner / Intermediate / Advanced levels

## Format Rules
- Bold key terms on first use
- Mermaid diagrams for architecture and data flows
- Bullet points for lists, never numbered unless order matters
- Concrete examples always — "For example, in FastAPI..." beats "For example..."
- Keep sections under 300 words

## After Teaching
Ask: "Ready to save this as a Theory.md file?"
If yes: save to the appropriate repo path following the repo's naming conventions.
Read MEMORY.md to find the correct repo path and naming conventions.
```

---

## Example 3: A code review skill

```markdown
# File: ~/.claude/skills/code-review.md
---
description: Structured code review with severity-ranked findings
usage: /code-review
when_to_use: When reviewing a PR, diff, or new feature for quality and correctness
---

## Review Framework
Review in this order (most critical to least):
1. **Correctness** — does the logic actually do what it claims?
2. **Security** — are there injection, auth, or exposure risks?
3. **Error handling** — what happens when things fail?
4. **Performance** — any obvious bottlenecks or N+1 queries?
5. **Maintainability** — will the next engineer understand this?
6. **Style** — naming, structure, conventions

## Severity Levels
- **Critical:** Will break in production. Must fix before merge.
- **Major:** High risk of failure or security issue. Should fix.
- **Minor:** Code quality or style. Nice to fix.
- **Note:** Observation or suggestion. Optional.

## What to Look For

### Security
- Hardcoded credentials or tokens
- SQL concatenation (potential injection)
- Unvalidated user input in dangerous operations
- Insecure defaults (world-readable files, open CORS, etc.)

### Correctness
- Off-by-one errors in loops
- Missing null/None checks
- Race conditions in concurrent code
- Incorrect error propagation

### Error Handling
- Bare `except` clauses
- Silent failures (errors caught but not logged)
- Missing cleanup on failure paths (file handles, DB connections)

## Output Format
List findings by severity. For each:
- File:line reference
- Severity level
- What the issue is
- Why it matters
- Suggested fix
```

---

## Example 4: A deployment skill

```markdown
# File: myproject/.claude/skills/deploy.md
---
description: Deploy myproject to staging or production
usage: /deploy <environment>
when_to_use: When deploying a new version of the service
allowed_tools:
  - Bash
  - Read
---

## Environments
- `staging` — AWS EKS staging cluster, `myapp-staging` namespace
- `production` — AWS EKS prod cluster, `myapp-prod` namespace

## Pre-Deploy Checklist
Before proceeding with $ARGUMENTS environment:
1. Run `pytest tests/ -q` — all tests must pass
2. Run `ruff check .` — no linting errors
3. Verify `git status` — no uncommitted changes
4. For production: confirm version bump in `pyproject.toml`

## Deploy Steps
1. Build image: `docker build -t myapp:$(git rev-parse --short HEAD) .`
2. Push to ECR: `aws ecr get-login-password | docker login ... && docker push ...`
3. Update Helm values in `deploy/<environment>/values.yaml`
4. Run: `helm upgrade myapp deploy/chart -f deploy/$ARGUMENTS/values.yaml`
5. Watch rollout: `kubectl rollout status deployment/myapp -n myapp-$ARGUMENTS`

## Rollback
If deploy fails: `helm rollback myapp -n myapp-$ARGUMENTS`
Always check pod logs after rollback to understand the root cause.

## Post-Deploy Verification
1. Check pod health: `kubectl get pods -n myapp-$ARGUMENTS`
2. Run smoke tests: `pytest tests/smoke/ -v`
3. Check error rate in CloudWatch for 5 minutes
```

---

## Example 5: Invoking and using skills

```bash
claude

# Load a skill
> /debugger
# Claude reads debugger.md and confirms readiness:
# "Debugger skill loaded. I'll approach this systematically: read before act,
#  narrow scope, hypothesis → test. What's failing?"

# Now work within that mental model
> The payment service is returning 500 errors randomly
# Claude follows the skill's approach: gathers evidence first, then narrows

# Load a different skill mid-session
> /clear
> /code-review
# Claude loads code review skill
> Review the changes in the last commit
# Claude follows the review framework from the skill
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [CLAUDE.md and Settings](../06_CLAUDE_md_and_Settings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Hooks](../08_Hooks/Theory.md)
