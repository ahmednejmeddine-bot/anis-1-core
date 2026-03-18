"""
StrategyAgent – Handles market analysis, strategic initiative planning,
competitive intelligence, and long-term goal evaluation.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

SYSTEM_PROMPT = """You are the StrategyAgent for Abdeljelil Group, part of the ANIS-1 Autonomous Neural Intelligence System.

Abdeljelil Group is an industrial manufacturing and packaging/converting group with ambitions for regional expansion, operational excellence, and technology-driven transformation. Your mandate is to develop strategies that strengthen competitive position, allocate capital to its highest-return uses, and build durable advantages in the Group's core and adjacent markets.

Specialisation — reason explicitly about:
- Market expansion: evaluate MENA and Sub-Saharan Africa opportunities — demand size, growth rate, localisation requirements (regulatory, language, distribution), tariff structures, and competitive intensity. Prioritise markets by attractiveness × strategic fit.
- Competitive positioning: assess cost leadership vs. differentiation options in industrial packaging and converting. Identify segments where Abdeljelil Group has pricing power and segments under commoditisation pressure.
- Investment priorities: frame every investment as a choice: capacity expansion vs. productivity improvement vs. new product lines. Apply IRR, NPV, and payback criteria. Automation ROI must include productivity gain, headcount impact, and maintenance cost.
- AI & Industry 4.0 transformation: IoT sensor deployment for predictive maintenance, MES/ERP integration for real-time production visibility, digital twin feasibility, AI-driven demand forecasting. Sequence investments by dependency and ROI.
- Growth levers: vertical integration (upstream into raw materials, downstream into distribution), adjacent product categories, B2B contract vs. spot revenue mix optimisation, private label opportunities.
- M&A and partnerships: strategic rationale, integration complexity, synergy quantification (revenue + cost), cultural and operational fit.
- Strategic risks: single-market dependency, energy price exposure, raw material supply concentration, regulatory change, technology disruption (alternative materials, new entrants).

Behavioural guidelines:
- State all assumptions explicitly before drawing conclusions; distinguish what is known from what is estimated.
- Present 2–3 distinct strategic options with pros, cons, required investment, and expected financial outcome for each.
- Always specify time horizon: immediate (0–3 months), near-term (3–12 months), medium-term (1–3 years), long-term (3+ years).
- Every recommendation must include a measurable success criterion and a named risk that could invalidate the recommendation.
- Structure every response: Strategic Context → Options Analysis (with financials) → Recommended Path → Success Metrics → Key Risks.

Tone: Analytical, commercially grounded, decisively forward-looking.
Scope: Market expansion · Competitive positioning · Investment prioritisation · AI/Industry 4.0 · Vertical integration · M&A · Strategic risk."""


class StrategyAgent:
    name = "StrategyAgent"
    description = "AI agent for strategic planning, market analysis, and competitive intelligence."
    capabilities = [
        "market_analysis",
        "competitive_intelligence",
        "initiative_planning",
        "risk_evaluation",
        "goal_tracking",
    ]

    def __init__(self):
        self.status = "idle"
        self.last_run: datetime | None = None
        self._initiatives: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # AI-powered method
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Send a free-form task to OpenAI using the StrategyAgent system prompt."""
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

    def analyze_market(self, market_data: dict[str, Any]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        growth_rate = market_data.get("growth_rate_pct", 0)
        competition = market_data.get("competition_level", "medium")
        market_size = market_data.get("market_size_usd", 0)

        opportunity_score = round(
            (growth_rate / 100) * (1 if competition == "low" else 0.6 if competition == "medium" else 0.3) * min(market_size / 1e9, 1),
            2,
        )

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "market_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "market": market_data.get("name", "unknown"),
            "growth_rate_pct": growth_rate,
            "competition_level": competition,
            "opportunity_score": opportunity_score,
            "recommendation": "pursue" if opportunity_score > 0.5 else "monitor" if opportunity_score > 0.2 else "avoid",
        }

    def competitive_analysis(self, competitors: list[dict[str, Any]]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        scored = []
        for c in competitors:
            threat_score = round(
                (c.get("market_share_pct", 0) / 100) * 0.4
                + (1 if c.get("funding") == "high" else 0.5 if c.get("funding") == "medium" else 0.2) * 0.3
                + (c.get("innovation_index", 0.5)) * 0.3,
                2,
            )
            scored.append({"name": c.get("name"), "threat_score": threat_score})

        scored.sort(key=lambda x: x["threat_score"], reverse=True)
        self.status = "idle"
        return {
            "agent": self.name,
            "task": "competitive_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "competitors_scored": scored,
            "top_threat": scored[0]["name"] if scored else None,
        }

    def plan_initiatives(self, objectives: list[str], horizon_months: int = 12) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        phases = []
        phase_size = max(len(objectives) // 3, 1)
        for i, chunk_start in enumerate(range(0, len(objectives), phase_size)):
            chunk = objectives[chunk_start: chunk_start + phase_size]
            phases.append({
                "phase": i + 1,
                "name": f"Phase {i + 1}",
                "objectives": chunk,
                "timeline_months": f"Month {i * (horizon_months // 3) + 1}–{(i + 1) * (horizon_months // 3)}",
                "priority": "high" if i == 0 else "medium" if i == 1 else "low",
            })

        self._initiatives.extend(phases)
        self.status = "idle"
        return {
            "agent": self.name,
            "task": "initiative_planning",
            "timestamp": datetime.utcnow().isoformat(),
            "horizon_months": horizon_months,
            "total_objectives": len(objectives),
            "phases": phases,
        }

    def evaluate_risks(self, strategy: str, risk_factors: list[str]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        factor_scores = {f: round(len(f) % 10 / 10 + 0.1, 2) for f in risk_factors}
        mitigations = {f: f"Monitor and hedge against {f}" for f in risk_factors}
        composite = round(sum(factor_scores.values()) / max(len(factor_scores), 1), 2)

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "risk_evaluation",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy": strategy,
            "factor_scores": factor_scores,
            "mitigations": mitigations,
            "composite_risk": composite,
            "risk_level": "high" if composite > 0.6 else "medium" if composite > 0.35 else "low",
        }

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "active_initiatives": len(self._initiatives),
        }
