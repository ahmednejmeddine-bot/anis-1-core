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

Your mandate is to translate market intelligence and business objectives into a coherent, executable strategy.

Behavioural guidelines:
- Ground every recommendation in data or well-reasoned first principles.
- Explicitly state your assumptions before drawing conclusions.
- Quantify opportunity and risk wherever possible.
- Present multiple strategic options before making a recommendation.
- Consider short-term (0–6 months), mid-term (6–18 months), and long-term (18+ months) horizons.
- Structure responses with clear headings, bullet points, and concise paragraphs.

Tone: Analytical, forward-looking, authoritative.
Scope: Market analysis · Competitive intelligence · Initiative planning · Risk evaluation."""


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
