# Prompt Patterns Catalog

8 reusable patterns you can copy, adapt, and use immediately. Each pattern has a template and a real example.

---

## Pattern 1: Role + Task

Give the model a specific identity before the task. The role frames everything that follows.

**Template:**
```
You are a [specific role with relevant expertise].
[Task description with any constraints.]
```

**Example:**
```
You are a senior Python developer with 10 years of experience in backend systems.
Review this function and identify any performance issues or bugs. Be direct and technical.

def get_users(db):
    users = []
    for id in range(1000):
        users.append(db.query(f"SELECT * FROM users WHERE id={id}"))
    return users
```

**When to use:** Any task where tone, expertise level, or perspective matters. Almost always worth adding.

---

## Pattern 2: Chain-of-Thought

Force the model to reason step by step before reaching a conclusion. Dramatically improves accuracy on complex tasks.

**Template:**
```
[Problem or question]

Think through this step by step:
1. First, identify [component 1]
2. Then, consider [component 2]
3. Finally, [conclusion]
```

**Example:**
```
A customer bought 3 items: $12.99, $8.50, and $24.00. They have a 15% discount coupon
and need to pay 8% sales tax. What is their final total?

Think through this step by step:
1. First, calculate the subtotal
2. Then, apply the discount
3. Then, add tax
4. Finally, give the total
```

**When to use:** Math, multi-step logic, planning, debugging, any question where the answer requires intermediate reasoning.

---

## Pattern 3: Few-Shot

Show the model 2–5 examples of the exact input/output format you want before your real request.

**Template:**
```
[Task description]

Examples:
Input: [example 1 input]
Output: [example 1 output]

Input: [example 2 input]
Output: [example 2 output]

Now do this:
Input: [your actual input]
Output:
```

**Example:**
```
Classify customer support tickets by department.

Examples:
Input: "My order hasn't arrived in 3 weeks"
Output: logistics

Input: "I was charged twice for one purchase"
Output: billing

Input: "The app crashes when I try to upload a photo"
Output: technical

Now do this:
Input: "I want to cancel my subscription"
Output:
```

**When to use:** Classification, transformation, extraction — any task where you have a clear pattern. 3 examples is usually the sweet spot.

---

## Pattern 4: Output Format

Specify the exact structure of the response. Use JSON, tables, lists, or custom templates.

**Template:**
```
[Task]

Return your answer in exactly this format:
[format description or example structure]
Do not include any other text.
```

**Example:**
```
Extract the key information from this job posting.

Return your answer as JSON with exactly these fields:
{
  "title": "job title",
  "company": "company name",
  "location": "city, country or remote",
  "salary_range": "range or null if not mentioned",
  "required_skills": ["skill1", "skill2"],
  "experience_years": number or null
}
Do not include any other text.

Job posting: "Senior ML Engineer at TechCorp in Austin, TX.
5+ years required. Skills: Python, TensorFlow, PyTorch. Salary: $160k-$200k."
```

**When to use:** Whenever you need to parse or display the output in code. Always use for production pipelines.

---

## Pattern 5: Step-by-Step Instructions

Break a complex task into numbered steps so the model handles each part separately.

**Template:**
```
Complete the following task in order:
Step 1: [first action]
Step 2: [second action]
Step 3: [third action]
...
After each step, label your output with the step number.
```

**Example:**
```
Complete the following task in order:
Step 1: Read the customer complaint below and identify the core issue in one sentence.
Step 2: Identify the customer's emotional state (frustrated, confused, angry, disappointed).
Step 3: Write a professional 2-sentence response that acknowledges their feeling and offers a resolution path.

Complaint: "I've been waiting 6 weeks for my refund. I've called three times and nobody
helps me. This is completely unacceptable. I want to speak to a manager."
```

**When to use:** Multi-part tasks, content transformation pipelines, tasks where sequence matters.

---

## Pattern 6: Critique and Revise

Ask the model to evaluate its own output and improve it. This gets higher quality in one API call.

**Template:**
```
[Task]

First draft: write your initial response.
Critique: identify 2-3 weaknesses or areas to improve.
Revised draft: rewrite incorporating your critique.
```

**Example:**
```
Write a product description for wireless earbuds targeted at gym-goers.

First draft: write your initial product description.
Critique: identify 2-3 weaknesses (clarity, missing benefits, weak call to action, etc.)
Revised draft: rewrite incorporating your critique.
```

**When to use:** Writing tasks, code review, any situation where quality matters more than speed. Adds one extra round of self-reflection.

---

## Pattern 7: ReAct-Style (Reason + Act)

The model alternates between reasoning (Thought) and taking an action (Action), then observes the result. Used in agentic systems.

**Template:**
```
You can use the following tools: [list tools and what they do]

For each step, follow this format:
Thought: [what you need to figure out]
Action: [tool name] | [input to tool]
Observation: [result of the action — provided by the system]
... (repeat as needed)
Final Answer: [your conclusion based on all observations]

Question: [the task to complete]
```

**Example:**
```
You can use: search(query) → returns web results, calculator(expression) → returns number

Thought: I need to find today's USD to EUR rate and convert $350.
Action: search | current USD to EUR exchange rate
Observation: 1 USD = 0.92 EUR as of March 2026
Thought: Now I can calculate the conversion.
Action: calculator | 350 * 0.92
Observation: 322
Final Answer: $350 USD is approximately €322 EUR.

Question: How much is $350 in Euros?
```

**When to use:** Agent systems, multi-step tasks that require external tools, any workflow that needs decision-making between steps.

---

## Pattern 8: Meta-Prompt

Use the model to write or improve prompts for another task. Useful when you want to automate prompt creation.

**Template:**
```
You are an expert prompt engineer. Your job is to write optimized prompts for LLMs.

Task description: [what the prompt needs to accomplish]
Target model: [Claude/GPT-4/etc.]
Input format: [what the prompt will receive as input]
Desired output: [what it should produce]

Write an optimized prompt for this task. Include:
- A clear role
- Specific instructions
- Output format specification
- One example if helpful
```

**Example:**
```
You are an expert prompt engineer. Your job is to write optimized prompts for LLMs.

Task description: Extract action items from meeting notes
Target model: Claude
Input format: Freeform meeting notes text
Desired output: Numbered list of action items with owner and deadline

Write an optimized prompt for this task. Include:
- A clear role
- Specific instructions
- Output format specification
- One example if helpful
```

**When to use:** Building prompt libraries, automating prompt generation for new use cases, iterating quickly on prompt quality.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Common_Mistakes.md](./Common_Mistakes.md) | Common prompt engineering mistakes |
| 📄 **Prompt_Patterns.md** | ← you are here |

⬅️ **Prev:** [09 Using LLM APIs](../../07_Large_Language_Models/09_Using_LLM_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Tool Calling](../02_Tool_Calling/Theory.md)
