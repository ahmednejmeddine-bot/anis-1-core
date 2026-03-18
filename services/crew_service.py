"""
CrewAI Orchestration Service for ANIS-1.

Assembles a real CrewAI crew from the triggered ANIS-1 agent domains,
appends a ReviewerAgent as the final synthesis layer, runs the crew
sequentially, and returns a unified structured response.

The ReviewerAgent always participates — it reads all prior outputs and
produces the 9-section executive report saved to outputs/.
"""

import os
import logging
from datetime import datetime
from typing import Any

from agents.reviewer_agent import CREWAI_CONFIG as REVIEWER_CONFIG

logger = logging.getLogger("anis1.crew")

# ---------------------------------------------------------------------------
# Specialist agent CrewAI definitions
# ---------------------------------------------------------------------------

_SPECIALIST_CONFIGS: dict[str, dict[str, str]] = {
    "finance": {
        "role": "Chief Financial Analyst",
        "goal": (
            "Deliver precise, data-driven financial insights, risk assessments, "
            "and budget recommendations for Abdeljelil Group."
        ),
        "backstory": (
            "You are the FinanceAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in budget analysis, revenue forecasting, expense tracking, and risk scoring. "
            "Always present numbers with clear units, flag anomalies immediately, "
            "distinguish actuals from estimates, and default to conservative assumptions."
        ),
    },
    "operations": {
        "role": "Chief Operations Officer",
        "goal": (
            "Keep every business process running at peak efficiency and minimise operational "
            "disruption for Abdeljelil Group."
        ),
        "backstory": (
            "You are the OperationsAgent for Abdeljelil Group within the ANIS-1 system. "
            "You specialise in process monitoring, KPI tracking, workflow optimisation, and incident response. "
            "Prioritise incident handling, classify severity rigorously (critical→high→medium→low), "
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
            "Ground every recommendation in data, state assumptions explicitly, quantify opportunity and risk, "
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
            "Preserve original meaning faithfully, label inferences clearly, structure output for readability, "
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
            "Treat every anomaly as potentially significant, alert early, correlate signals, "
            "and provide severity-graded alerts with clear remediation steps."
        ),
    },
}

# Report section headings used by the ReviewerAgent
REPORT_SECTIONS = [
    "Executive Summary",
    "Financial Analysis",
    "Operations Assessment",
    "Strategic Recommendations",
    "Document & Knowledge Assessment",
    "Security & Monitoring Status",
    "Cross-Agent Synthesis & Contradiction Resolution",
    "Risk Summary",
    "Final Recommendations & Next Steps",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _specialist_task_description(agent_key: str, index: int, task: str, context: str) -> str:
    full_task = f"{task}\n\nAdditional context: {context}" if context else task
    role = _SPECIALIST_CONFIGS[agent_key]["role"]
    if index == 0:
        return (
            f"You are the lead analyst on this request. Analyse the following "
            f"from your {role} perspective and provide a thorough, structured analysis:\n\n{full_task}"
        )
    return (
        f"Building on the analyses already contributed by the council, add your "
        f"unique {role} perspective to this request. Do not repeat prior analysis — "
        f"focus on domain-specific insights and concrete recommendations:\n\n{full_task}"
    )


def _reviewer_task_description(task: str, agent_keys: list[str]) -> str:
    agents_str = ", ".join(agent_keys)
    sections = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(REPORT_SECTIONS))
    return (
        f"You have received analyses from the following ANIS-1 specialist agents: {agents_str}.\n\n"
        f"Original task: {task}\n\n"
        f"Your duties:\n"
        f"  1. Identify any contradictions, inconsistencies, or gaps between the agent analyses.\n"
        f"  2. Resolve or flag each contradiction clearly.\n"
        f"  3. Improve any sections that are vague, repetitive, or non-actionable.\n"
        f"  4. Assemble a final, leadership-ready executive report using exactly these 9 sections:\n"
        f"{sections}\n\n"
        f"Be decisive. Prioritise recommendations by urgency and impact. "
        f"Cite which agent contributed each key finding."
    )


