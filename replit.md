# ANIS-1 – Autonomous Neural Intelligence System

## Overview
ANIS-1 is the AI operations, strategy, and automation platform for Abdeljelil Group.
It consists of a Python FastAPI backend exposing a multi-agent AI system, and a React + TypeScript
Commander Dashboard frontend for real-time monitoring and task dispatch.

## Project Structure

```
anis-1-core/
├── agents/
│   ├── finance_agent.py        # Budget analysis, forecasting, risk scoring
│   ├── operations_agent.py     # Process monitoring, KPIs, incident response
│   ├── strategy_agent.py       # Market analysis, competitive intelligence, planning
│   ├── document_agent.py       # Document processing, summarisation, extraction
│   └── watchtower_agent.py     # System health, anomaly detection, alerting
├── council/
│   └── ai_council.py           # Central orchestrator – routes tasks to agents
├── api/
│   └── server.py               # FastAPI server (port 8000, localhost)
├── dashboard/
│   └── commander_dashboard.tsx # React dashboard component
├── prompts/
│   └── agent_prompts.md        # System prompts for each agent
├── src/
│   └── main.tsx                # React entry point
├── index.html                  # HTML shell for Vite
├── vite.config.ts              # Vite config – port 5000, proxies /api → 8000
├── tsconfig.json               # TypeScript config
└── package.json                # Node dependencies (React, Vite, Axios)
```

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 19 + TypeScript + Vite        |
| Backend   | Python 3.11 + FastAPI + Uvicorn     |
| Agents    | Pure Python classes                 |
| Styling   | Inline styles (no CSS framework)    |

## Running the Application

### Frontend (Vite dev server)
- Workflow: **Start application** → `npm run dev`
- Port: **5000** (bound to 0.0.0.0, accessible via preview pane)
- Proxies `/api/*` requests to the backend on port 8000

### Backend (FastAPI)
- Workflow: **Start Backend** → `python3 -m uvicorn api.server:app --host localhost --port 8000 --reload`
- Port: **8000** (bound to localhost only)
- API docs available at `/docs` (Swagger UI)

## Key API Endpoints

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | `/api/health`               | Health check                 |
| GET    | `/api/council/status`       | Full council + agent status  |
| GET    | `/api/council/agents`       | List all agents              |
| GET    | `/api/council/activity`     | Activity log                 |
| POST   | `/api/council/dispatch`     | Dispatch a task to the council |
| POST   | `/api/agents/finance/budget`| Budget analysis              |
| POST   | `/api/agents/strategy/market`| Market analysis             |
| POST   | `/api/agents/watchtower/alert`| Send an alert              |

## Dashboard Features

- **Agents tab** – Live status cards for all 5 agents with capabilities listed
- **Activity tab** – Real-time task dispatch history
- **Alerts tab** – Watchtower alert feed with severity colour-coding
- **Dispatch tab** – Manual task dispatch to the AI Council
- Auto-refreshes every 8 seconds

## Dependencies

### Python
- `fastapi` – Web framework
- `uvicorn[standard]` – ASGI server
- `pydantic` – Data validation
- `python-multipart` – Form data support

### Node.js
- `react` / `react-dom` – UI framework
- `vite` + `@vitejs/plugin-react` – Build tooling
- `typescript` – Type safety
- `axios` – HTTP client
