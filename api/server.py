"""
ANIS-1 API Server – FastAPI backend.

Routes:
  GET  /health          – System health check
  GET  /agents          – List all agents with status
  POST /dispatch_task   – Smart dispatch: single-agent or CrewAI crew

All existing /api/* routes for the Commander Dashboard are preserved.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("anis1.server")

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from council.ai_council import AICouncil
from services.llm_service import LLMError
from services import task_classifier, crew_service

# ---------------------------------------------------------------------------
app = FastAPI(
    title="ANIS-1 API",
    description="Autonomous Neural Intelligence System – Abdeljelil Group",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

council = AICouncil()
logger.info("ANIS-1 AICouncil online  agents=%d", len(council.agents))

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class DispatchTaskRequest(BaseModel):
    task: str
    agent: str | None = None   # optional: finance | operations | strategy | document | watchtower | crew
    context: str = ""          # optional background context

class DispatchRequest(BaseModel):
    task: str
    payload: dict[str, Any] = {}

class BudgetRequest(BaseModel):
    allocations: dict[str, float]
    actuals: dict[str, float]

class ForecastRequest(BaseModel):
    historical: list[float]
    periods: int = 3

class RiskRequest(BaseModel):
    factors: list[str]

class KpiRequest(BaseModel):
    kpis: dict[str, float]
    targets: dict[str, float]

class MarketRequest(BaseModel):
    name: str
    growth_rate_pct: float
    competition_level: str = "medium"
    market_size_usd: float = 0

class DocumentRequest(BaseModel):
    id: str = ""
    content: str
    type: str = "general"

class SummariseRequest(BaseModel):
    text: str
    max_sentences: int = 3

class AlertRequest(BaseModel):
    severity: str = "info"
    message: str
    component: str = "unknown"


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "system": "ANIS-1",
        "version": "2.0.0",
        "group": "Abdeljelil Group",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestration": "CrewAI + GPT-4o",
        "routes": {
            "health":        "GET  /health",
            "agents":        "GET  /agents",
            "dispatch_task": "POST /dispatch_task",
            "docs":          "GET  /docs",
        },
    }


@app.get("/health")
@app.get("/api/health")
def health():
    """System health — includes openai_configured flag for the dashboard."""
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_configured": api_key_set,
        "agents_online": len(council.agents),
        "orchestration": "CrewAI + GPT-4o",
    }


@app.get("/agents")
@app.get("/api/council/agents")
def list_agents():
    """All registered ANIS-1 agents with capabilities and current status."""
    return {"agents": council.agent_list()}


# ---------------------------------------------------------------------------
# /dispatch_task – smart AI dispatch (single-agent or CrewAI crew)
# ---------------------------------------------------------------------------

@app.post("/dispatch_task")
@app.post("/api/dispatch_task")
async def dispatch_task(req: DispatchTaskRequest):
    """
    Dispatch a natural-language task to ANIS-1.

    Routing logic:
      1. If `agent` is explicitly set to a known key → single-agent execution.
      2. If `agent` is "crew"                        → forced CrewAI crew (all 5 agents).
      3. If `agent` is omitted (auto-route):
           • Task Classifier scores keyword domains.
           • Single domain  → single-agent execution.
           • Multi-domain   → CrewAI multi-agent crew execution.

    Args (JSON body):
        task    – required; natural-language task description.
        agent   – optional; "finance" | "operations" | "strategy" |
                  "document" | "watchtower" | "crew" | null (auto).
        context – optional; extra background for the agent(s).
    """
    if not req.task.strip():
        raise HTTPException(status_code=400, detail="'task' must not be empty.")

    # ------------------------------------------------------------------
    # Forced full-crew mode
    # ------------------------------------------------------------------
    if req.agent == "crew":
        logger.info("Forced crew dispatch  task='%s'", req.task[:60])
        return await _run_crew_dispatch(
            task=req.task,
            context=req.context,
            agent_keys=list(council.agents.keys()),
            auto_routed=False,
            classification={"mode": "crew", "agents": list(council.agents.keys()), "reason": "forced_crew"},
        )

    # ------------------------------------------------------------------
    # Forced single-agent mode
    # ------------------------------------------------------------------
    if req.agent:
        if req.agent not in council.agents:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown agent '{req.agent}'. Valid options: {list(council.agents.keys())} or 'crew'.",
            )
        logger.info("Forced single-agent dispatch  agent='%s'  task='%s'", req.agent, req.task[:60])
        return await _run_single_agent_dispatch(
            task=req.task,
            context=req.context,
            agent_key=req.agent,
            auto_routed=False,
            classification={"mode": "single", "agent": req.agent, "reason": "forced"},
        )

    # ------------------------------------------------------------------
    # Auto-route via Task Classifier
    # ------------------------------------------------------------------
    classification = task_classifier.classify(req.task)
    logger.info(
        "Auto-classified  mode=%s  agents=%s  reason=%s",
        classification["mode"], classification["agents"], classification["reason"],
    )

    if classification["mode"] == "crew":
        return await _run_crew_dispatch(
            task=req.task,
            context=req.context,
            agent_keys=classification["agents"],
            auto_routed=True,
            classification=classification,
        )

    return await _run_single_agent_dispatch(
        task=req.task,
        context=req.context,
        agent_key=classification["agent"],
        auto_routed=True,
        classification=classification,
    )


# ---------------------------------------------------------------------------
# Internal dispatch helpers
# ---------------------------------------------------------------------------

async def _run_single_agent_dispatch(
    task: str,
    context: str,
    agent_key: str,
    auto_routed: bool,
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Call a single agent's ask() method and return a unified response."""
    agent = council.agents[agent_key]

    if not hasattr(agent, "ask"):
        raise HTTPException(
            status_code=500,
            detail=f"Agent '{agent_key}' does not support AI dispatch (no ask() method).",
        )

    logger.info("Single-agent execution  agent='%s'", agent_key)
    try:
        result = agent.ask(task_description=task, context=context)
    except Exception as exc:
        logger.error("Agent '%s' raised exception: %s", agent_key, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

    if "error" in result:
        logger.warning("Agent '%s' returned error: %s", agent_key, result["error"])
        raise HTTPException(status_code=502, detail=result["error"])

    _log_activity(task, [agent_key], context)

    return {
        "system": "ANIS-1",
        "execution_mode": "single_agent",
        "agent": agent_key,
        "agent_name": result.get("agent"),
        "agents_used": [agent_key],
        "agent_count": 1,
        "task": task,
        "context_provided": bool(context),
        "auto_routed": auto_routed,
        "model": result.get("model", "gpt-4o"),
        "response": result.get("response"),
        "execution_time_s": None,
        "timestamp": result.get("timestamp"),
        "classification": classification,
    }


async def _run_crew_dispatch(
    task: str,
    context: str,
    agent_keys: list[str],
    auto_routed: bool,
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Run a CrewAI multi-agent crew and return a unified response."""
    logger.info("CrewAI execution  agents=%s", agent_keys)
    try:
        result = crew_service.run_crew(
            task_description=task,
            agent_keys=agent_keys,
            context=context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("CrewAI execution failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"CrewAI execution error: {exc}")

    _log_activity(task, agent_keys, context)

    return {
        "system": "ANIS-1",
        "execution_mode": "crew",
        "agent": "crew",
        "agent_name": "ANIS-1 CrewAI Council",
        "agents_used": result.get("agents_used", agent_keys),
        "agent_count": result.get("agent_count", len(agent_keys)),
        "task": task,
        "context_provided": bool(context),
        "auto_routed": auto_routed,
        "model": result.get("model", "gpt-4o"),
        "response": result.get("response"),
        "execution_time_s": result.get("execution_time_s"),
        "timestamp": result.get("timestamp"),
        "classification": classification,
    }


def _log_activity(task: str, agents: list[str], context: str) -> None:
    council._activity_log.append({
        "task": task[:80],
        "agents_dispatched": agents,
        "timestamp": datetime.utcnow().isoformat(),
        "payload_keys": ["task", "context"] if context else ["task"],
    })


# ---------------------------------------------------------------------------
# Council endpoints (used by the Commander Dashboard)
# ---------------------------------------------------------------------------

@app.get("/api/council/status")
def council_status():
    return council.council_status()

@app.get("/api/council/activity")
def activity_log(limit: int = 20):
    return {"log": council.activity_log(limit=limit)}

@app.post("/api/council/dispatch")
def council_dispatch(req: DispatchRequest):
    result = council.dispatch(req.task, req.payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ---------------------------------------------------------------------------
# Finance agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/finance/budget")
def finance_budget(req: BudgetRequest):
    return council.agents["finance"].analyze_budget({"allocations": req.allocations, "actuals": req.actuals})

@app.post("/api/agents/finance/forecast")
def finance_forecast(req: ForecastRequest):
    return council.agents["finance"].forecast_revenue(req.historical, req.periods)

@app.post("/api/agents/finance/risk")
def finance_risk(req: RiskRequest):
    return council.agents["finance"].risk_assessment(req.factors)

@app.get("/api/agents/finance/report")
def finance_report():
    return council.agents["finance"].generate_report()


# ---------------------------------------------------------------------------
# Operations agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/operations/kpis")
def ops_kpis(req: KpiRequest):
    return council.agents["operations"].track_kpis(req.kpis, req.targets)

@app.get("/api/agents/operations/report")
def ops_report():
    return council.agents["operations"].generate_report()


# ---------------------------------------------------------------------------
# Strategy agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/strategy/market")
def strategy_market(req: MarketRequest):
    return council.agents["strategy"].analyze_market(req.model_dump())

@app.get("/api/agents/strategy/report")
def strategy_report():
    return council.agents["strategy"].generate_report()


# ---------------------------------------------------------------------------
# Document agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/document/process")
def document_process(req: DocumentRequest):
    return council.agents["document"].process_document(req.model_dump())

@app.post("/api/agents/document/summarise")
def document_summarise(req: SummariseRequest):
    return council.agents["document"].summarise(req.text, req.max_sentences)

@app.get("/api/agents/document/report")
def document_report():
    return council.agents["document"].get_status()


# ---------------------------------------------------------------------------
# Watchtower agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/watchtower/alert")
def watchtower_alert(req: AlertRequest):
    return council.agents["watchtower"].send_alert(req.model_dump())

@app.get("/api/agents/watchtower/alerts")
def watchtower_alerts(unacknowledged_only: bool = False):
    return {"alerts": council.agents["watchtower"].get_alerts(unacknowledged_only=unacknowledged_only)}

@app.get("/api/agents/watchtower/uptime")
def watchtower_uptime():
    return council.agents["watchtower"].uptime()

@app.get("/api/agents/watchtower/report")
def watchtower_report():
    return council.agents["watchtower"].generate_report()


# ---------------------------------------------------------------------------

