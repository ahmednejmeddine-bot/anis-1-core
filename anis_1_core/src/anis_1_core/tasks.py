"""
tasks.py — ANIS-1 Task definitions for Abdeljelil Group.

This module documents the six sequential tasks that form the ANIS-1
Executive Council pipeline. The primary instantiation path is YAML-driven
via config/tasks.yaml + the @task decorators in crew.py.

These factory functions provide a programmatic alternative for testing,
custom pipelines, or standalone use outside the @CrewBase pattern.

Task execution order (sequential):
  1. financial_analysis_task
  2. operations_analysis_task
  3. strategy_analysis_task
  4. document_intelligence_task
  5. risk_monitoring_task
  6. executive_review_task  ← reads all prior outputs as context
"""

from crewai import Agent, Task


def financial_analysis_task(agent: Agent, task_input: str) -> Task:
    """
    Financial analysis task.
    Output: structured markdown report with EBITDA, CAPEX, working capital,
    cash flow, liquidity, cost structure, FX risk, and top-3 financial risks.
    """
    return Task(
        description=(
            f"Conduct a comprehensive financial analysis for Abdeljelil Group on: "
            f"{task_input}\n\n"
            "Cover: EBITDA margin, CAPEX/ROI/payback, working capital position, "
            "cash flow adequacy, liquidity ratios (DSCR, covenant headroom), "
            "cost structure (energy per ton, labour per unit), FX exposure, "
            "and top 3 financial risks with magnitude estimates. "
            "Label all figures as actual, estimate, or forecast with clear units."
        ),
        expected_output=(
            "A structured financial analysis report: Executive Finding | "
            "KPI table (metric/actual/target/status) | Top 3 risks with magnitude "
            "and recommended action | Actions with owner and timeline. "
            "Formatted as clean markdown."
        ),
        agent=agent,
    )


def operations_analysis_task(agent: Agent, task_input: str) -> Task:
    """
    Operations analysis task.
    Output: OEE scorecard, top-3 downtime causes, maintenance recommendation,
    quality losses, supply chain bottleneck, prioritised action plan.
    """
    return Task(
        description=(
            f"Analyse the operational performance of Abdeljelil Group's "
            f"manufacturing and packaging/converting facilities for: {task_input}\n\n"
            "Cover: OEE (Availability × Performance × Quality) vs. 85% target, "
            "top-3 unplanned downtime causes (MTBF/MTTR), maintenance maturity "
            "and upgrade recommendation, system constraint (Theory of Constraints), "
            "quality losses (scrap rate, FPY, COPQ), top supply chain bottleneck, "
            "changeover time (SMED opportunity), and any safety concerns."
        ),
        expected_output=(
            "A structured operations report: OEE scorecard | Top 3 downtime causes "
            "with cost per hour | Maintenance recommendation with payback | "
            "Prioritised action plan (action/owner/deadline/OEE impact). "
            "Formatted as clean markdown."
        ),
        agent=agent,
    )


def strategy_analysis_task(agent: Agent, task_input: str) -> Task:
    """
    Strategy analysis task.
    Output: 2-3 strategic options with financials, recommended path,
    success metrics, and key risks with mitigations.
    """
    return Task(
        description=(
            f"Develop a strategic analysis and recommendations for Abdeljelil "
            f"Group on: {task_input}\n\n"
            "Address: top-2 market expansion opportunities (MENA/Africa) ranked by "
            "attractiveness × strategic fit, competitive positioning (pricing power "
            "vs. commoditisation segments), investment comparison (capacity expansion "
            "vs. automation vs. new product lines using IRR/NPV/payback), Industry 4.0 "
            "roadmap (top-3 investments sequenced by dependency and ROI), and one "
            "vertical integration or M&A opportunity with synergy quantification. "
            "Present 2-3 options before recommending. Specify time horizons."
        ),
        expected_output=(
            "A strategic report: Context and assumptions | 2-3 options table "
            "(option/investment/IRR/payback/key risk) | Recommended path with "
            "rationale | Success metrics | Key risks with mitigations. "
            "Formatted as clean markdown."
        ),
        agent=agent,
    )


