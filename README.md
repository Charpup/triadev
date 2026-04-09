# TriaDev v3.0 — Golden Triangle Orchestrator

Lightweight orchestration skill for structured multi-step projects.
Routes work through the right skill stack and maintains a shared handoff contract.

## What It Does

TriaDev coordinates three skills into a coherent workflow:

```
planning-with-files → task-workflow → [value-gate] → [tdd-sdd]
       (plan)           (schedule)      (assess)      (implement)
```

**Two paths:**
- **Core** (non-coding): planning + scheduling for research, analysis, documentation
- **Extended** (coding): adds value gate + TDD/SDD for implementation work

## Installation

```bash
# Claude Code
claude skill add Charpup/triadev

# Manual
git clone https://github.com/Charpup/triadev.git ~/.claude/skills/triadev
```

## Dependencies

Install these skills first:
- [planning-with-files](https://github.com/OthmanAdi/planning-with-files) (required)
- [task-workflow](https://github.com/Charpup/openclaw-task-workflow) (required)
- [tdd-sdd-development](https://github.com/Charpup/openclaw-tdd-sdd-skill) (Extended path)
- [value-first-gate](https://github.com/Charpup/value-first-gate) (Extended path)

## How It Works

1. **Route**: Classifies intent as Core (non-coding) or Extended (coding)
2. **Plan**: Delegates to planning-with-files for task_plan.md / findings.md / progress.md
3. **Schedule**: Delegates to task-workflow for DAG-based batch ordering
4. **Gate** (Extended): Runs value-first-gate; requires GO verdict
5. **Implement** (Extended): Runs TDD/SDD cycles per task-workflow batches
6. **Complete**: Updates all files, archives changes

State is coordinated via `triadev-handoff.json` — the inter-skill contract.

## Project Structure

```
triadev/
├── SKILL.md                     # Orchestration instructions
├── references/
│   ├── handoff-contract.md      # triadev-handoff.json schema
│   └── routing-rules.md         # Core vs Extended decision tree
├── templates/
│   └── triadev-handoff.json     # Handoff file template
└── evals/
    └── evals.json               # Evaluation test cases
```

## Changelog

### v3.0.0 (2026-04-09)
- **Breaking**: Removed Python runtime (orchestrator.py, cli.py, install.sh)
- **New**: Pure prompt-based orchestration via SKILL.md
- **New**: `triadev-handoff.json` inter-skill contract
- **New**: Explicit route announcement (Core vs Extended)
- **New**: Session recovery from existing handoff state
- **Changed**: Dependencies are consumed as installed skills, not imported Python modules

### v2.1.0
- Added brownfield support, delta specs, artifact flow
- Hybrid A-first routing

## License

MIT
