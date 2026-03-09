# Research Agent — Step by Step

Build the full research agent from scratch. Each step is independent and builds on the previous.

---

## Step 1: Setup

Create the project structure and install dependencies.

```bash
mkdir research_agent && cd research_agent
python -m venv venv
source venv/bin/activate

pip install langchain langchain-openai langchain-community \
            tavily-python requests beautifulsoup4 pydantic python-dotenv
```

Create `.env`:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

Create `main.py` to verify setup:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Verify keys are loaded
assert os.environ.get("OPENAI_API_KEY"), "Missing OPENAI_API_KEY"
assert os.environ.get("TAVILY_API_KEY"), "Missing TAVILY_API_KEY"

print("Setup complete. Keys loaded successfully.")
```

Run: `python main.py` — should print "Setup complete."

---

## Step 2: Build the Tools

Create `tools/search.py`:

```python
import os
from langchain.tools import Tool
from tavily import TavilyClient

def search_web(query: str) -> str:
    """
    Search the web for information on the given query.
    Returns titles, URLs, and content snippets from top results.
    """
    try:
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        results = client.search(
            query=query,
            max_results=5,
            search_depth="basic"
        )

        if not results.get("results"):
            return f"No results found for: {query}"

        formatted = f"Search results for '{query}':\n\n"
        for i, r in enumerate(results["results"][:5], 1):
            formatted += f"{i}. **{r['title']}**\n"
            formatted += f"   URL: {r['url']}\n"
            formatted += f"   {r['content'][:300]}...\n\n"

        return formatted

    except Exception as e:
        return f"Search error: {str(e)}"


search_tool = Tool(
    name="search_web",
    func=search_web,
    description=(
        "Search the internet for current information on a topic. "
        "Use this when you need facts, definitions, comparisons, or recent news. "
        "Input: a search query string. "
        "Returns: titles, URLs, and content snippets from the top 5 results. "
        "Look for useful URLs in the results to read in full with read_url."
    )
)
```

Create `tools/reader.py`:

```python
import requests
from bs4 import BeautifulSoup
from langchain.tools import Tool

def read_url(url: str) -> str:
    """
    Fetch and extract the main text content from a URL.
    """
    try:
        url = url.strip()
        if not url.startswith("http"):
            return "Error: URL must start with http:// or https://"

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML and extract text
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, navigation
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # Get main text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Limit to first 3000 characters to avoid context overflow
        if len(clean_text) > 3000:
            clean_text = clean_text[:3000] + "\n\n[Content truncated — this is the first 3000 characters]"

        return f"Content from {url}:\n\n{clean_text}"

    except requests.Timeout:
        return f"Error: Request to {url} timed out after 10 seconds"
    except requests.HTTPError as e:
        return f"Error: HTTP {e.response.status_code} when fetching {url}"
    except Exception as e:
        return f"Error reading {url}: {str(e)}"


read_url_tool = Tool(
    name="read_url",
    func=read_url,
    description=(
        "Read the full text content of a webpage. "
        "Use this when you want to read an article or page in detail beyond the search snippet. "
        "Input: a full URL starting with https://. "
        "Returns: the extracted text content of the page (up to 3000 characters)."
    )
)
```

Test the tools:

```python
# test_tools.py
from tools.search import search_web
from tools.reader import read_url

# Test search
result = search_web("Python asyncio explained")
print("SEARCH RESULT:")
print(result[:500])
print()

# Test reader (use a real URL from search results)
# result = read_url("https://docs.python.org/3/library/asyncio.html")
# print("READ RESULT:")
# print(result[:500])
```

---

## Step 3: Build the Agent Loop

Create `agent.py`:

```python
import os
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from tools.search import search_tool
from tools.reader import read_url_tool

def create_research_agent():
    """Create and return the research agent."""

    # LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=2000
    )

    # Tools
    tools = [search_tool, read_url_tool]

    # Memory — keep last 10 turns to prevent context overflow
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=10
    )

    # System prompt
    system_message = """You are a thorough research assistant.

Your job: answer research questions accurately using web search.

Research process:
1. Search for the topic to find relevant sources
2. Read the most relevant source in full using read_url
3. If needed, do a follow-up search for more specific aspects
4. Synthesize everything into a clear, well-structured answer

Always cite your sources. Format your final answer as:

## [Topic Title]

### Summary
[2-3 sentence overview]

### Key Points
1. [point]
2. [point]
3. [point]

### Details
[Expanded explanation]

### Sources
[1] [Title] — [URL]
[2] [Title] — [URL]

Important rules:
- Never make up facts — only state what you found in sources
- Always run at least one search before answering
- If search results are unclear, search again with different terms"""

    # Create agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": system_message}
    )

    return agent