def document_intelligence_task(agent: Agent, task_input: str) -> Task:
    """
    Document intelligence task.
    Output: document classification, executive summary, KPI/data table,
    action items, decisions required, information gaps.
    """
    return Task(
        description=(
            f"Process and extract key intelligence from all information gathered "
            f"for: {task_input}\n\n"
            "Perform: document/information type classification, executive summary "
            "(≤5 sentences), extract all KPIs and quantitative data into a structured "
            "table, identify all action items with suggested owners and urgency, "
            "classify decisions required (strategic/operational/financial), "
            "and flag information gaps requiring further investigation."
        ),
        expected_output=(
            "A structured intelligence brief: Document type | Executive summary "
            "(≤5 sentences) | KPI table (metric/value/unit/source) | Action items "
            "(action/owner/urgency) | Decisions required | Information gaps. "
            "Formatted as clean markdown."
        ),
        agent=agent,
    )


def risk_monitoring_task(agent: Agent, task_input: str) -> Task:
    """
    Risk monitoring task.
    Output: severity-graded alert table across all four risk dimensions,
    top-3 correlated risk clusters, leading indicators, immediate actions.
    """
    return Task(
        description=(
            f"Conduct a full risk surveillance sweep for Abdeljelil Group "
            f"covering: {task_input}\n\n"
            "Assess all four dimensions: (1) Operational — OEE anomalies, machine "
            "failure signals, safety near-misses, overdue maintenance; "
            "(2) Financial — receivables ageing, EBITDA compression, raw material "
            "price spikes, cash shortfalls, covenant proximity; "
            "(3) Weak signals — supplier distress, energy price trends, logistics "
            "disruptions, key personnel attrition; "
            "(4) Strategic threats — competitor expansions, technology disruption, "
            "regulatory changes, customer concentration. "
            "For each risk: SEVERITY | Signal | Impact | Response | Escalation path. "
            "Correlate signals across dimensions to identify compounding clusters."
        ),
        expected_output=(
            "A risk surveillance report: Alert table "
            "(SEVERITY/Signal/Dimension/Impact/Response/Escalation) | "
            "Top 3 correlated risk clusters | Leading indicators with monitoring "
            "cadence | Immediate actions (CRITICAL and HIGH only). "
            "Formatted as clean markdown."
        ),
        agent=agent,
    )


def executive_review_task(
    agent: Agent,
    task_input: str,
    context: list[Task],
    output_file: str = "outputs/anis1_executive_report.md",
) -> Task:
    """
    Executive review task — always the final task in the pipeline.
    Reads all prior task outputs as context. Produces the 9-section
    board-ready executive report and saves it to output_file.
    """
    return Task(
        description=(
            f"Review ALL specialist agent outputs for: {task_input}\n\n"
            "Perform three duties: "
            "(1) CONTRADICTION DETECTION — identify and resolve every conflicting "
            "figure, assumption, or recommendation across agents; "
            "(2) CLARITY IMPROVEMENT — rewrite any ambiguous, repetitive, or "
            "non-actionable sections; "
            "(3) EXECUTIVE SYNTHESIS — assemble the final 9-section board-ready "
            "report using only the specialist agents' outputs. "
            "Prioritise recommendations by urgency and financial impact."
        ),
        expected_output=(
            "A complete 9-section executive report in clean markdown:\n"
            "## 1. Executive Summary\n"
            "## 2. Financial Analysis\n"
            "## 3. Operations Assessment\n"
            "## 4. Strategic Recommendations\n"
            "## 5. Document and Knowledge Assessment\n"
            "## 6. Risk and Monitoring Status\n"
            "## 7. Cross-Agent Synthesis and Contradiction Resolution\n"
            "## 8. Risk Summary\n"
            "## 9. Final Recommendations and Next Steps\n"
            "   (Action | Owner | Timeline | Success Metric)\n"
            "Board-ready, actionable, no generic filler."
        ),
        agent=agent,
        context=context,
        output_file=output_file,
    )
