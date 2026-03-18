"""
OperationsAgent – Monitors business processes, tracks KPIs,
manages workflow optimisation, and handles incident response.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

SYSTEM_PROMPT = """You are the OperationsAgent for Abdeljelil Group, part of the ANIS-1 Autonomous Neural Intelligence System.

Abdeljelil Group operates industrial manufacturing and packaging/converting production lines. Your mandate is to maximise factory performance, eliminate waste, reduce unplanned downtime, and drive continuous improvement across all production assets.

Specialisation — reason explicitly about:
- OEE (Overall Equipment Effectiveness): Availability × Performance × Quality. World-class target ≥ 85%; flag anything below 70% as CRITICAL; quantify the production volume and revenue lost.
- Downtime: distinguish planned (scheduled maintenance, changeovers, shift breaks) from unplanned (breakdowns, material shortages, operator errors). Track MTBF (Mean Time Between Failures) and MTTR (Mean Time To Repair).
- Maintenance strategy: assess maturity level (reactive → preventive → predictive). Prioritise assets by criticality (impact of failure × failure probability). Recommend condition-based monitoring where ROI is justified.
- Throughput & capacity: actual vs. nameplate capacity, units/hour, tons/shift. Identify the system constraint using Theory of Constraints; improving non-constraints does not increase throughput.
- Quality losses: scrap rate (%), rework rate (%), first-pass yield (FPY). Trace defects to root cause using 5-Why or Ishikawa. Calculate the full cost of poor quality (COPQ).
- Supply chain bottlenecks: raw material availability vs. production schedule, supplier lead time variability, packaging component stockouts, inbound logistics delays.
- Changeover & setup: SMED analysis; target changeover time <10% of available production time. Quantify lost production per changeover.
- Energy & utilities: energy consumption (kWh or GJ) per ton of output; identify the top 3 energy-consuming assets and their optimisation potential.
- Safety: every safety event or near-miss is severity CRITICAL regardless of outcome. Track LTI rate and near-miss frequency as leading indicators.

Behavioural guidelines:
- Severity: CRITICAL (line stopped / safety event / >20% OEE impact) → HIGH (>10% OEE impact / imminent failure) → MEDIUM (monitored degradation) → LOW (minor inefficiency).
- Always include root-cause hypothesis and at least one corrective action with owner, deadline, and measurable target.
- Quantify the cost of every significant downtime event: lost revenue per hour, recovery cost, customer impact.
- Structure every response: Current Performance vs. Target → Root Cause → Action Plan → Expected Impact.

Tone: Operational, factory-floor grounded, methodical.
Scope: OEE · Downtime/MTBF/MTTR · Maintenance strategy · Throughput · Quality/COPQ · Supply chain · Changeover · Energy · Safety."""


class OperationsAgent:
    name = "OperationsAgent"
    description = "AI agent for process monitoring, KPI tracking, and operational optimisation."
    capabilities = [
        "process_monitoring",
        "kpi_tracking",
        "workflow_optimization",
        "incident_response",
        "capacity_planning",
    ]

    def __init__(self):
        self.status = "idle"
        self.last_run: datetime | None = None
        self._active_incidents: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # AI-powered method
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Send a free-form task to OpenAI using the OperationsAgent system prompt."""
        self.status = "active"
        self.last_run = datetime.utcnow()

        user_message = f"Context:\n{context}\n\nTask:\n{task_description}" if context else task_description

        try:
            response = chat(SYSTEM_PROMPT, user_message)
            self.status = "idle"
            return {
                "agent": self.name,
                "task": task_description,
                "timestamp": datetime.utcnow().isoformat(),
                "response": response,
                "model": "gpt-4o",
            }
        except LLMError as exc:
            self.status = "idle"
            return {"agent": self.name, "error": str(exc), "timestamp": datetime.utcnow().isoformat()}

    # ------------------------------------------------------------------
    # Deterministic methods (unchanged)
    # ------------------------------------------------------------------

    def monitor_processes(self, processes: list[dict[str, Any]]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        healthy, degraded, down = [], [], []
        for p in processes:
            health = p.get("health", "unknown")
            if health == "healthy":
                healthy.append(p["name"])
            elif health == "degraded":
                degraded.append(p["name"])
            else:
                down.append(p["name"])

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "process_monitoring",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total": len(processes),
                "healthy": healthy,
                "degraded": degraded,
                "down": down,
                "overall_health": "critical" if down else "degraded" if degraded else "healthy",
            },
        }

    def track_kpis(self, kpis: dict[str, float], targets: dict[str, float]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        scores: dict[str, dict[str, Any]] = {}
        for key, value in kpis.items():
            target = targets.get(key, 0)
            pct = round((value / target * 100), 1) if target else 0.0
            scores[key] = {
                "actual": value,
                "target": target,
                "achievement_pct": pct,
                "status": "on_track" if pct >= 90 else "at_risk" if pct >= 70 else "off_track",
            }

        overall = round(sum(s["achievement_pct"] for s in scores.values()) / max(len(scores), 1), 1)
        self.status = "idle"
        return {
            "agent": self.name,
            "task": "kpi_tracking",
            "timestamp": datetime.utcnow().isoformat(),
            "kpis": scores,
            "overall_performance_pct": overall,
        }

    def optimize_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        steps = workflow.get("steps", [])
        bottlenecks = [s for s in steps if s.get("avg_duration_s", 0) > s.get("sla_s", 9999)]
        suggestions = [f"Optimise step '{s['name']}': avg {s['avg_duration_s']}s vs SLA {s['sla_s']}s" for s in bottlenecks]

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "workflow_optimization",
            "timestamp": datetime.utcnow().isoformat(),
            "workflow": workflow.get("name", "unknown"),
            "total_steps": len(steps),
            "bottlenecks_found": len(bottlenecks),
            "suggestions": suggestions,
        }

    def incident_response(self, incident: dict[str, Any]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        severity = incident.get("severity", "low")
        actions = {
            "critical": ["Page on-call team", "Initiate war room", "Escalate to leadership"],
            "high": ["Alert on-call team", "Start root-cause analysis", "Notify stakeholders"],
            "medium": ["Create ticket", "Assign to ops team", "Monitor for escalation"],
            "low": ["Log incident", "Schedule review"],
        }

        plan = {
            "incident_id": incident.get("id", f"INC-{int(datetime.utcnow().timestamp())}"),
            "severity": severity,
            "actions": actions.get(severity, ["Log and monitor"]),
            "estimated_resolution": "30m" if severity == "critical" else "2h" if severity == "high" else "24h",
        }
        self._active_incidents.append(plan)
        self.status = "idle"
        return {"agent": self.name, "task": "incident_response", "timestamp": datetime.utcnow().isoformat(), "plan": plan}

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "active_incidents": len(self._active_incidents),
        }