```

---

## Step 4: Add Memory

The agent already has `ConversationBufferWindowMemory` (from Step 3) which provides in-context memory across turns in the same session.

Let's verify it works for follow-up questions:

```python
# test_memory.py
from agent import create_research_agent

agent = create_research_agent()

# First question
print("=== QUESTION 1 ===")
result1 = agent.invoke({
    "input": "What is the Python GIL and why does it exist?"
})
print(result1["output"])

# Follow-up — should use research from previous question
print("\n=== FOLLOW-UP QUESTION ===")
result2 = agent.invoke({
    "input": "Based on what you just explained, what are the alternatives to working around the GIL?"
})
print(result2["output"])
```

The second question should reference what was found in the first question without re-searching from scratch.

---

## Step 5: Output Formatting

Add a structured output formatter using Pydantic.

Create `output.py`:

```python
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

class ResearchAnswer(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    detailed_explanation: str
    sources: list[str]
    confidence: str  # "high" | "medium" | "low"

def format_research_output(raw_agent_output: str, original_question: str) -> str:
    """
    Take the agent's raw output and format it cleanly.
    Falls back to the raw output if formatting fails.
    """
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        prompt = f"""Convert this research answer into a clean, formatted response.

Original question: {original_question}

Research answer: {raw_agent_output}

Format the response as a well-structured markdown document with:
- A clear title
- A brief summary (2-3 sentences)
- 3-5 key bullet points
- A more detailed explanation section
- A properly formatted sources list

Keep all the information — just organize it clearly."""

        response = llm.invoke([
            SystemMessage(content="You are a formatting assistant. Organize information clearly."),
            HumanMessage(content=prompt)
        ])

        return response.content

    except Exception:
        # If formatting fails, return the raw output
        return raw_agent_output


def display_answer(question: str, answer: str):
    """Print a nicely formatted research answer."""
    print("\n" + "="*60)
    print("RESEARCH ANSWER")
    print("="*60)
    print(f"Question: {question}")
    print("-"*60)
    print(answer)
    print("="*60 + "\n")
```

---

## Putting It All Together

Create the main `main.py`:

```python
import os
from dotenv import load_dotenv
from agent import create_research_agent
from output import display_answer

load_dotenv()

def main():
    print("Research Agent Ready")
    print("Type your research question, or 'quit' to exit\n")

    agent = create_research_agent()

    while True:
        question = input("Your question: ").strip()

        if not question:
            continue

        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        print("\nResearching...\n")
        try:
            result = agent.invoke({"input": question})
            display_answer(question, result["output"])

        except Exception as e:
            print(f"Error: {e}")
            print("Try rephrasing your question or asking something different.\n")


if __name__ == "__main__":
    main()
```

Run it:

```bash
python main.py
```

---

## Testing Your Agent

Try these test questions to verify each capability:

```python
# Test 1: Basic research
"What is the difference between supervised and unsupervised learning?"

# Test 2: Current information (needs search)
"What new AI models were released in early 2024?"

# Test 3: Technical comparison
"What are the tradeoffs between PostgreSQL and MongoDB for a web application?"

# Test 4: Multi-step research
"Explain vector databases and when you would use Pinecone vs Chroma"

# Test 5: Follow-up question (tests memory)
# First: "Explain transformer attention mechanisms"
# Then:  "What's the computational complexity of what you just described?"
```

---

## Expected Output Example

```
============================================================
RESEARCH ANSWER
============================================================
Question: What is the difference between RAG and fine-tuning for LLMs?

# RAG vs Fine-Tuning: When to Use Each Approach

### Summary
RAG (Retrieval-Augmented Generation) adds external knowledge at inference time,
while fine-tuning modifies the model's weights through additional training.
They solve different problems and are often complementary.

### Key Points
1. RAG retrieves relevant documents at query time — no model changes required
2. Fine-tuning updates model weights — requires training data and GPU compute
3. RAG is better for frequently updated information; fine-tuning for style/behavior
4. RAG has higher per-query costs; fine-tuning has higher upfront costs
5. Many production systems use both together

### Details
[Expanded explanation with technical details...]

### Sources
[1] "RAG vs Fine-Tuning" — https://example.com/...
[2] "When to Fine-Tune vs RAG" — https://example.com/...
============================================================
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture diagram |
| [📄 Project_Guide.md](./Project_Guide.md) | Project overview |
| 📄 **Step_by_Step.md** | ← you are here |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Common issues and fixes |

⬅️ **Prev:** [08 Agent Frameworks](../08_Agent_Frameworks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 MCP Fundamentals](../../11_MCP_Model_Context_Protocol/01_MCP_Fundamentals/Theory.md)
