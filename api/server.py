"""
ANIS-1 API Server – FastAPI backend exposing all agent capabilities
and the AICouncil orchestration layer via a RESTful interface.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from council.ai_council import AICouncil

# ---------------------------------------------------------------------------
app = FastAPI(
    title="ANIS-1 API",
    description="Autonomous Neural Intelligence System – Abdeljelil Group",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

council = AICouncil()

# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

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
# Root + health
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"system": "ANIS-1", "group": "Abdeljelil Group", "status": "online", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ---------------------------------------------------------------------------
# Council endpoints
# ---------------------------------------------------------------------------

@app.get("/api/council/status")
def council_status():
    return council.council_status()

@app.get("/api/council/agents")
def list_agents():
    return {"agents": council.agent_list()}

@app.get("/api/council/activity")
def activity_log(limit: int = 20):
    return {"log": council.activity_log(limit=limit)}

@app.post("/api/council/dispatch")
def dispatch(req: DispatchRequest):
    result = council.dispatch(req.task, req.payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# ---------------------------------------------------------------------------
# Finance agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/finance/budget")
def finance_budget(req: BudgetRequest):
    agent = council.agents["finance"]
    return agent.analyze_budget({"allocations": req.allocations, "actuals": req.actuals})

@app.post("/api/agents/finance/forecast")
def finance_forecast(req: ForecastRequest):
    agent = council.agents["finance"]
    return agent.forecast_revenue(req.historical, req.periods)

@app.post("/api/agents/finance/risk")
def finance_risk(req: RiskRequest):
    agent = council.agents["finance"]
    return agent.risk_assessment(req.factors)

@app.get("/api/agents/finance/report")
def finance_report():
    return council.agents["finance"].generate_report()

# ---------------------------------------------------------------------------
# Operations agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/operations/kpis")
def ops_kpis(req: KpiRequest):
    agent = council.agents["operations"]
    return agent.track_kpis(req.kpis, req.targets)

@app.get("/api/agents/operations/report")
def ops_report():
    return council.agents["operations"].generate_report()

# ---------------------------------------------------------------------------
# Strategy agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/strategy/market")
def strategy_market(req: MarketRequest):
    agent = council.agents["strategy"]
    return agent.analyze_market(req.model_dump())

@app.get("/api/agents/strategy/report")
def strategy_report():
    return council.agents["strategy"].generate_report()

# ---------------------------------------------------------------------------
# Document agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/document/process")
def document_process(req: DocumentRequest):
    agent = council.agents["document"]
    return agent.process_document(req.model_dump())

@app.post("/api/agents/document/summarise")
def document_summarise(req: SummariseRequest):
    agent = council.agents["document"]
    return agent.summarise(req.text, req.max_sentences)

@app.get("/api/agents/document/report")
def document_report():
    return council.agents["document"].get_status()

# ---------------------------------------------------------------------------
# Watchtower agent endpoints
# ---------------------------------------------------------------------------

@app.post("/api/agents/watchtower/alert")
def watchtower_alert(req: AlertRequest):
    agent = council.agents["watchtower"]
    return agent.send_alert(req.model_dump())

@app.get("/api/agents/watchtower/alerts")
def watchtower_alerts(unacknowledged_only: bool = False):
    agent = council.agents["watchtower"]
    return {"alerts": agent.get_alerts(unacknowledged_only=unacknowledged_only)}

@app.get("/api/agents/watchtower/uptime")
def watchtower_uptime():
    return council.agents["watchtower"].uptime()

@app.get("/api/agents/watchtower/report")
def watchtower_report():
    return council.agents["watchtower"].generate_report()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="localhost", port=8000, reload=True)
