# Basic Usage and Commands — Interview Q&A

## Beginner 🟢

**Q1: How do you run Claude Code in non-interactive mode?**

<details>
<summary>💡 Show Answer</summary>

Use the `--print` flag followed by your task:
```bash
claude --print "What files are in the src/ directory?"
```
This runs the task, prints the result to stdout, and exits. No interactive prompts. This mode requires all needed tool permissions to be pre-approved in `settings.json`, since there's no user to prompt.

</details>

---

<br>

**Q2: What happens when Claude Code wants to edit a file?**

<details>
<summary>💡 Show Answer</summary>

Claude shows you a unified diff of the proposed changes and prompts: `Allow this edit? [y/n/a/d]`. You can approve (`y`), reject (`n`), auto-approve all future edits this session (`a`), or view the full diff (`d`) before deciding. Claude never modifies files silently by default.

</details>

---

<br>

**Q3: What kinds of requests don't require any permission prompts?**

<details>
<summary>💡 Show Answer</summary>

Read-only operations — reading files, listing directories, searching content with glob/grep — never require approval because they don't change your system. Permission prompts appear only for writes (file edits, new files), shell command execution, and network requests.

</details>

---

## Intermediate 🟡

**Q4: How does the permission system work and what are the three states a tool can be in?**

<details>
<summary>💡 Show Answer</summary>

Every tool action falls into one of three states: auto-approved (listed in `permissions.allow` in settings.json — executes silently), blocked (listed in `permissions.deny` — always rejected and reported), or prompted (everything else — Claude pauses and asks before executing). You configure the allow/deny lists per project or globally to match your risk tolerance.

</details>

---

<br>

**Q5: How do you build a multi-step verification workflow in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

Chain tasks naturally in conversation. For example: "Refactor the login function" → [Claude edits] → "Now run the tests" → [Claude runs pytest] → "The test_session_timeout test is still failing — fix it" → [Claude reads error, iterates]. Because Claude remembers the full conversation context, it can connect cause and effect across multiple turns. You can also write a single compound instruction: "Refactor the login function, then run tests and fix any failures."

</details>

---

<br>

**Q6: When would you use `--continue` vs `--resume`?**

<details>
<summary>💡 Show Answer</summary>

`--continue` resumes the most recent conversation, regardless of what it was. `--resume <id>` resumes a specific conversation by its ID. Use `--continue` when you closed the terminal and want to pick up where you left off. Use `--resume` when you want to return to a specific earlier task (e.g., debugging session from yesterday) while keeping more recent conversations separate.

</details>

---

## Advanced 🔴

**Q7: How would you integrate Claude Code into a pre-commit hook to automatically review changes?**

<details>
<summary>💡 Show Answer</summary>

```bash
# .git/hooks/pre-commit
#!/bin/bash
DIFF=$(git diff --cached)
RESULT=$(claude --print "Review this diff for obvious bugs or style issues. Be brief: $DIFF")
echo "$RESULT"
read -p "Proceed with commit? [y/n] " choice
[ "$choice" = "y" ]
```
The key is using `--print` for non-interactive output, capturing stdout, and setting the pre-commit hook to exit non-zero to block the commit if needed. Pre-approve `Read` and `Bash(git diff *)` in settings.json to avoid prompts.

</details>

---

<br>

**Q8: What is the interaction model difference between asking a question vs requesting an action in Claude Code?**

<details>
<summary>💡 Show Answer</summary>

Questions (e.g., "What does X do?") trigger only read tools — no permission prompts, immediate response. Actions (e.g., "Add X to Y") trigger the full plan → act → observe loop: Claude reads relevant files for context, proposes changes as a diff, waits for approval, executes approved changes, then reads back to verify. The model actively distinguishes between information requests and action requests, though you can always check the planned tool calls before approving.

</details>

---

<br>

**Q9: What does Claude Code do when a bash command fails or a test fails?**

<details>
<summary>💡 Show Answer</summary>

It reads the error output as observation data and incorporates it into the next planning step. If pytest fails with a specific error message, Claude reads that error, identifies which test failed and why, and can either fix the code automatically (if the cause is clear) or report back to you with the diagnosis. This is the "observe" phase of the agentic loop — failures are not dead ends, they're inputs to the next iteration.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Practical examples |

⬅️ **Prev:** [Installation and Setup](../02_Installation_and_Setup/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Slash Commands](../04_Slash_Commands/Theory.md)