def _save_report(task: str, content: str, agent_keys: list[str]) -> str:
    """Save the executive report to outputs/ and return the file path."""
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = "".join(c if c.isalnum() or c in "-_ " else "" for c in task[:40]).strip().replace(" ", "_")
    filename = f"outputs/anis1_report_{safe_task}_{timestamp}.md"

    agents_str = " | ".join(a.upper() for a in agent_keys)
    header = (
        f"# ANIS-1 Executive Report\n\n"
        f"**Task:** {task}\n\n"
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"**Agents:** {agents_str} | REVIEWER\n\n"
        f"**Model:** GPT-4o  |  **System:** ANIS-1 v2.0 – Abdeljelil Group\n\n"
        f"---\n\n"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + content)

    logger.info("Report saved → %s", filename)
    return filename


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def run_crew(
    task_description: str,
    agent_keys: list[str],
    context: str = "",
) -> dict[str, Any]:
    """
    Build and run a CrewAI crew for a complex, multi-domain task.

    Workflow:
      1. One Task per specialist agent (sequential, each builds on prior).
      2. Final ReviewerAgent Task: synthesises all prior output into the
         9-section executive report and saves it to outputs/.

    Args:
        task_description: Natural-language task.
        agent_keys:       Ordered specialist agent keys to include.
        context:          Optional background context.

    Returns:
        Structured result dict (execution_mode, agents_used, response, output_path, …).
    """
    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError as exc:
        raise RuntimeError(f"CrewAI is not installed: {exc}") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Add it to Replit Secrets to enable CrewAI."
        )

    logger.info(
        "Assembling crew  specialists=%s  task='%s'", agent_keys, task_description[:60]
    )

    llm = LLM(model="gpt-4o", api_key=api_key, temperature=0.4)

    # -----------------------------------------------------------------------
    # 1. Build specialist agents
    # -----------------------------------------------------------------------
    crew_agents: list[Any] = []
    valid_keys: list[str] = []

    for key in agent_keys:
        cfg = _SPECIALIST_CONFIGS.get(key)
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
            f"No valid agent keys found in: {agent_keys}. "
            f"Valid options: {list(_SPECIALIST_CONFIGS.keys())}"
        )

    # -----------------------------------------------------------------------
    # 2. Build ReviewerAgent (always added as the final council member)
    # -----------------------------------------------------------------------
    reviewer = Agent(
        role=REVIEWER_CONFIG["role"],
        goal=REVIEWER_CONFIG["goal"],
        backstory=REVIEWER_CONFIG["backstory"],
        llm=llm,
        verbose=True,          # Reviewer logs its reasoning prominently
        allow_delegation=False,
    )

    # -----------------------------------------------------------------------
    # 3. Build Tasks — one per specialist, then the reviewer synthesis task
    # -----------------------------------------------------------------------
    crew_tasks: list[Any] = []

    for i, (agent, key) in enumerate(zip(crew_agents, valid_keys)):
        desc = _specialist_task_description(key, i, task_description, context)
        expected = (
            f"A structured {_SPECIALIST_CONFIGS[key]['role']} analysis with: "
            "clear section headings, bullet-pointed key findings, "
            "specific actionable recommendations, and identified risks."
        )
        crew_tasks.append(Task(description=desc, expected_output=expected, agent=agent))

    reviewer_task = Task(
        description=_reviewer_task_description(task_description, valid_keys),
        expected_output=(
            "A complete 9-section executive report ready for Abdeljelil Group leadership. "
            "Each section must be clearly headed, free of contradictions, and contain "
            "specific, actionable recommendations ordered by priority."
        ),
        agent=reviewer,
    )
    crew_tasks.append(reviewer_task)

    # -----------------------------------------------------------------------
    # 4. Assemble and run the crew
    # -----------------------------------------------------------------------
    crew = Crew(
        agents=[*crew_agents, reviewer],
        tasks=crew_tasks,
        process=Process.sequential,
        verbose=False,
    )

    start = datetime.utcnow()
    logger.info(
        "CrewAI kickoff  agents=%d  tasks=%d (incl. reviewer)",
        len(crew_agents) + 1, len(crew_tasks),
    )

    try:
        result = crew.kickoff()
    except Exception as exc:
        logger.error("CrewAI kickoff failed: %s", exc, exc_info=True)
        raise

    elapsed = round((datetime.utcnow() - start).total_seconds(), 2)
    raw_output: str = result.raw if hasattr(result, "raw") else str(result)

    logger.info(
        "Crew completed  elapsed=%.1fs  output_chars=%d", elapsed, len(raw_output)
    )

    # -----------------------------------------------------------------------
    # 5. Save report to outputs/
    # -----------------------------------------------------------------------
    all_agents = valid_keys + ["reviewer"]
    output_path = _save_report(task_description, raw_output, all_agents)

    return {
        "system": "ANIS-1",
        "execution_mode": "crew",
        "agents_used": all_agents,
        "specialist_agents": valid_keys,
        "reviewer_included": True,
        "agent_count": len(all_agents),
        "task": task_description,
        "context_provided": bool(context),
        "model": "gpt-4o",
        "response": raw_output,
        "execution_time_s": elapsed,
        "output_path": output_path,
        "report_sections": REPORT_SECTIONS,
        "timestamp": datetime.utcnow().isoformat(),
    }
