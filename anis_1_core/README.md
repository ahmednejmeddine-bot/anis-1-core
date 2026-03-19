# ANIS-1 — Autonomous Neural Intelligence System
### Abdeljelil Group Executive Council · Powered by CrewAI + GPT-4o

---

## What This Is

ANIS-1 is a six-agent CrewAI executive council that delivers board-level
analysis across finance, operations, strategy, document intelligence,
risk monitoring, and executive synthesis for Abdeljelil Group's industrial
manufacturing and packaging/converting operations.

### Six Specialist Agents

| Agent | Role | Domain |
|---|---|---|
| `finance_analyst` | Chief Financial Analyst | EBITDA, CAPEX, cash flow, working capital, FX risk |
| `operations_manager` | Chief Operations Officer | OEE, downtime, maintenance, throughput, quality |
| `strategy_advisor` | Chief Strategy Officer | Market expansion, Industry 4.0, investment prioritisation |
| `document_analyst` | Chief Document Officer | Intelligence extraction, KPI tables, action items |
| `risk_monitor` | Chief Risk Officer | Operational, financial, and strategic risk surveillance |
| `executive_reviewer` | Board-Level Reviewer | Contradiction detection + 9-section executive synthesis |

The crew runs **sequentially**. The `executive_reviewer` always runs last,
reading all prior outputs as context, and produces a 9-section executive
report saved to `outputs/anis1_executive_report.md`.

---

## Prerequisites

- Python 3.10–3.13
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key with GPT-4o access

---

## Installation

```bash
# From inside the anis_1_core/ directory:
pip install uv          # if uv not installed

crewai install          # installs deps + generates uv.lock
```

Or manually:
```bash
cd anis_1_core
uv sync
```

---

## Configuration

Set your OpenAI API key in `anis_1_core/.env`:

```
OPENAI_API_KEY=sk-...
```

---

## Running the Crew

### Default run (12-month executive roadmap task):
```bash
cd anis_1_core
crewai run
```

### Custom task via trigger payload:
```bash
cd anis_1_core
python -c "
from anis_1_core.main import run_with_trigger
import sys
sys.argv = ['main', '{\"task_input\": \"Analyse Q3 financial performance\"}']
run_with_trigger()
"
```

### Output
The final 9-section executive report is saved to:
```
outputs/anis1_executive_report.md
```

---

## Project Structure

```
anis_1_core/
├── pyproject.toml                         # CrewAI deployment manifest
├── .env                                   # OPENAI_API_KEY (not committed)
├── outputs/                               # Generated executive reports
└── src/
    └── anis_1_core/
        ├── __init__.py                    # Package declaration
        ├── crew.py                        # @CrewBase class — 6 agents, 6 tasks
        ├── agents.py                      # Programmatic agent factory functions
        ├── tasks.py                       # Programmatic task factory functions
        ├── main.py                        # Entry points: run/train/replay/test
        └── config/
            ├── agents.yaml               # Agent role/goal/backstory definitions
            └── tasks.yaml                # Task descriptions and expected outputs
```

---

## Deploying to CrewAI Enterprise

1. Generate the lock file:
```bash
cd anis_1_core
crewai install
```

2. Commit everything including `uv.lock`:
```bash
git add anis_1_core/
git commit -m "feat: ANIS-1 CrewAI deployment structure for Abdeljelil Group"
git push origin main
```

3. In CrewAI Studio: connect the repository, set `OPENAI_API_KEY` as a secret,
   and deploy. The entry point is `anis_1_core.main:run_with_trigger`.

---

## Support

- CrewAI docs: https://docs.crewai.com
- CrewAI Enterprise: https://app.crewai.com
