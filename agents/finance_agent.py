"""
FinanceAgent – Handles financial analysis, budget tracking,
revenue forecasting, and risk assessment for Abdeljelil Group.
"""

from datetime import datetime
from typing import Any


class FinanceAgent:
    name = "FinanceAgent"
    description = "AI agent for financial analysis, forecasting, and risk management."
    capabilities = [
        "budget_analysis",
        "revenue_forecasting",
        "risk_assessment",
        "expense_tracking",
        "financial_reporting",
    ]

    def __init__(self):
        self.status = "idle"
        self.last_run: datetime | None = None

    # ------------------------------------------------------------------
    def analyze_budget(self, budget_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze budget allocations and flag overspend categories."""
        self.status = "active"
        self.last_run = datetime.utcnow()
        results: dict[str, Any] = {"agent": self.name, "task": "budget_analysis", "timestamp": self.last_run.isoformat()}

        total_allocated = sum(budget_data.get("allocations", {}).values())
        total_spent = sum(budget_data.get("actuals", {}).values())
        variance = total_allocated - total_spent

        overspend = {
            k: v - budget_data["allocations"].get(k, 0)
            for k, v in budget_data.get("actuals", {}).items()
            if v > budget_data["allocations"].get(k, 0)
        }

        results["summary"] = {
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "variance": variance,
            "overspend_categories": overspend,
            "health": "healthy" if variance >= 0 else "over_budget",
        }
        self.status = "idle"
        return results

    def forecast_revenue(self, historical: list[float], periods: int = 3) -> dict[str, Any]:
        """Simple moving-average revenue forecast for the next N periods."""
        self.status = "active"
        self.last_run = datetime.utcnow()

        if not historical:
            return {"agent": self.name, "error": "No historical data provided"}

        window = min(len(historical), 3)
        avg = sum(historical[-window:]) / window
        forecast = [round(avg * (1 + 0.02 * i), 2) for i in range(1, periods + 1)]

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "revenue_forecast",
            "timestamp": datetime.utcnow().isoformat(),
            "periods": periods,
            "forecast": forecast,
            "trend": "upward" if forecast[-1] > forecast[0] else "flat",
        }

    def risk_assessment(self, factors: list[str]) -> dict[str, Any]:
        """Score financial risk factors and return a composite risk level."""
        self.status = "active"
        self.last_run = datetime.utcnow()

        risk_weights = {
            "high_debt": 0.9,
            "currency_exposure": 0.7,
            "low_cash_reserves": 0.8,
            "market_volatility": 0.6,
            "regulatory_changes": 0.5,
            "supply_chain": 0.4,
        }

        scored = {f: risk_weights.get(f, 0.3) for f in factors}
        composite = round(sum(scored.values()) / max(len(scored), 1), 2) if scored else 0.0
        level = "critical" if composite > 0.75 else "high" if composite > 0.5 else "moderate" if composite > 0.25 else "low"

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "risk_assessment",
            "timestamp": datetime.utcnow().isoformat(),
            "factors": scored,
            "composite_score": composite,
            "risk_level": level,
        }

    def generate_report(self) -> dict[str, Any]:
        """Return an agent status and capability summary."""
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }
