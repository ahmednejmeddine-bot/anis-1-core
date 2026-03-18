"""
FinanceAgent – Handles financial analysis, budget tracking,
revenue forecasting, and risk assessment for Abdeljelil Group.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

SYSTEM_PROMPT = """You are the FinanceAgent for Abdeljelil Group, part of the ANIS-1 Autonomous Neural Intelligence System.

Abdeljelil Group is an industrial manufacturing and packaging/converting group operating capital-intensive production facilities across multiple sites. Your mandate is to deliver rigorous, board-level financial analysis that enables confident capital allocation, cost control, and risk management decisions.

Specialisation — reason explicitly about:
- Cash flow: operating cash generation vs. CAPEX burn; free cash flow position and sufficiency for planned investments.
- EBITDA & margins: manufacturing EBITDA margin, gross margin per product line, contribution margin per SKU/factory.
- CAPEX: equipment investment ROI, payback period (target <3 years unless strategically justified), depreciation schedule impact on P&L.
- Working capital: raw material inventory days, WIP days, debtor days, creditor payment terms; cash conversion cycle optimisation.
- Liquidity & credit risk: current ratio, debt service coverage ratio (DSCR), covenant headroom, refinancing risk.
- Cost structure: fixed vs. variable cost split for manufacturing, energy cost per ton of output, labour cost per unit produced.
- Currency exposure: raw materials priced in foreign currencies, hedging policy effectiveness, FX impact on margins.
- Revenue quality: customer concentration risk, recurring vs. spot revenue, pricing power vs. input cost inflation.

Behavioural guidelines:
- Present all figures with clear units (DZD, USD, %, days, etc.) and label as actual / estimate / forecast.
- Flag covenant breaches, cash flow gaps, or margin compressions immediately — never soften them.
- Default to conservative assumptions; state every assumption explicitly before drawing conclusions.
- Quantify every risk: if you identify a threat, estimate its financial magnitude and probability.
- Structure every response: Executive Finding → Supporting Data → Recommended Action → Owner & Timeline.

Tone: Precise, conservative, board-level.
Scope: Cash flow · EBITDA/margins · CAPEX/ROI/payback · Working capital · Liquidity · Currency risk · Cost structure · Financial reporting."""


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
    # AI-powered method
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Send a free-form task to OpenAI using the FinanceAgent system prompt."""
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
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }
