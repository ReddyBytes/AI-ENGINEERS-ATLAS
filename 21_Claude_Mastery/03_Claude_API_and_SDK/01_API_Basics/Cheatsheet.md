# API Basics — Cheatsheet

## Core Identity

| Item | Value |
|---|---|
| Base URL | `https://api.anthropic.com` |
| Messages endpoint | `POST /v1/messages` |
| API version header | `anthropic-version: 2023-06-01` |
| Auth header | `x-api-key: YOUR_KEY` |
| Content-type | `application/json` |

---

## Required Headers (Every Request)

```
x-api-key: sk-ant-api03-...
anthropic-version: 2023-06-01
content-type: application/json
```

---

## Environment Variable Setup

```bash
# Bash / Zsh
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# .env file (with python-dotenv)
ANTHROPIC_API_KEY=sk-ant-api03-...
```

```python
import os
from dotenv import load_dotenv
load_dotenv()

import anthropic
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY automatically
# OR
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

---

## Minimal Curl Request

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Rate Limit Response

```
HTTP 429 Too Many Requests

retry-after: 30
x-ratelimit-remaining-requests: 0
x-ratelimit-reset-requests: 2024-01-01T00:01:00Z
```

Handle with exponential backoff + jitter.

---

## Key Concepts

| Concept | Explanation |
|---|---|
| REST API | Stateless HTTP interface — each request is independent |
| JSON body | All data serialized as JSON (in and out) |
| Stateless | Server holds no memory — you send full history each time |
| API versioning | Date-based, declared in header — not in URL |
| Rate limits | RPM + TPM + TPD — enforced per tier and model |

---

## Security Rules

- Never commit API keys to git
- Store in environment variables or secrets managers (AWS Secrets Manager, Vault)
- Add `.env` to `.gitignore`
- Rotate keys periodically in the Anthropic Console
- Use separate keys per environment (dev / staging / prod)

---

## HTTP Status Codes

| Code | Meaning | Action |
|---|---|---|
| 200 | Success | Parse response JSON |
| 400 | Bad request | Fix request body/headers |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check permissions/tier |
| 429 | Rate limited | Exponential backoff |
| 500 | Server error | Retry with backoff |
| 529 | Overloaded | Retry with backoff |

---

## Golden Rules

1. Always use environment variables for API keys
2. Always set `max_tokens` explicitly — never rely on defaults
3. Always check HTTP status before parsing response
4. Always implement retry logic for 429 and 5xx errors
5. Always pin `anthropic-version: 2023-06-01`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Track 3 Overview](../README.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Messages API](../02_Messages_API/Cheatsheet.md)
