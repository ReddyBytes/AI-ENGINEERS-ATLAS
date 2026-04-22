# Installation and Setup — Code Examples

## Full Setup Walkthrough

### 1. Check prerequisites

```bash
node --version
# Should output v18.x.x or higher

npm --version
# Should output 8.x.x or higher
```

If Node is too old:
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 20
nvm use 20
node --version   # v20.x.x
```

---

### 2. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
# claude 1.x.x

claude --help
# Displays all available flags
```

---

### 3. API Key Authentication (recommended for teams)

```bash
# Add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxx"

# Reload shell
source ~/.zshrc

# Verify
echo $ANTHROPIC_API_KEY
# sk-ant-api03-xxxxxxxxxx

# Launch Claude Code
claude
```

---

### 4. OAuth Authentication (for individuals)

```bash
# Just run claude — it prompts automatically on first run
claude
# > No credentials found. Authenticate?
# > [1] Open browser (OAuth)
# > [2] Enter API key manually
# Select 1 → browser opens → log in → credentials saved
```

---

### 5. Create a minimal CLAUDE.md

```bash
cat > ~/.claude/CLAUDE.md << 'EOF'
# Global CLAUDE.md

## My Setup
- Primary language: Python 3.11+
- Style: PEP8, type hints everywhere
- Testing: pytest
- Never use print() for debugging — use logging

## Workflow Rules
- Always run tests before marking a task complete
- Prefer editing existing files over creating new ones
- Ask before deleting any file
EOF
```

---

### 6. Create project-level config

```bash
cd ~/myproject

# Create CLAUDE.md for project context
cat > CLAUDE.md << 'EOF'
# My FastAPI Project

## Stack
- FastAPI + SQLAlchemy + PostgreSQL
- Tests: pytest + httpx
- Linting: ruff + mypy

## Commands
- Run tests: `pytest tests/ -v`
- Start server: `uvicorn app.main:app --reload`
- Format code: `ruff format .`

## Conventions
- All endpoints in `app/routers/`
- DB models in `app/models/`
- Business logic in `app/services/`
EOF

# Create .claude directory and settings
mkdir -p .claude

cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(pytest *)",
      "Bash(ruff *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)"
    ]
  }
}
EOF
```

---

### 7. First project task

```bash
cd ~/myproject

# Interactive mode
claude
# > Hello! I can see this is a FastAPI project...
# > What would you like to work on?

# Or non-interactive
claude --print "List all the API endpoints in this project"

# Resume last session
claude --continue
```

---

### 8. CI/CD usage

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Run review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --print "Review the changes in this PR for bugs and suggest improvements. Focus on the diff: $(git diff HEAD~1)"
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

⬅️ **Prev:** [What is Claude Code](../01_What_is_Claude_Code/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Basic Usage and Commands](../03_Basic_Usage_and_Commands/Theory.md)
