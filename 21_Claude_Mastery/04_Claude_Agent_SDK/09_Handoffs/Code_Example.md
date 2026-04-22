# Handoffs — Code Example

## Linear Pipeline Handoff

```python
"""
Two-stage pipeline: Agent A analyzes → hands off → Agent B acts.
"""
import json
from claude_agent_sdk import Agent, tool
from datetime import datetime


# ── STAGE 1 TOOLS (Analysis) ──────────────────────────────────

@tool
def classify_support_ticket(text: str) -> dict:
    """Classify a support ticket by type and urgency.
    Returns: {type: billing|technical|account|other, urgency: low|medium|high, 
    entities: [key elements extracted]}"""
    # Simplified classification (in production: ML model or Claude)
    text_lower = text.lower()
    ticket_type = "other"
    if any(w in text_lower for w in ["charge", "refund", "billing", "payment", "invoice"]):
        ticket_type = "billing"
    elif any(w in text_lower for w in ["error", "bug", "crash", "broken", "not working"]):
        ticket_type = "technical"
    elif any(w in text_lower for w in ["password", "login", "account", "access"]):
        ticket_type = "account"
    
    urgency = "high" if any(w in text_lower for w in ["urgent", "asap", "critical", "immediately"]) else "medium"
    
    return {
        "type": ticket_type,
        "urgency": urgency,
        "word_count": len(text.split()),
        "timestamp": datetime.utcnow().isoformat()
    }

@tool
def extract_ticket_entities(text: str) -> dict:
    """Extract key entities from a support ticket.
    Returns: {customer_name, product_mentioned, amount_mentioned, dates_mentioned}"""
    # Simplified extraction
    import re
    amounts = re.findall(r'\$[\d,]+\.?\d*', text)
    dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
    
    return {
        "amounts_mentioned": amounts,
        "dates_mentioned": dates,
        "raw_length": len(text)
    }


# ── STAGE 2 TOOLS (Action) ────────────────────────────────────

@tool
def lookup_account(search_term: str) -> dict:
    """Look up a customer account by name, email, or ticket reference.
    Returns account details or error if not found."""
    # Simulated database
    ACCOUNTS = {
        "alice@example.com": {
            "id": "acct_001", "name": "Alice Chen", 
            "plan": "Pro", "status": "active", "balance": 0
        }
    }
    for key, account in ACCOUNTS.items():
        if search_term.lower() in key.lower() or search_term.lower() in account["name"].lower():
            return account
    return {"error": f"Account not found: {search_term}"}

@tool
def create_action_note(
    account_id: str,
    action_taken: str,
    resolution: str,
    follow_up_required: bool = False
) -> str:
    """Create an action note on an account.
    Returns confirmation with note ID."""
    note_id = f"note_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    print(f"[ACTION NOTE] {note_id} → Account {account_id}: {action_taken}")
    return f"Note created: {note_id}"

@tool
def escalate_ticket(
    ticket_summary: str,
    reason: str,
    urgency: str,
    assigned_to: str = "senior_support"
) -> str:
    """Escalate a ticket to a higher support tier.
    Returns escalation reference ID."""
    esc_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    print(f"[ESCALATION] {esc_id} → {assigned_to} | {urgency} | {reason}")
    return f"Escalated: {esc_id}"


# ── STAGE 1: ANALYSIS AGENT ──────────────────────────────────

def run_analysis_stage(ticket_text: str) -> dict:
    """Stage 1: Analyze and classify the ticket. Returns handoff message."""
    
    analysis_agent = Agent(
        model="claude-haiku-4-5",
        tools=[classify_support_ticket, extract_ticket_entities],
        system="""You are a ticket analysis agent. Your job:
        1. Classify the ticket (type and urgency)
        2. Extract key entities (amounts, dates, references)
        3. Create a structured handoff for the action agent
        
        Return a JSON handoff message with these exact fields:
        {
            "handoff_to": "action_agent",
            "context_summary": "one-sentence summary of the ticket",
            "classification": {...},  // from classify_support_ticket
            "entities": {...},        // from extract_ticket_entities
            "recommended_action": "what should be done",
            "completed_steps": ["classified ticket", "extracted entities"],
            "remaining_steps": ["look up account", "take action", "log resolution"]
        }""",
        max_steps=5
    )
    
    result = analysis_agent.run(
        f"Analyze this support ticket:\n\n{ticket_text}"
    )
    
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        # Fallback if agent didn't return clean JSON
        return {
            "handoff_to": "action_agent",
            "context_summary": "Ticket analyzed",
            "raw_analysis": result,
            "completed_steps": ["analyzed ticket"],
            "remaining_steps": ["determine action"]
        }


# ── STAGE 2: ACTION AGENT ─────────────────────────────────────

def run_action_stage(handoff: dict, ticket_text: str) -> str:
    """Stage 2: Receives handoff and takes appropriate action."""
    
    action_agent = Agent(
        model="claude-sonnet-4-6",
        tools=[lookup_account, create_action_note, escalate_ticket],
        system="""You are a support action agent. You receive pre-analyzed tickets.
        Your job: take the appropriate action based on the analysis.
        
        Follow these rules:
        - High urgency + billing → look up account and escalate
        - Technical issue → create action note with next steps
        - Account issue → look up account and create action note
        - Always log your action with create_action_note""",
        max_steps=6
    )
    
    # Pass the handoff context + original ticket
    prompt = f"""Continue from the analysis stage.

Analysis context:
{json.dumps(handoff, indent=2)}

Original ticket:
{ticket_text}

Completed steps: {handoff.get('completed_steps', [])}
Remaining steps: {handoff.get('remaining_steps', [])}

Take the appropriate action(s) based on the analysis."""
    
    return action_agent.run(prompt)


# ── PIPELINE RUNNER ───────────────────────────────────────────

def process_ticket(ticket_text: str) -> str:
    """Run the full 2-stage pipeline for a support ticket."""
    print(f"\n{'='*60}")
    print(f"PROCESSING TICKET: {ticket_text[:80]}...")
    print(f"{'='*60}")
    
    # Stage 1: Analysis
    print("\n[Stage 1: Analysis]")
    handoff = run_analysis_stage(ticket_text)
    print(f"Handoff created: {handoff.get('context_summary', 'unknown')}")
    print(f"Classification: {handoff.get('classification', {}).get('type', 'unknown')}")
    
    # Stage 2: Action
    print("\n[Stage 2: Action]")
    result = run_action_stage(handoff, ticket_text)
    
    return result


if __name__ == "__main__":
    tickets = [
        "Hi, I was charged $49.99 twice this month for my subscription. "
        "This is urgent and I need a refund immediately. My email is alice@example.com.",
        
        "The dashboard keeps crashing when I try to export reports. "
        "This is a critical bug affecting my team's workflow.",
    ]
    
    for ticket in tickets:
        result = process_ticket(ticket)
        print(f"\nFinal resolution: {result}")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Subagents](../08_Subagents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Safety in Agents](../10_Safety_in_Agents/Theory.md)
