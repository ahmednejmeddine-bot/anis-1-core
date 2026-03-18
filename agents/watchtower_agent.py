"""
WatchtowerAgent – Continuously monitors system health, detects anomalies,
manages alerts, and provides a real-time status overview of all ANIS-1 components.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

SYSTEM_PROMPT = """You are the WatchtowerAgent for Abdeljelil Group, part of the ANIS-1 Autonomous Neural Intelligence System.

Abdeljelil Group operates capital-intensive industrial manufacturing and packaging/converting assets where undetected risks can cause costly production stoppages, financial losses, or reputational damage. Your mandate is to provide 24/7 early-warning intelligence — surfacing threats before they escalate into incidents that harm production output, cash flow, or strategic position.

Specialisation — monitor and reason across four risk dimensions:

1. OPERATIONAL RISK
   - Machine failure signals: abnormal vibration, temperature, energy draw, or error codes.
   - Production pace anomalies: OEE drops >5% below baseline, throughput below plan for >2 consecutive shifts.
   - Quality deviation trends: scrap rate increasing, customer complaints, non-conformance reports.
   - Safety near-misses and unsafe conditions — always CRITICAL severity.
   - Maintenance overdue: assets past scheduled PM interval or with open high-severity work orders.

2. FINANCIAL RISK SIGNALS
   - Receivables ageing beyond agreed terms; key customer payment delays as early warning of distress.
   - Cost overruns vs. budget by >5% in any category; EBITDA margin compression trend.
   - Raw material price spikes >10% vs. budget — assess pass-through ability vs. margin impact.
   - Working capital deterioration: inventory build-up, cash conversion cycle lengthening.
   - Covenant proximity: flag when DSCR or leverage ratio approaches trigger thresholds.

3. WEAK SIGNALS & DISRUPTION RISKS
   - Supplier distress indicators: late deliveries, quality rejections, news of financial difficulty.
   - Energy price trends and utility availability risks (power cuts, gas supply restrictions).
   - Logistics disruptions: port congestion, freight rate spikes, cross-border delay trends.
   - Geopolitical developments affecting raw material origins or export markets.
   - Key personnel attrition in critical operational or technical roles.

4. STRATEGIC THREATS
   - Competitor capacity expansions or new product launches in Abdeljelil Group's core segments.
   - Technology disruption: alternative packaging materials, new automation entrants undercutting costs.
   - Regulatory changes: environmental standards, labelling requirements, import/export restrictions.
   - Customer concentration risk: revenue dependency on top-3 customers and signs of churn.

Behavioural guidelines:
- Alert format: SEVERITY | Signal Description | Impact Assessment | Recommended Response | Escalation Path.
- Severity: CRITICAL (immediate action, CEO/Board escalation) → HIGH (24h response, VP level) → MEDIUM (weekly review, department head) → LOW (logged, monitored).
- Correlate signals across dimensions: an OEE dip + material delay + margin compression together signal compounding risk — assess the combined exposure, not each in isolation.
- Provide leading indicators: flag the early warning before the outcome materialises.
- Never suppress a signal to reduce noise; a false positive costs time, a false negative costs money.

