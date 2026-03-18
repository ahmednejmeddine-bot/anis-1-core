"""
ANIS-1 – Autonomous Neural Intelligence System
Abdeljelil Group  ·  Command-line entry point

Usage:
    python main.py "<task description>"
    python main.py "<task description>" --agent finance
    python main.py "<task description>" --agent crew
    python main.py "<task description>" --context "extra background"

Examples:
    python main.py "build a SaaS platform for smart factories"
    python main.py "assess our Q2 budget and flag overspend risks" --agent finance
    python main.py "strategic expansion into the GCC market" --agent crew
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))


def _print_banner() -> None:
    print("\n" + "=" * 70)
    print("  ANIS-1  |  Autonomous Neural Intelligence System")
    print("  Abdeljelil Group  ·  Powered by CrewAI + GPT-4o")
    print("=" * 70 + "\n")


def _print_result(result: dict) -> None:
    mode = result.get("execution_mode", "unknown")
    agents = result.get("agents_used", [])
    elapsed = result.get("execution_time_s")
    output_path = result.get("output_path")

    print(f"\n{'─' * 70}")
    print(f"  Execution mode : {mode.upper()}")
    print(f"  Agents used    : {', '.join(agents)}")
    if elapsed:
        print(f"  Elapsed time   : {elapsed}s")
    if output_path:
        print(f"  Report saved   : {output_path}")
    print(f"{'─' * 70}\n")
    print(result.get("response", "(no response)"))
    print(f"\n{'─' * 70}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ANIS-1 – Dispatch a task to the AI agent council.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("task", nargs="?", help="Natural-language task description")
    parser.add_argument(
        "--agent",
        default=None,
        help="Force a specific agent: finance | operations | strategy | document | watchtower | crew",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Optional background context for the agent(s).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the raw JSON result instead of formatted text.",
    )

    args = parser.parse_args()

    _print_banner()

    if not args.task:
        parser.print_help()
        return 1

    task = args.task.strip()
    print(f"  Task    : {task}")
    print(f"  Agent   : {args.agent or 'auto-route'}")
    if args.context:
        print(f"  Context : {args.context[:80]}{'...' if len(args.context) > 80 else ''}")
    print()

    # ------------------------------------------------------------------
    # Import services (after path is set up)
    # ------------------------------------------------------------------
    from services import task_classifier, crew_service
    from council.ai_council import AICouncil

    council = AICouncil()

    # ------------------------------------------------------------------
    # Forced crew
    # ------------------------------------------------------------------
    if args.agent == "crew":
        agent_keys = [k for k in council.agents if k != "reviewer"]
        print(f"  [CREW]  Running full CrewAI crew  →  {agent_keys} + reviewer\n")
        try:
            result = crew_service.run_crew(
                task_description=task,
                agent_keys=agent_keys,
                context=args.context,
            )
        except Exception as exc:
            print(f"  [ERROR]  CrewAI execution failed: {exc}", file=sys.stderr)
            return 1

    # ------------------------------------------------------------------
    # Forced single agent
    # ------------------------------------------------------------------
    elif args.agent and args.agent in council.agents:
        agent = council.agents[args.agent]
        print(f"  [SINGLE AGENT]  Dispatching to {args.agent}\n")
        if not hasattr(agent, "ask"):
            print(f"  [ERROR]  Agent '{args.agent}' has no ask() method.", file=sys.stderr)
            return 1
        raw = agent.ask(task_description=task, context=args.context)
        if "error" in raw:
            print(f"  [ERROR]  {raw['error']}", file=sys.stderr)
            return 1
        result = {
            "execution_mode": "single_agent",
            "agents_used": [args.agent],
            "agent_count": 1,
            "task": task,
            "model": raw.get("model", "gpt-4o"),
            "response": raw.get("response"),
            "timestamp": raw.get("timestamp"),
        }

    # ------------------------------------------------------------------
    # Auto-route via Task Classifier
    # ------------------------------------------------------------------
    else:
        classification = task_classifier.classify(task, force_agent=args.agent)
        mode = classification["mode"]
        print(
            f"  [CLASSIFIER]  mode={mode}  agents={classification['agents']}"
            f"  reason={classification['reason']}\n"
        )

        if mode == "crew":
            try:
                result = crew_service.run_crew(
                    task_description=task,
                    agent_keys=classification["agents"],
                    context=args.context,
                )
            except Exception as exc:
                print(f"  [ERROR]  CrewAI execution failed: {exc}", file=sys.stderr)
                return 1
        else:
            agent_key = classification["agent"]
            agent = council.agents[agent_key]
            print(f"  [SINGLE AGENT]  Routing to {agent_key}\n")
            raw = agent.ask(task_description=task, context=args.context)
            if "error" in raw:
                print(f"  [ERROR]  {raw['error']}", file=sys.stderr)
                return 1
            result = {
                "execution_mode": "single_agent",
                "agents_used": [agent_key],
                "agent_count": 1,
                "task": task,
                "model": raw.get("model", "gpt-4o"),
                "response": raw.get("response"),
                "timestamp": raw.get("timestamp"),
                "classification": classification,
            }

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_result(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
