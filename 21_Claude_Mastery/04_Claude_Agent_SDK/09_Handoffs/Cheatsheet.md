# Handoffs — Cheatsheet

## Handoff vs Subagent Call

| | Subagent Call | Handoff |
|---|---|---|
| Control flow | Orchestrator → worker → back | Agent A → Agent B (no return) |
| Context | Parent stays active | Parent done; B continues |
| Pattern | Delegation | Sequential relay |
| Use when | Independent parallel sub-tasks | Sequential pipeline stages |

---

## Handoff Message Template

```python
handoff_message = {
    "handoff_to": "review_agent",          # next agent role/name
    "context_summary": "...",              # human-readable summary
    "state": {                             # structured data to pass
        "items_processed": [...],
        "issues_found": [...],
        "decisions_made": [...]
    },
    "completed_steps": ["step1", "step2"], # what's already done
    "remaining_steps": ["step3", "step4"], # what still needs doing
    "metadata": {
        "session_id": "...",
        "timestamp": "...",
        "trace_id": "..."
    },
    "flags": []                            # alerts, errors, special conditions
}
```

---

## Routing Patterns

```python
def route_handoff(handoff: dict) -> Agent:
    role = handoff["handoff_to"]
    if role == "review_agent":
        return Agent(model=..., system="You are a reviewer...", tools=[...])
    elif role == "action_agent":
        return Agent(model=..., system="You are an action executor...", tools=[...])
    elif role == "human_escalation":
        notify_human(handoff)
        return None  # pause for human input
    else:
        raise ValueError(f"Unknown role: {role}")
```

---

## Pipeline Pattern

```python
async def run_pipeline(data: dict) -> dict:
    # Stage 1
    extract_agent = Agent(system="Extract key entities.")
    result1 = await extract_agent.arun(f"Extract from: {data}")
    
    # Stage 2 — uses stage 1 output
    validate_agent = Agent(system="Validate extracted entities.")
    result2 = await validate_agent.arun(
        f"Validate these entities: {result1}\nOriginal data: {data}"
    )
    
    # Stage 3 — uses stage 2 output
    action_agent = Agent(system="Take action on validated entities.")
    result3 = await action_agent.arun(
        f"Act on: {result2}"
    )
    
    return result3
```

---

## Human-in-the-Loop Handoff

```python
@tool
def escalate_to_human(issue: str, context: dict, urgency: str) -> str:
    """Pause execution and escalate to a human agent.
    urgency: 'low' (next business day), 'medium' (4 hours), 'high' (immediate).
    Returns human's decision and any additional instructions."""
    ticket = create_escalation_ticket(issue, context, urgency)
    response = wait_for_human_response(ticket.id, timeout=urgency_timeout(urgency))
    return f"Human decision: {response.decision}. Notes: {response.notes}"
```

---

## Preventing State Loss

| Risk | Mitigation |
|---|---|
| Next agent re-does completed work | Include `completed_steps` in handoff |
| Critical context dropped | Always include `context_summary` |
| Circular handoffs | Track `hop_count`; stop at max |
| State too large to inline | Store externally, pass reference ID |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Handoff pipeline in code |

⬅️ **Prev:** [Subagents](../08_Subagents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Safety in Agents](../10_Safety_in_Agents/Theory.md)
