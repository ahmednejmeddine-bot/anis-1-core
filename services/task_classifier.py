"""
Task Classifier for ANIS-1.

Scores an incoming task against each agent's keyword domain and decides whether
to route to a single specialist agent or to escalate to a CrewAI multi-agent crew.
"""

import logging
from typing import Any

logger = logging.getLogger("anis1.classifier")

_AGENT_KEYWORDS: dict[str, list[str]] = {
    "finance": [
        "budget", "revenue", "forecast", "profit", "loss", "cash", "financial",
        "invoice", "expense", "cost", "funding", "roi", "margin", "investment",
        "capital", "spend", "earning", "valuation", "liquidity", "pricing",
        "subscription", "saas", "monetise", "monetize", "billing", "payment",
    ],
    "operations": [
        "process", "workflow", "kpi", "incident", "sla", "capacity", "operations",
        "monitoring", "performance", "bottleneck", "efficiency", "throughput",
        "logistics", "delivery", "pipeline", "team", "headcount", "build",
        "deploy", "launch", "implement", "platform", "infrastructure", "factory",
        "manufacturing", "production", "supply chain", "automation", "integration",
        "system", "service", "scalability", "architecture",
    ],
    "strategy": [
        "market", "strategy", "competitive", "initiative", "goal", "objective",
        "vision", "growth", "expansion", "opportunity", "positioning", "roadmap",
        "plan", "target", "direction", "partnership", "acquisition", "startup",
        "enterprise", "business", "saas", "product", "customer", "segment",
        "innovation", "differentiation", "go-to-market", "gtm", "disruption",
        "smart", "digital", "transformation", "industry",
    ],
    "document": [
        "document", "report", "summary", "extract", "draft", "write", "summarise",
        "classify", "text", "content", "note", "memo", "brief", "template",
        "presentation", "documentation", "proposal", "specification", "spec",
        "requirements", "contract", "policy",
    ],
    "watchtower": [
        "health", "alert", "anomaly", "uptime", "monitor", "security",
        "threat", "status", "availability", "surveillance", "risk", "incident",
        "vulnerability", "breach", "reliability", "compliance", "audit",
        "firewall", "intrusion", "access control", "data protection",
    ],
}

# Minimum keyword hits to count an agent as triggered
_MIN_SCORE = 1

# How many distinct agents must be triggered to escalate to CrewAI crew
_CREW_THRESHOLD = 2


def classify(task: str, force_agent: str | None = None) -> dict[str, Any]:
    """
    Classify a task and decide routing mode.

    Args:
        task:        Natural-language task description.
        force_agent: If provided, always routes to this specific agent (single mode).

    Returns a dict with:
        mode   – "single" or "crew"
        agent  – agent key (single mode only, else None)
        agents – list of all triggered agent keys
        scores – raw keyword hit counts per agent
        reason – human-readable explanation of the routing decision
    """
    if force_agent:
        logger.debug("Forced agent routing → '%s'", force_agent)
        return {
            "mode": "single",
            "agent": force_agent,
            "agents": [force_agent],
            "scores": {},
            "reason": "forced",
        }

    task_lower = task.lower()
    scores: dict[str, int] = {
        agent: sum(1 for kw in keywords if kw in task_lower)
        for agent, keywords in _AGENT_KEYWORDS.items()
    }

    triggered: dict[str, int] = {k: v for k, v in scores.items() if v >= _MIN_SCORE}
    logger.debug("Classification scores: %s  triggered: %s", scores, triggered)

    if not triggered:
        logger.debug("No keyword match — defaulting to FinanceAgent")
        return {
            "mode": "single",
            "agent": "finance",
            "agents": ["finance"],
            "scores": scores,
            "reason": "no_keyword_match_default_finance",
        }

    if len(triggered) >= _CREW_THRESHOLD:
        # Sort by score descending so the most relevant agent leads the crew
        agents_ordered = sorted(triggered, key=lambda k: triggered[k], reverse=True)
        logger.info("Multi-domain task → CrewAI crew  agents=%s", agents_ordered)
        return {
            "mode": "crew",
            "agent": None,
            "agents": agents_ordered,
            "scores": scores,
            "reason": "multi_domain",
        }

    best = max(triggered, key=lambda k: triggered[k])
    logger.debug("Single-domain task → '%s'", best)
    return {
        "mode": "single",
        "agent": best,
        "agents": [best],
        "scores": scores,
        "reason": "single_domain",
    }
