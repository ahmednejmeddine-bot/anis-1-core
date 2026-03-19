"""
ANIS-1 CrewAI Crew Definition — Abdeljelil Group Executive Council.

Six specialist agents run sequentially:
  1. finance_analyst        — Financial analysis, EBITDA, CAPEX, cash flow
  2. operations_manager     — OEE, downtime, maintenance, throughput, quality
  3. strategy_advisor       — Market expansion, competitive positioning, Industry 4.0
  4. document_analyst       — Document intelligence, KPI extraction, action items
  5. risk_monitor           — Operational, financial, and strategic risk surveillance
  6. executive_reviewer     — Contradiction detection + 9-section executive synthesis

The executive_reviewer reads all prior task outputs as context and produces
the final board-ready report, saved to outputs/anis1_executive_report.md.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class Anis1Core():
    """ANIS-1 Executive Council Crew for Abdeljelil Group."""

    agents: List[BaseAgent]
    tasks: List[Task]

    # ------------------------------------------------------------------
    # Agents — each loaded from config/agents.yaml
    # ------------------------------------------------------------------

    @agent
    def finance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['finance_analyst'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def operations_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['operations_manager'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def strategy_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_advisor'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def document_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['document_analyst'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def risk_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_monitor'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def executive_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['executive_reviewer'],  # type: ignore[index]
            verbose=True,
        )

    # ------------------------------------------------------------------
    # Tasks — each loaded from config/tasks.yaml
    # ------------------------------------------------------------------

    @task
    def financial_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['financial_analysis_task'],  # type: ignore[index]
        )

    @task
    def operations_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['operations_analysis_task'],  # type: ignore[index]
        )

    @task
    def strategy_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_analysis_task'],  # type: ignore[index]
        )

    @task
    def document_intelligence_task(self) -> Task:
        return Task(
            config=self.tasks_config['document_intelligence_task'],  # type: ignore[index]
        )

    @task
    def risk_monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_monitoring_task'],  # type: ignore[index]
        )

    @task
    def executive_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['executive_review_task'],  # type: ignore[index]
            output_file='outputs/anis1_executive_report.md',
        )

    # ------------------------------------------------------------------
    # Crew — sequential pipeline, reviewer always last
    # ------------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Creates the ANIS-1 Executive Council crew."""
        return Crew(
            agents=self.agents,   # populated by @agent decorators above
            tasks=self.tasks,     # populated by @task decorators above
            process=Process.sequential,
            verbose=True,
        )
