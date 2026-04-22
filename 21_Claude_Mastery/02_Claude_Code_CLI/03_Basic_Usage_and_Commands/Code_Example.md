# Basic Usage and Commands — Code Examples

## Example 1: Reading and asking questions

```bash
cd ~/myproject

# Start Claude Code
claude

# Ask about project structure (read-only, no permission prompts)
> What is the overall structure of this codebase?
> What does src/auth/jwt_handler.py do?
> Show me all the places where the database connection is used

# Find something specific
> List all API endpoints and their HTTP methods
> What environment variables does this app require?
```

---

## Example 2: Requesting a file edit

```bash
# In Claude Code session

> Add input validation to the register() function in src/api/users.py

# Claude responds with a diff:
# --- src/api/users.py
# +++ src/api/users.py
# @@ -15,6 +15,14 @@
#  def register(email: str, password: str):
# +    if not email or "@" not in email:
# +        raise ValueError("Invalid email address")
# +    if len(password) < 8:
# +        raise ValueError("Password must be at least 8 characters")
#     db.create_user(email, password)

# You type: y  (to approve)
# Claude applies the edit
```

---

## Example 3: Running shell commands

```bash
# Ask Claude to run tests
> Run the test suite and tell me what's failing

# Claude shows:
# Claude Code wants to run: pytest tests/ -v
# Allow? [y/n/a]

# You type: y
# Claude runs pytest, reads the output, reports failures

# Then ask for fixes
> Fix the first failing test

# Then verify
> Run the tests again
```

---

## Example 4: Non-interactive --print mode

```bash
# Simple query to stdout
claude --print "What does config.py contain?"

# Save output to file
claude --print "List all TODO comments in the codebase" > todos.txt

# Use in a bash script
#!/bin/bash
ISSUES=$(claude --print "Check for obvious security issues in src/auth.py")
if [ -n "$ISSUES" ]; then
    echo "Security review findings:"
    echo "$ISSUES"
    exit 1
fi
echo "No issues found"

# Use in Makefile
review:
    claude --print "Review the changes in the last commit for bugs"
```

---

## Example 5: Multi-step conversation

```bash
claude

# Step 1: Explore
> Show me the current database models

# Step 2: Plan
> I want to add a UserProfile model that links to User — what changes would be needed?

# Step 3: Act
> Make those changes

# Step 4: Verify
> Run the migrations and then run the tests

# Step 5: Iterate
> The test_user_profile_creation test is failing — fix it
```

---

## Example 6: Scoped and precise instructions

```bash
# Too vague — avoid
> Fix the authentication

# Better — scoped
> In src/auth/jwt_handler.py, the verify_token() function doesn't handle expired tokens.
> Add proper handling that raises an AuthError with message "Token expired"

# Verify scope before acting
> Show me all functions that call verify_token() before you make any changes

# Then act
> Now add the expired token handling
```

---

## Example 7: Pre-approving safe tools in settings.json

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git log --oneline *)",
      "Bash(git diff *)",
      "Bash(pytest tests/ *)",
      "Bash(python -m mypy src/)",
      "Bash(ruff check .)",
      "Bash(ruff format --check .)"
    ],
    "deny": [
      "Bash(git push *)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(pip install *)"
    ]
  }
}
```

With this config, Claude can run tests, linting, and read git info without any prompts — but can't push code, delete files, or install packages without your explicit approval.

---

## Example 8: Resume a conversation

```bash
# First session — start a complex task
claude
> Start a refactor of the authentication module

# [You close terminal mid-task]

# Next day — resume
claude --continue
# Claude loads previous conversation and continues

# Or resume a specific session
claude --list-sessions
# Shows recent session IDs

claude --resume abc123def
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

⬅️ **Prev:** [Installation and Setup](../02_Installation_and_Setup/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Slash Commands](../04_Slash_Commands/Theory.md)
