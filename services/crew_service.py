"""
CrewAI Orchestration Service for ANIS-1.

Assembles a real CrewAI crew from the triggered ANIS-1 agent domains,
runs a sequential multi-agent task, and returns a unified structured response.
"""

import os
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("anis1.crew")

# ---------------------------------------------------------------------------
# Agent role definitions for CrewAI
# ---------------------------------------------------------------------------

_AGENT_CONFIGS: dict[str, dict[str, str]] = {
    "finance": {
        "role": "Chief Financial Analyst",
        "goal": (
            "Deliver precise, data-driven financial insights, risk assessments, "
            "and budget recommendations for Abdeljelil Group."
        ),
        "backstory": (
            "You are the FinanceAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in budget analysis, revenue forecasting, expense tracking, and risk scoring. "
            "You always present numbers with clear units, flag anomalies immediately, "
            "distinguish actuals from estimates, and default to conservative assumptions."
        ),
    },
    "operations": {
        "role": "Chief Operations Officer",
        "goal": (
            "Keep every business process running at peak efficiency and minimise operational disruption "
            "for Abdeljelil Group."
        ),
        "backstory": (
            "You are the OperationsAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in process monitoring, KPI tracking, workflow optimisation, and incident response. "
            "You prioritise incident handling, classify severity rigorously (critical→high→medium→low), "
            "always include root-cause hypotheses, and propose measurable optimisation steps."
        ),
    },
    "strategy": {
        "role": "Chief Strategy Officer",
        "goal": (
            "Translate market intelligence and business objectives into a coherent, "
            "executable strategy for Abdeljelil Group."
        ),
        "backstory": (
            "You are the StrategyAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in market analysis, competitive intelligence, initiative planning, and risk evaluation. "
            "You ground every recommendation in data, state assumptions explicitly, quantify opportunity and risk, "
            "present multiple options, and consider short (0–6 months), mid (6–18), and long (18+) horizons."
        ),
    },
    "document": {
        "role": "Chief Document & Knowledge Officer",
        "goal": (
            "Transform unstructured information into clear, structured, actionable documents "
            "for Abdeljelil Group."
        ),
        "backstory": (
            "You are the DocumentAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in document summarisation, data extraction, report generation, and content analysis. "
            "You preserve original meaning faithfully, label inferences clearly, structure output for readability, "
            "and adapt document style to the intended audience."
        ),
    },
    "watchtower": {
        "role": "Chief Security & Monitoring Officer",
        "goal": (
            "Maintain 24/7 vigilance over all ANIS-1 systems and surface threats "
            "before they become incidents for Abdeljelil Group."
        ),
        "backstory": (
            "You are the WatchtowerAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in system health checks, anomaly detection, alert management, and uptime tracking. "
            "You treat every anomaly as potentially significant, alert early, correlate signals across components, "
            "and provide clear, time-stamped, severity-graded alerts with remediation steps."
        ),
    },
}


def _build_task_description(agent_key: str, agent_index: int, task: str, context: str) -> str:
    """Build a task description for a specific agent in the crew."""
    full_task = f"{task}\n\nContext: {context}" if context else task
    role = _AGENT_CONFIGS[agent_key]["role"]

    if agent_index == 0:
        return (
            f"You are the lead analyst on this task. Analyse the following from your "
            f"{role} perspective and provide a thorough, structured analysis:\n\n{full_task}"
        )
    return (
        f"Building on prior analysis from the council, contribute your unique "
        f"{role} perspective to the following task. Do not repeat what has already been said — "
        f"add new domain-specific insights and recommendations:\n\n{full_task}"
    )


def run_crew(
    task_description: str,
    agent_keys: list[str],
    context: str = "",
) -> dict[str, Any]:
    """
    Build and run a CrewAI crew for a complex, multi-domain task.

    Args:
        task_description: Natural-language task from the user.
        agent_keys:       Ordered list of ANIS-1 agent domain keys to include.
        context:          Optional background context string.

    Returns:
        Structured result dict with execution_mode, agents_used, response, etc.

    Raises:
        RuntimeError: If CrewAI is not installed.
        ValueError:   If the OpenAI API key is missing or no valid agents are found.
    """
    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError as exc:
        raise RuntimeError(f"CrewAI is not installed: {exc}") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Add it to Replit Secrets to enable CrewAI execution."
        )

    logger.info("Assembling CrewAI crew  agents=%s  task='%s'", agent_keys, task_description[:60])

    llm = LLM(model="gpt-4o", api_key=api_key, temperature=0.4)

    # -----------------------------------------------------------------------
    # Build CrewAI agents
    # -----------------------------------------------------------------------
    crew_agents: list[Any] = []
    valid_keys: list[str] = []

    for key in agent_keys:
        cfg = _AGENT_CONFIGS.get(key)
        if not cfg:
            logger.warning("Unknown agent key '%s' — skipping", key)
            continue
        crew_agents.append(
            Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                llm=llm,
                verbose=False,
                allow_delegation=False,
            )
        )
        valid_keys.append(key)

    if not crew_agents:
        raise ValueError(
            f"No valid agents found for keys: {agent_keys}. "
            f"Valid options: {list(_AGENT_CONFIGS.keys())}"
        )

    # -----------------------------------------------------------------------
    # Build Tasks — one per agent, sequential
    # -----------------------------------------------------------------------
    crew_tasks: list[Any] = []
    for i, (agent, key) in enumerate(zip(crew_agents, valid_keys)):
        desc = _build_task_description(key, i, task_description, context)
        expected = (
            f"A well-structured {_AGENT_CONFIGS[key]['role']} analysis with: "
            "clear section headings, bullet-pointed key findings, "
            "specific actionable recommendations, and any relevant risks or caveats."
        )
        crew_tasks.append(
            Task(description=desc, expected_output=expected, agent=agent)
        )

    # -----------------------------------------------------------------------
    # Assemble and run the crew
    # -----------------------------------------------------------------------
    crew = Crew(
        agents=crew_agents,
        tasks=crew_tasks,
        process=Process.sequential,
        verbose=False,
    )

    start = datetime.utcnow()
    logger.info("CrewAI kickoff started  agents=%d  tasks=%d", len(crew_agents), len(crew_tasks))

    try:
        result = crew.kickoff()
    except Exception as exc:
        logger.error("CrewAI kickoff failed: %s", exc, exc_info=True)
        raise

    elapsed = round((datetime.utcnow() - start).total_seconds(), 2)

    # Extract the final string output (CrewOutput.raw in crewai ≥ 0.30)
    raw_output: str = result.raw if hasattr(result, "raw") else str(result)

    logger.info("CrewAI crew completed  elapsed=%.1fs  output_chars=%d", elapsed, len(raw_output))

    return {
        "system": "ANIS-1",
        "execution_mode": "crew",
        "agents_used": valid_keys,
        "agent_count": len(valid_keys),
        "task": task_description,
        "context_provided": bool(context),
        "model": "gpt-4o",
        "response": raw_output,
        "execution_time_s": elapsed,
        "timestamp": datetime.utcnow().isoformat(),
    }
