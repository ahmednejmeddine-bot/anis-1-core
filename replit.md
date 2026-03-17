# ANIS-1 – Autonomous Neural Intelligence System

## Overview
ANIS-1 is the real AI operations, strategy, and automation platform for Abdeljelil Group.
It consists of a Python FastAPI backend with five GPT-4o-powered agents, a shared LLM service,
an AICouncil orchestrator, and a React + TypeScript Commander Dashboard.

## Project Structure

```
anis-1-core/
├── agents/
│   ├── finance_agent.py        # Budget analysis, forecasting, risk scoring + GPT-4o ask()
│   ├── operations_agent.py     # Process monitoring, KPIs, incident response + GPT-4o ask()
│   ├── strategy_agent.py       # Market analysis, competitive intelligence + GPT-4o ask()
│   ├── document_agent.py       # Document processing, summarisation + GPT-4o ask()
│   └── watchtower_agent.py     # System health, anomaly detection + GPT-4o ask()
├── services/
│   └── llm_service.py          # Shared OpenAI client – chat(), get_client(), LLMError
├── council/
│   └── ai_council.py           # Central orchestrator – routes tasks to agents
├── api/
│   └── server.py               # FastAPI server (port 8000, localhost)
├── dashboard/
│   └── commander_dashboard.tsx # React Commander Dashboard
├── prompts/
│   └── agent_prompts.md        # System prompts for each agent
├── src/
│   └── main.tsx                # React entry point
├── index.html                  # HTML shell for Vite
├── vite.config.ts              # Vite – port 5000, proxies /api /health /agents /dispatch_task
├── tsconfig.json               # TypeScript config
└── package.json                # Node dependencies
```

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 19 + TypeScript + Vite        |
| Backend    | Python 3.11 + FastAPI + Uvicorn     |
| AI         | OpenAI GPT-4o via `openai` SDK      |
| Agents     | Python classes with `ask()` method  |
| Styling    | Inline styles (no CSS framework)    |

## Secrets Required

| Secret          | Purpose                        |
|-----------------|--------------------------------|
| `OPENAI_API_KEY`| Powers all 5 agents via GPT-4o |

## Running the Application

### Frontend (Vite dev server)
- Workflow: **Start application** → `npm run dev`
- Port: **5000** (bound to 0.0.0.0, accessible via preview pane)
- Proxies `/api`, `/health`, `/agents`, `/dispatch_task` to backend port 8000

### Backend (FastAPI)
- Workflow: **Start Backend** → `python3 -m uvicorn api.server:app --host localhost --port 8000 --reload`
- Port: **8000** (bound to localhost only)
- Interactive API docs: `GET /docs` (Swagger UI)

## Key API Endpoints

| Method | Path              | Description                                        |
|--------|-------------------|----------------------------------------------------|
| GET    | `/health`         | Health check — includes `openai_configured` flag  |
| GET    | `/agents`         | List all agents with status and capabilities       |
| POST   | `/dispatch_task`  | **AI Dispatch** – GPT-4o response from any agent  |
| GET    | `/api/council/status`  | Full council + all agent status             |
| GET    | `/api/council/activity`| Activity log                                |
| POST   | `/api/council/dispatch`| Deterministic task dispatch (no LLM)        |

### POST /dispatch_task

```json
{
  "task": "What are the top financial risks this quarter?",
  "agent": "finance",      // optional – auto-routes by keyword if omitted
  "context": "..."         // optional – extra background for the agent
}
```

Returns a full GPT-4o response from the chosen agent.

## LLM Service (`services/llm_service.py`)

Single place to control all OpenAI calls:
- Model: `gpt-4o`
- Temperature: `0.4`
- Max tokens: `1024`
- `LLMError` raised on missing key or API failure
- All 5 agents import `from services.llm_service import chat, LLMError`

## Agent `ask()` Method

Every agent exposes:
```python
agent.ask(task_description: str, context: str = "") -> dict
# Returns: { agent, task, response, model, timestamp }
# On error: { agent, error, timestamp }
```

## Dashboard Features

- **Agents tab** – Live status cards, capability tags, last-run timestamp
- **Activity tab** – Real-time task dispatch history (auto-refreshes every 8s)
- **Alerts tab** – WatchtowerAgent alert feed with severity colour-coding
- **AI Dispatch tab** – Free-text task input, agent selector, context field, GPT-4o response display

## Dependencies

### Python
- `fastapi`, `uvicorn[standard]` – Web framework & server
- `openai` – GPT-4o SDK
- `pydantic`, `python-multipart` – Validation

### Node.js
- `react`, `react-dom`, `vite`, `@vitejs/plugin-react`, `typescript`, `axios`