Tone: Vigilant, concise, urgent when the situation demands it.
Scope: Operational alerts · Financial risk signals · Weak signal detection · Supply chain disruption · Strategic threats · Regulatory & cyber risk."""


class WatchtowerAgent:
    name = "WatchtowerAgent"
    description = "AI agent for system health monitoring, anomaly detection, and alerting."
    capabilities = [
        "health_check",
        "anomaly_detection",
        "alert_management",
        "uptime_tracking",
        "performance_profiling",
    ]

    def __init__(self):
        self.status = "active"
        self.last_run: datetime | None = None
        self._alerts: list[dict[str, Any]] = []
        self._uptime_start = datetime.utcnow()

    # ------------------------------------------------------------------
    # AI-powered method
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Send a free-form task to OpenAI using the WatchtowerAgent system prompt."""
        self.last_run = datetime.utcnow()

        user_message = f"Context:\n{context}\n\nTask:\n{task_description}" if context else task_description

        try:
            response = chat(SYSTEM_PROMPT, user_message)
            return {
                "agent": self.name,
                "task": task_description,
                "timestamp": datetime.utcnow().isoformat(),
                "response": response,
                "model": "gpt-4o",
            }
        except LLMError as exc:
            return {"agent": self.name, "error": str(exc), "timestamp": datetime.utcnow().isoformat()}

    # ------------------------------------------------------------------
    # Deterministic methods (unchanged)
    # ------------------------------------------------------------------

    def health_check(self, components: list[dict[str, Any]]) -> dict[str, Any]:
        self.last_run = datetime.utcnow()

        results: list[dict[str, Any]] = []
        for c in components:
            status = c.get("status", "unknown")
            latency_ms = c.get("latency_ms", 0)
            healthy = status == "up" and latency_ms < c.get("latency_threshold_ms", 500)
            results.append({
                "component": c.get("name"),
                "status": status,
                "latency_ms": latency_ms,
                "healthy": healthy,
                "note": "" if healthy else f"Latency {latency_ms}ms exceeds threshold" if latency_ms >= c.get("latency_threshold_ms", 500) else f"Status: {status}",
            })

        overall = "healthy" if all(r["healthy"] for r in results) else "degraded" if any(r["healthy"] for r in results) else "down"
        return {
            "agent": self.name,
            "task": "health_check",
            "timestamp": datetime.utcnow().isoformat(),
            "overall": overall,
            "components": results,
            "healthy_count": sum(1 for r in results if r["healthy"]),
            "total_count": len(results),
        }

    def detect_anomalies(self, metrics: dict[str, list[float]]) -> dict[str, Any]:
        self.last_run = datetime.utcnow()

        anomalies: dict[str, Any] = {}
        for metric, values in metrics.items():
            if len(values) < 2:
                continue
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = variance ** 0.5
            outliers = [v for v in values if abs(v - mean) > 2 * std]
            if outliers:
                anomalies[metric] = {
                    "mean": round(mean, 3),
                    "std": round(std, 3),
                    "outliers": outliers,
                    "severity": "high" if len(outliers) > len(values) * 0.2 else "medium",
                }

        return {
            "agent": self.name,
            "task": "anomaly_detection",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_scanned": len(metrics),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
        }

    def send_alert(self, alert: dict[str, Any]) -> dict[str, Any]:
        self.last_run = datetime.utcnow()

        record = {
            "alert_id": f"ALT-{len(self._alerts) + 1:04d}",
            "severity": alert.get("severity", "info"),
            "message": alert.get("message", "No message provided"),
            "component": alert.get("component", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "acknowledged": False,
        }
        self._alerts.append(record)
        return {"agent": self.name, "task": "alert_sent", "alert": record}

    def acknowledge_alert(self, alert_id: str) -> dict[str, Any]:
        for alert in self._alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                return {"agent": self.name, "acknowledged": True, "alert_id": alert_id}
        return {"agent": self.name, "acknowledged": False, "error": f"Alert {alert_id} not found"}

    def get_alerts(self, unacknowledged_only: bool = False) -> list[dict[str, Any]]:
        if unacknowledged_only:
            return [a for a in self._alerts if not a["acknowledged"]]
        return list(self._alerts)

    def uptime(self) -> dict[str, Any]:
        delta = datetime.utcnow() - self._uptime_start
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            "agent": self.name,
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "uptime_seconds": int(delta.total_seconds()),
            "started_at": self._uptime_start.isoformat(),
        }

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_alerts": len(self._alerts),
            "unacknowledged_alerts": len([a for a in self._alerts if not a["acknowledged"]]),
            "uptime": self.uptime()["uptime"],
        }
