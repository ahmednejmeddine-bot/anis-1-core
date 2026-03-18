"""
AICouncil – Central orchestrator for ANIS-1.
Routes tasks to the appropriate specialised agent, aggregates multi-agent
responses, and maintains a unified activity log across all council members.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from agents.finance_agent import FinanceAgent
from agents.operations_agent import OperationsAgent
from agents.strategy_agent import StrategyAgent
from agents.document_agent import DocumentAgent
from agents.watchtower_agent import WatchtowerAgent
from agents.reviewer_agent import ReviewerAgent


TASK_ROUTING: dict[str, list[str]] = {
    "budget_analysis": ["finance"],
    "revenue_forecasting": ["finance"],
    "risk_assessment": ["finance", "strategy"],
    "financial_reporting": ["finance"],
    "process_monitoring": ["operations"],
    "kpi_tracking": ["operations"],
    "workflow_optimization": ["operations"],
    "incident_response": ["operations", "watchtower"],
    "market_analysis": ["strategy"],
    "competitive_intelligence": ["strategy"],
    "initiative_planning": ["strategy"],
    "goal_tracking": ["strategy"],
    "document_summarisation": ["document"],
    "data_extraction": ["document"],
    "report_generation": ["document"],
    "document_classification": ["document"],
    "health_check": ["watchtower"],
    "anomaly_detection": ["watchtower"],
    "alert_management": ["watchtower"],
    "uptime_tracking": ["watchtower"],
}


class AICouncil:
    """
    The AICouncil coordinates all ANIS-1 agents. It:
    - Routes incoming tasks to the correct agent(s).
    - Aggregates and returns combined responses.
    - Maintains a full activity log.
    - Provides a system-wide status view.
    """

    def __init__(self):
        self.agents: dict[str, Any] = {
            "finance": FinanceAgent(),
            "operations": OperationsAgent(),
            "strategy": StrategyAgent(),
            "document": DocumentAgent(),
            "watchtower": WatchtowerAgent(),
            "reviewer": ReviewerAgent(),
        }
        self._activity_log: list[dict[str, Any]] = []
        self._session_start = datetime.utcnow()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dispatch(self, task: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Dispatch a task to all agents responsible for it.
        Returns a unified response envelope.
        """
        payload = payload or {}
        responsible = TASK_ROUTING.get(task, [])

        if not responsible:
            return self._error(f"Unknown task: '{task}'. No agent is registered for it.")

        results: list[dict[str, Any]] = []
        for agent_key in responsible:
            agent = self.agents.get(agent_key)
            if agent is None:
                continue
            try:
                result = self._invoke(agent, task, payload)
                results.append(result)
            except Exception as exc:
                results.append({"agent": agent_key, "error": str(exc)})

        entry = {
            "task": task,
            "agents_dispatched": responsible,
            "timestamp": datetime.utcnow().isoformat(),
            "payload_keys": list(payload.keys()),
        }
        self._activity_log.append(entry)

        return {
            "council": "ANIS-1 AICouncil",
            "task": task,
            "dispatched_to": responsible,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
        }

    def council_status(self) -> dict[str, Any]:
        """Return a full status report for all agents and the council itself."""
        agent_reports = {}
        for key, agent in self.agents.items():
            report_fn = getattr(agent, "generate_report", None) or getattr(agent, "get_status", None)
            agent_reports[key] = report_fn() if report_fn else {"status": "unknown"}

        delta = datetime.utcnow() - self._session_start
        return {
            "council": "ANIS-1 AICouncil",
            "session_uptime_s": int(delta.total_seconds()),
            "session_started": self._session_start.isoformat(),
            "total_tasks_dispatched": len(self._activity_log),
            "agents": agent_reports,
        }

    def activity_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent activity log entries."""
        return self._activity_log[-limit:]

    def agent_list(self) -> list[dict[str, Any]]:
        """Return a lightweight summary of all registered agents."""
        return [
            {
                "id": key,
                "name": getattr(agent, "name", key),
                "description": getattr(agent, "description", ""),
                "capabilities": getattr(agent, "capabilities", []),
                "status": getattr(agent, "status", "unknown"),
            }
            for key, agent in self.agents.items()
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _invoke(self, agent: Any, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Map a task name to the correct agent method and call it."""
        method_map: dict[str, str] = {
            "budget_analysis": "analyze_budget",
            "revenue_forecasting": "forecast_revenue",
            "risk_assessment": "risk_assessment",
            "financial_reporting": "generate_report",
            "process_monitoring": "monitor_processes",
            "kpi_tracking": "track_kpis",
            "workflow_optimization": "optimize_workflow",
            "incident_response": "incident_response",
            "market_analysis": "analyze_market",
            "competitive_intelligence": "competitive_analysis",
            "initiative_planning": "plan_initiatives",
            "goal_tracking": "generate_report",
            "document_summarisation": "summarise",
            "data_extraction": "extract_data",
            "report_generation": "generate_report",
            "document_classification": "process_document",
            "health_check": "health_check",
            "anomaly_detection": "detect_anomalies",
            "alert_management": "get_alerts",
            "uptime_tracking": "uptime",
        }
        method_name = method_map.get(task, "generate_report")
        method = getattr(agent, method_name, agent.generate_report if hasattr(agent, "generate_report") else None)
        if method is None:
            return {"agent": getattr(agent, "name", "unknown"), "error": f"No method for task '{task}'"}
        return method(**payload) if payload else method()

    def _error(self, message: str) -> dict[str, Any]:
        return {"council": "ANIS-1 AICouncil", "error": message, "timestamp": datetime.utcnow().isoformat()}
