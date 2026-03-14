# Multimodal Agents — Architecture Deep Dive

## Computer Use Agent: Full Architecture

```mermaid
flowchart TB
    subgraph UserLayer ["User / Orchestrator"]
        TASK["Task: 'Book cheapest flight\nNYC to London next Tuesday'"]
    end

    subgraph AgentCore ["Agent Core"]
        PLANNER[Task Planner\nDecompose into subtasks]
        EXEC[Agent Executor\nobserve-reason-act loop]
        MEMORY[Working Memory\nsteps taken, current state\ncontext compression]
    end

    subgraph PerceptionLayer ["Perception"]
        SS[Screenshot\ncapture module]
        RESIZE[Resize to\n1280×720]
        SOM[Set-of-Marks\noverlay numbered labels\non detected elements]
    end

    subgraph ReasoningLayer ["Reasoning — VLM"]
        VLM_INPUT["Input to VLM:\n• Resized screenshot + SoM markers\n• Task description\n• Step history (compressed)\n• Available actions"]
        VLM[Vision-Language Model\nClaude / GPT-4V]
        VLM_OUTPUT["Output:\n• What I see\n• Next action\n• Action parameters\n• Confidence"]
    end

    subgraph ActionLayer ["Action Execution"]
        PARSER[Action Parser\nvalidate + parse JSON action]
        GUARD{Safety\ncheck}
        CONFIRM[Human confirmation\nrequired for:\n• form submit\n• file delete\n• email send]
        EXECUTOR[Action Executor\npyautogui / Playwright\n/ OS API]
    end

    subgraph VerifyLayer ["Verification"]
        SS2[Take new screenshot]
        VERIFY[Verify expected\nresult occurred]
        CHECKPOINT{Subtask\ncomplete?}
    end

    TASK --> PLANNER --> EXEC
    EXEC --> SS --> RESIZE --> SOM --> VLM_INPUT --> VLM --> VLM_OUTPUT
    VLM_OUTPUT --> EXEC
    EXEC --> PARSER --> GUARD
    GUARD -->|Safe action| EXECUTOR
    GUARD -->|Needs confirmation| CONFIRM --> EXECUTOR
    EXECUTOR --> SS2 --> VERIFY --> CHECKPOINT
    CHECKPOINT -->|No| EXEC
    CHECKPOINT -->|Yes| NEXT_SUBTASK[Next subtask\nor done]
    EXEC <--> MEMORY
```

---

## Voice Agent: Full Pipeline Architecture

```mermaid
flowchart TB
    subgraph Input ["Input Processing"]
        MIC[Microphone / Audio stream]
        VAD[Voice Activity Detection\nsilero-vad\ndetects end of speech]
        CHUNK[Audio chunk\nready to process]
        MIC --> VAD --> CHUNK
    end

    subgraph STT_Layer ["Speech-to-Text"]
        PREPROCESS[Audio preprocessing\n16kHz mono WAV]
        WHISPER["STT Model\nWhisper via API\nor Deepgram streaming"]
        TRANSCRIPT[Transcribed text]
        CHUNK --> PREPROCESS --> WHISPER --> TRANSCRIPT
    end

    subgraph LLM_Layer ["LLM with Tools"]
        INTENT[Intent classification\nrouting to right handler]
        TOOL_LLM[Tool-calling LLM\nClaude / GPT-4o]
        TOOLS["Available tools:\n• get_account_info()\n• search_knowledge_base()\n• book_appointment()\n• escalate_to_human()"]
        RESPONSE_TEXT[Response text]
        TRANSCRIPT --> INTENT --> TOOL_LLM
        TOOL_LLM <-->|tool calls + results| TOOLS
        TOOL_LLM --> RESPONSE_TEXT
    end

    subgraph TTS_Layer ["Text-to-Speech"]
        TTS_MODEL["TTS Model\nOpenAI TTS-1 (fast)\nor ElevenLabs Flash"]
        AUDIO_OUT[Synthesized audio stream]
        RESPONSE_TEXT --> TTS_MODEL --> AUDIO_OUT
    end

    subgraph Output ["Output"]
        SPEAKER[Speaker / Phone line]
        AUDIO_OUT --> SPEAKER
    end

    subgraph Memory ["Session State"]
        HISTORY[Conversation history]
        USER_CTX[User context\naccount info, preferences]
        TOOL_LLM <--> HISTORY
        TOOL_LLM <--> USER_CTX
    end
```

