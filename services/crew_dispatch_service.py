"""
Crew Dispatch Service for ANIS-1.

Centralises the classification-to-routing decision and produces the
structured dispatch response skeleton (classified_domain, execution_mode,
status, message) that the API layer merges with AI execution results.
"""

import logging
from datetime import datetime
from typing import Any

from services import task_classifier

logger = logging.getLogger("anis1.dispatch")

# ---------------------------------------------------------------------------
# Domain display names (used in human-readable messages)
# ---------------------------------------------------------------------------

_DOMAIN_NAMES: dict[str, str] = {
    "finance":    "Finance",
    "operations": "Operations",
    "strategy":   "Strategy",
    "document":   "Document & Knowledge",
    "watchtower": "Watchtower",
}


def classify_and_route(
    task: str,
    context: str = "",
    force_agent: str | None = None,
) -> dict[str, Any]:
    """
    Classify a task and produce the dispatch decision record.

    Args:
        task:        Natural-language task string.
        context:     Optional background context (not used in classification,
                     included in the response for traceability).
        force_agent: If set, classification is bypassed and this agent key
                     is used directly.

    Returns a dict with:
        task             – the original task string
        classified_domain – primary domain name ("finance", "operations", …,
                           or "multi_domain" when crew is triggered)
        execution_mode   – "single_agent" | "crew"
        status           – always "dispatched" at this stage
        message          – human-readable routing summary
        classification   – raw classifier output (scores, reason, agents)
        timestamp        – ISO-8601 UTC dispatch timestamp
    """
    classification = task_classifier.classify(task, force_agent=force_agent)
    mode       = classification["mode"]
    agents     = classification["agents"]
    reason     = classification.get("reason", "")

    if mode == "crew":
        classified_domain = "multi_domain"
        execution_mode    = "crew"
        domain_list       = ", ".join(
            _DOMAIN_NAMES.get(a, a.title()) for a in agents
        )
        message = (
            f"Task spans {len(agents)} domain(s) ({domain_list}) — "
            f"escalated to CrewAI multi-agent crew with ReviewerAgent synthesis."
        )
    else:
        agent_key         = classification.get("agent") or (agents[0] if agents else "finance")
        classified_domain = agent_key
        execution_mode    = "single_agent"
        display_name      = _DOMAIN_NAMES.get(agent_key, agent_key.title())
        message = (
            f"Task classified as '{classified_domain}' domain"
            + (f" (reason: {reason})" if reason and reason not in {"forced", "single_domain"} else "")
            + f" — routed to {display_name}Agent for execution."
        )

    logger.info(
        "Dispatch decision  mode=%s  classified_domain=%s  agents=%s  reason=%s",
        execution_mode, classified_domain, agents, reason,
    )

    return {
        "task":             task,
        "classified_domain": classified_domain,
        "execution_mode":   execution_mode,
        "status":           "dispatched",
        "message":          message,
        "classification":   classification,
        "timestamp":        datetime.utcnow().isoformat(),
    }
