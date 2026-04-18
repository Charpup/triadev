# TriaDev v3.1 — Golden Triangle Orchestrator

Lightweight orchestration skill for structured multi-step projects.
Routes work through the right skill stack and maintains a shared handoff contract.

## What It Does

TriaDev coordinates a triangle of skills into a coherent workflow:

```
planning-with-files → task-workflow → [value-first-gate] → [tdd-sdd-development]
       (plan)           (schedule)         (assess)              (implement)
```

**Two paths:**
- **Core** (non-coding): planning + scheduling for research, analysis, documentation
- **Extended** (coding): adds value gate + TDD/SDD for implementation work

State is coordinated via `triadev-handoff.json` — the inter-skill contract. Each skill reads and writes only its own section.

## Installation

```bash
# Claude Code
claude skill add Charpup/triadev

# Manual
git clone https://github.com/Charpup/triadev.git ~/.claude/skills/triadev
```

## Dependencies

- [planning-with-files](https://github.com/OthmanAdi/planning-with-files) ≥ 2.10 (required)
- [task-workflow](https://github.com/Charpup/openclaw-task-workflow) ≥ 3.0 (required)
- [value-first-gate](https://github.com/Charpup/value-first-gate) ≥ 2.0 (Extended path)
- [tdd-sdd-development](https://github.com/Charpup/openclaw-tdd-sdd-skill) ≥ 3.0 (Extended path)

## How It Works

1. **Route**: Classifies intent as Core (non-coding) or Extended (coding). Announced explicitly.
2. **Plan**: Delegates to planning-with-files for `task_plan.md` / `findings.md` / `progress.md`.
3. **Schedule**: Delegates to task-workflow for DAG-based batch ordering.
4. **Gate** (Extended): Runs value-first-gate; requires `verdict=GO` AND no rubber-stamp flag.
5. **Implement** (Extended): Runs TDD/SDD cycles per task-workflow batches.
6. **Complete**: Updates all files, archives changes.

## Project Structure

```
triadev/
├── SKILL.md                                     # Main workflow
├── README.md                                    # This file
├── contracts/
│   └── triadev-handoff.schema.json              # JSON Schema — machine validation
├── templates/
│   └── triadev-handoff.json                     # Empty-instance starting template
├── references/
│   ├── handoff-contract.md                      # Human-readable schema + ownership rules
│   ├── routing-rules.md                         # Core vs Extended decision tree
│   └── phase-transitions.md                     # Legal transitions + drift canonicals
├── examples/
│   └── d-to-x-migration-partial/                # BRONZE — real Core-path mid-flow
└── evals/
    └── evals.json                               # 8 cases (smoke × 3, recovery, lifecycle, schema, negative)
```

## The Handoff Contract — Four Layers

Understanding these four files is the whole skill:

| File | Role | When to load |
|------|------|--------------|
| `contracts/triadev-handoff.schema.json` | Machine-readable JSON Schema | Before writing handoff.json — validate after each write |
| `templates/triadev-handoff.json` | Empty-instance starting template | At project init — copy as starting point |
| `references/handoff-contract.md` | Human-readable schema + ownership rules | When authoring or reviewing handoff logic |
| `references/phase-transitions.md` | Legal transitions + canonical field values | **Always before advancing `current_phase`** (drift-prevention) |

## Usage Examples

**Core path** (research / analysis):
> "Research 3 API gateway solutions, compare pricing and plugin ecosystems, recommend one."

**Extended path** (coding):
> "Build a rate-limiter module: 100 req/min/user, Redis-backed, sliding window. Production-ready with tests."

**Session recovery**:
> Existing `task_plan.md` is detected on start; triadev constructs or resumes `triadev-handoff.json` from current state rather than starting over.

## Boundary Rules

| File | Owner | Others may... |
|------|-------|--------------|
| `task_plan.md` | planning-with-files | Read (task-workflow extracts tasks) |
| `findings.md` | planning-with-files | Read only |
| `progress.md` | planning-with-files | Append session entries |
| `triadev-handoff.json` | triadev (coordinator) | Read/write own section only |
| `value-review.json` | value-first-gate | triadev reads for verdict→status mapping |
| `SPEC.yaml` | tdd-sdd-development | Read only (triadev, task-workflow) |
| `.tdd-state.json` | tdd-sdd-development | Not accessed by others |

## Working Example

See [`examples/d-to-x-migration-partial/`](examples/d-to-x-migration-partial/) for a real Core-path run (D:\ → X:\ workspace migration, April 2026). Labeled **BRONZE** because:

- ✅ Real planning trio (not constructed)
- ✅ Real mid-flow state (`current_phase: scheduling`, Stage A complete, Stages B-D pending)
- ⚠️ Handoff was retrofitted — triadev was not actually orchestrating this run
- ⚠️ Project paused mid-flow; no completion transition demonstrated

For a completed Extended-path reference (GOLD), see the `tdd-sdd-development` skill's `examples/pdf-ocr-skill/`.

## Changelog

### v3.1.0 (2026-04-18)
Round-2 standardization pass. Additive; no breaking changes.

- **New**: `contracts/triadev-handoff.schema.json` — JSON Schema for programmatic validation. Separates contract (machine) from template (empty instance).
- **New**: `references/phase-transitions.md` — legal/illegal transitions + canonical field values (prevents drift like `done` vs `complete`, `in-progress` vs `in_progress`).
- **New**: `examples/d-to-x-migration-partial/` — BRONZE real Core-path mid-flow snapshot. 5 files: README (BRONZE labeling) + task_plan/findings/progress verbatim + reconstructed handoff.json.
- **Hardened**: `evals/evals.json` — 4 → 8 cases, new coverage (handoff lifecycle, /clear recovery, illegal-phase detection, JSON schema validation). Assertion mix shifted to ~75% deterministic (file_exists, json_path_equals, json_schema_valid) vs `llm_judge`.
- **Rewritten**: SKILL.md Handoff Contract section — 4-file semantic table distinguishing contracts / templates / references / phase-transitions and when to load each. Working Examples section added.

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
