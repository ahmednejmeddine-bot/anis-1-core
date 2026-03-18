"""
ReviewerAgent – Final-stage synthesis agent for ANIS-1.

Sits at the end of every CrewAI crew execution.  It reads all prior agent
outputs, detects contradictions or gaps, sharpens the language, and produces
a structured 9-section Executive Report for Abdeljelil Group leadership.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

# ---------------------------------------------------------------------------
# CrewAI agent config (consumed by crew_service.py)
# ---------------------------------------------------------------------------

CREWAI_CONFIG: dict[str, str] = {
    "role": "AI Project Reviewer & Executive Synthesiser",
    "goal": (
        "Review and synthesise the outputs of all ANIS-1 specialist agents into a single, "
        "coherent, contradiction-free executive report that Abdeljelil Group leadership can act on."
    ),
    "backstory": (
        "You are the ReviewerAgent for Abdeljelil Group, the final intelligence layer in the "
        "ANIS-1 Autonomous Neural Intelligence System.  "
        "After all specialist agents have contributed their domain analyses, you receive their "
        "combined work and perform three duties:\n"
        "  1. Contradiction detection – identify any conflicting figures, assumptions, or "
        "recommendations across agents and flag or resolve them.\n"
        "  2. Clarity improvement – rewrite any sections that are ambiguous, repetitive, or "
        "lack actionable specificity.\n"
        "  3. Executive synthesis – assemble a final 9-section report that is precise, "
        "leadership-ready, and prioritised by urgency and impact.\n\n"
        "You never add new data; you only evaluate, resolve, and synthesise what the agents "
        "have already produced.  "
        "Tone: authoritative, balanced, decisive.  "
        "Format: clear section headings, numbered recommendations, explicit risk callouts."
    ),
}

# System prompt for the standalone ask() method (single-agent mode)
_SYSTEM_PROMPT = f"""You are the ReviewerAgent for Abdeljelil Group, part of the ANIS-1 system.

{CREWAI_CONFIG['backstory']}

When you produce the final report, always use this exact 9-section structure:

1. Executive Summary
2. Financial Analysis
3. Operations Assessment
4. Strategic Recommendations
5. Document & Knowledge Assessment
6. Security & Monitoring Status
7. Cross-Agent Synthesis & Contradiction Resolution
8. Risk Summary
9. Final Recommendations & Next Steps

Tone: Authoritative, balanced, decisive.
Scope: Multi-agent review · Contradiction detection · Executive reporting · Synthesis."""


# ---------------------------------------------------------------------------
# ReviewerAgent class (ANIS-1 compatible)
# ---------------------------------------------------------------------------

class ReviewerAgent:
    name = "ReviewerAgent"
    description = (
        "AI meta-agent that reviews all specialist agent outputs, resolves contradictions, "
        "and produces a structured 9-section executive report."
    )
    capabilities = [
        "contradiction_detection",
        "executive_synthesis",
        "clarity_improvement",
        "cross_agent_review",
        "report_generation",
    ]

    def __init__(self) -> None:
        self.status = "idle"
        self.last_run: datetime | None = None
        self._reports_generated: int = 0

    # ------------------------------------------------------------------
    # AI-powered method (single-agent mode)
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Review task/context and produce a structured executive report."""
        self.status = "active"
        self.last_run = datetime.utcnow()

        user_message = (
            f"Context from specialist agents:\n{context}\n\nReview request:\n{task_description}"
            if context
            else task_description
        )

        try:
            response = chat(_SYSTEM_PROMPT, user_message)
            self.status = "idle"
            self._reports_generated += 1
            return {
                "agent": self.name,
                "task": task_description,
                "timestamp": datetime.utcnow().isoformat(),
                "response": response,
                "model": "gpt-4o",
            }
        except LLMError as exc:
            self.status = "idle"
            return {
                "agent": self.name,
                "error": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            }

    # ------------------------------------------------------------------
    # Deterministic report stub
    # ------------------------------------------------------------------

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "reports_generated": self._reports_generated,
        }
