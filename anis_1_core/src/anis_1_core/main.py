#!/usr/bin/env python
"""
ANIS-1 Entry Points — Abdeljelil Group Executive Council.

Usage:
  crewai run                              # run with default task
  crewai train <n_iterations> <filename> # train the crew
  crewai replay <task_id>                # replay from a specific task
  crewai test <n_iterations> <eval_llm>  # test and evaluate
"""
import sys
import warnings

from anis_1_core.crew import Anis1Core

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

_DEFAULT_TASK = (
    "Prepare a 12-month executive roadmap for Abdeljelil Group to improve "
    "industrial performance, financial control, strategic expansion, and "
    "risk monitoring across all manufacturing and packaging/converting operations."
)


def run():
    """Run the ANIS-1 crew with the default executive roadmap task."""
    inputs = {
        "task_input": _DEFAULT_TASK,
    }
    try:
        Anis1Core().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """Train the crew for a given number of iterations."""
    inputs = {"task_input": _DEFAULT_TASK}
    try:
        Anis1Core().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task ID."""
    try:
        Anis1Core().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return evaluation results."""
    inputs = {"task_input": _DEFAULT_TASK}
    try:
        Anis1Core().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with a JSON trigger payload from CrewAI Enterprise.

    The trigger payload is passed as the first CLI argument (JSON string).
    The 'task_input' key is extracted from the payload; if absent, the
    entire payload is serialised and used as the task description.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Pass a JSON string as the first argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument.")

    task_input = trigger_payload.get("task_input") or json.dumps(trigger_payload)

    inputs = {
        "task_input": task_input,
        "crewai_trigger_payload": trigger_payload,
    }

    try:
        result = Anis1Core().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
