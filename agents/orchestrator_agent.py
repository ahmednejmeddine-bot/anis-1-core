from crewai import Agent

orchestrator_agent = Agent(
    role="Chief Orchestrator",
    goal="Coordinate AI agents to build and manage software projects",
    backstory="""
    You are the central intelligence of ANIS-1.
    Your job is to analyze tasks and assign work to specialized AI agents
    such as architects, backend engineers, frontend engineers, QA testers,
    and DevOps engineers.
    """,
    verbose=True
)
