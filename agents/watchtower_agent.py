"""
WatchtowerAgent – Continuously monitors system health, detects anomalies,
manages alerts, and provides a real-time status overview of all ANIS-1 components.
"""

from datetime import datetime
from typing import Any


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
    def health_check(self, components: list[dict[str, Any]]) -> dict[str, Any]:
        """Perform a health sweep across all registered system components."""
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
        """Flag metric series that deviate significantly from their mean."""
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
        """Register an alert and return its tracking record."""
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
        """Mark an alert as acknowledged."""
        for alert in self._alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                return {"agent": self.name, "acknowledged": True, "alert_id": alert_id}
        return {"agent": self.name, "acknowledged": False, "error": f"Alert {alert_id} not found"}

    def get_alerts(self, unacknowledged_only: bool = False) -> list[dict[str, Any]]:
        """Return all (or only unacknowledged) alerts."""
        if unacknowledged_only:
            return [a for a in self._alerts if not a["acknowledged"]]
        return list(self._alerts)

    def uptime(self) -> dict[str, Any]:
        """Return how long the WatchtowerAgent has been running."""
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