---

## Set-of-Marks (SoM) Grounding Pipeline

```mermaid
flowchart LR
    subgraph RawScreen ["Raw Screenshot"]
        RAW[Screenshot\n1280×720]
    end

    subgraph ElementDetection ["UI Element Detection"]
        OD[Object detector\nor OCR + layout parser]
        ELEMENTS["Detected elements:\n• Button: 'Submit' @ (450, 820)\n• Input: 'Email' @ (340, 280)\n• Link: 'Cancel' @ (200, 820)"]
        RAW --> OD --> ELEMENTS
    end

    subgraph Overlay ["SoM Overlay"]
        MARK[Draw numbered markers\non each element]
        MARKED_IMG["Annotated screenshot:\n• ①Submit button\n• ②Email input\n• ③Cancel link"]
        ELEMENTS --> MARK --> MARKED_IMG
    end

    subgraph VLM_SOM ["VLM Reasoning"]
        VLM_IN["Input:\nAnnotated screenshot +\n'I need to submit the form.\nWhich element number?'"]
        VLM_CHOICE["Output:\n'Element ①'\n(the Submit button)"]
        MARKED_IMG --> VLM_IN --> VLM_CHOICE
    end

    subgraph Execution ["Action Execution"]
        MAP[Map choice ① → coordinates\n(450, 820)]
        CLICK[Execute click\nat (450, 820)]
        VLM_CHOICE --> MAP --> CLICK
    end
```

---

## Multi-Agent Multimodal System

Some tasks benefit from multiple specialized agents working together:

```mermaid
flowchart TB
    subgraph Orchestrator ["Orchestrator Agent"]
        ORCH[Main LLM\ndecomposes task\nassigns to workers]
    end

    subgraph Workers ["Specialized Worker Agents"]
        WEB_AGENT[Web Navigation Agent\n• screenshot perception\n• browser actions]
        VISION_AGENT[Document Vision Agent\n• reads PDFs, images\n• extracts structured data]
        VOICE_AGENT[Voice Agent\n• STT → LLM → TTS\n• phone/audio interface]
        CODE_AGENT[Code Agent\n• executes code\n• processes data]
    end

    subgraph Tools ["Shared Tools"]
        DB[Database]
        API_S[External APIs]
        FILE[File system\n(sandboxed)]
    end

    USER[User task] --> ORCH
    ORCH -->|subtask 1| WEB_AGENT
    ORCH -->|subtask 2| VISION_AGENT
    ORCH -->|subtask 3| VOICE_AGENT
    ORCH -->|subtask 4| CODE_AGENT
    WEB_AGENT & VISION_AGENT & CODE_AGENT <--> DB & API_S & FILE
    WEB_AGENT & VISION_AGENT & VOICE_AGENT & CODE_AGENT -->|results| ORCH
    ORCH --> FINAL[Final answer / action]
```

---

## Context Window Management in Long Computer Use Tasks

A major challenge: each screenshot adds ~1,400 tokens. By step 20, you've used 28,000 tokens just for screenshots.

```mermaid
flowchart LR
    subgraph ContextStrategy ["Context Management Strategy"]
        FULL[Steps 1-5\nFull screenshot + reasoning]
        SUMMARY[Steps 6-15\nSummarize: 'Completed login,\nnavigated to checkout,\ncurrent state: cart page']
        CURRENT[Steps 16+\nOnly most recent screenshot\n+ compressed history]

        FULL --> SUMMARY --> CURRENT
    end
```

**Implementation**: After every N steps (e.g., 5), prompt the LLM to produce a compressed summary of what has happened so far and what the current state is. Replace the detailed history with this summary, keeping only the most recent screenshot at full fidelity.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Code examples |

⬅️ **Prev:** [06 — Multimodal Embeddings](../06_Multimodal_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 18 — AI Evaluation](../../18_AI_Evaluation/01_Evaluation_Fundamentals/Theory.md)
