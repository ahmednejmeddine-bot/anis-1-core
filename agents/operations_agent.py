"""
OperationsAgent – Monitors business processes, tracks KPIs,
manages workflow optimisation, and handles incident response.
"""

from datetime import datetime
from typing import Any


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
    def monitor_processes(self, processes: list[dict[str, Any]]) -> dict[str, Any]:
        """Evaluate a list of running processes and flag unhealthy ones."""
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
        """Compare current KPI values against targets and score performance."""
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
        """Identify bottlenecks in a workflow and suggest improvements."""
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
        """Log an incident and return a response action plan."""
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
