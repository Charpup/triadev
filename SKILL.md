---
name: triadev
description: >-
  TRIGGER: triadev, Golden Triangle, structured development, multi-step project,
  brownfield workflow, delta spec, greenfield project.
  TriaDev v3.0 orchestrates structured multi-step projects through two paths:
  Core (planning + scheduling) for non-coding work, Extended (+ value-gate + TDD/SDD)
  for implementation. Creates triadev-handoff.json to coordinate between
  planning-with-files, task-workflow, and tdd-sdd-development.
  Use for projects with 5+ tasks or cross-session work. NOT for single edits or quick fixes.
---

# TriaDev v3.0 — Golden Triangle Orchestrator

Coordinate structured multi-step projects by routing through the right skill stack
and maintaining a shared handoff contract between skills.

## Dependencies

| Skill | Role | Required? |
|-------|------|-----------|
| planning-with-files | Persistent planning (task_plan.md, findings.md, progress.md) | Yes (Core + Extended) |
| task-workflow | DAG scheduling, complexity scoring, batch ordering | Yes (Core + Extended) |
| value-first-gate | GO/REVISE/NO-GO value assessment before implementation | Extended only |
| tdd-sdd-development | TDD+SDD with SPEC.yaml and RED-GREEN-REFACTOR | Extended only |

## Route Decision (First Step — Always Do This)

Classify the user's intent before doing anything else:

```
Is there coding intent?
(implementation, refactoring, tests, SPEC changes, new features)

  YES → Extended Path
  NO  → Core Path (default)
```

**Announce the route explicitly:**
```
Route: Core — no implementation intent detected.
Route: Extended — coding intent detected (building a rate limiter module).
```

### Core Path (Non-Coding)
For planning, research, orchestration, analysis, documentation.

```
Planning → Scheduling → Execute (research/analysis/writing) → Complete
```

Skills used: planning-with-files + task-workflow

### Extended Path (Coding)
For implementation, refactoring, testing, spec-driven development.

```
Planning → Scheduling → Value Gate → TDD/SDD Cycles → Complete
```

Skills used: planning-with-files + task-workflow + value-first-gate + tdd-sdd-development

**Gate rule:** Before entering TDD/SDD, value-first-gate must return `GO`.
- `GO` → proceed to implementation
- `REVISE` → return to planning, adjust scope
- `NO-GO` → stop, explain why to user

## Session Recovery

**Before starting any work**, check for existing state:

1. If `triadev-handoff.json` exists → read it, resume from `current_phase`
2. If `task_plan.md` exists but no handoff.json → planning-with-files was used standalone; create handoff.json from plan state
3. If neither exists → fresh start

## Phase 1: Planning

Delegate to **planning-with-files**:

1. Create `task_plan.md` with phases and objectives (checkbox format)
2. Create `findings.md` for research discoveries
3. Create `progress.md` for session logging
4. Follow planning-with-files rules (2-Action Rule, Read Before Decide, etc.)

**After planning is complete**, extract tasks from task_plan.md:

Parse checkbox items that represent actionable work units. For each, assign:
- `id`: kebab-case identifier (e.g., `research-api-gateways`)
- `name`: human-readable name
- `complexity`: 1-10 score (1-3 simple, 4-6 moderate, 7-10 complex)
- `dependencies`: list of task IDs this depends on

Write the extracted tasks into `triadev-handoff.json` → `planning.tasks_extracted`.

## Phase 2: Scheduling

Delegate to **task-workflow**:

1. Read `triadev-handoff.json` → `planning.tasks_extracted`
2. Build DAG from task dependencies
3. Sort by topological order, then by complexity (lower first)
4. Group into execution batches (independent tasks in same batch)
5. Write batch schedule to `triadev-handoff.json` → `scheduling.batches`

## Phase 3: Value Gate (Extended Path Only)

Delegate to **value-first-gate**:

1. Run value assessment on the implementation scope
2. Record verdict in `triadev-handoff.json` → `value_gate.verdict`
3. If `GO`: proceed to Phase 4
4. If `REVISE`: return to Phase 1 with narrowed scope
5. If `NO-GO`: stop and explain

## Phase 4: Implementation (Extended Path Only)

Delegate to **tdd-sdd-development** for each task in batch order:

1. Read current batch from `triadev-handoff.json` → `scheduling.batches`
2. For each task:
   a. Update `implementation.current` in handoff.json
   b. Create/update SPEC.yaml for this task's requirements
   c. Run full TDD cycle (RED → GREEN → REFACTOR) per tdd-sdd rules
   d. On completion, move task to `implementation.completed`
   e. Update corresponding checkbox in `task_plan.md`
3. After all batches complete, set `current_phase` to `complete`

## Phase 5: Completion

1. Update all checkboxes in `task_plan.md`
2. Log final summary in `progress.md`
3. **Before** setting `current_phase` to `complete`, invoke [`verification-before-completion`](../verification-before-completion/SKILL.md) skill to verify: (a) all tasks in `scheduling.batches` appear in `implementation.completed`, (b) `value_gate.verdict == "GO"` (Extended) or `skipped` (Core), (c) handoff.json re-reads cleanly after write and schema-validates
4. Set `triadev-handoff.json` → `current_phase` to `complete`
5. If changes/ directory has active items, run archive

## Handoff Contract

The `triadev-handoff.json` file is the single source of truth for inter-skill state.

**Three files define the handoff**:

| File | Purpose | When to load |
|------|---------|--------------|
| [contracts/triadev-handoff.schema.json](contracts/triadev-handoff.schema.json) | Machine-readable JSON Schema for programmatic validation | Before writing handoff.json — validate after each write |
| [templates/triadev-handoff.json](templates/triadev-handoff.json) | Empty-instance template | At project init — copy as starting point |
| [references/handoff-contract.md](references/handoff-contract.md) | Human-readable schema explanation + ownership rules | When authoring or reviewing handoff logic |
| [references/phase-transitions.md](references/phase-transitions.md) | Legal phase transitions + canonical field values | **Always load before advancing `current_phase` or any `*.status` field** (drift-prevention) |

**Rules:**
- Each skill reads and writes ONLY its section
- triadev updates `current_phase` and coordinates transitions
- planning-with-files does NOT read handoff.json (it manages its own files)
- task-workflow reads `planning.tasks_extracted`, writes `scheduling.batches`
- tdd-sdd reads `scheduling.batches`, writes `implementation.*`

## Working Examples

See [examples/d-to-x-migration-partial/](examples/d-to-x-migration-partial/) for a
real (BRONZE-labeled) mid-flow Core-path project — useful reference for handoff field
shapes when `current_phase=scheduling` and `value_gate.status=skipped`.

## Boundary Rules

| File | Owner | Other skills may... |
|------|-------|-------------------|
| `task_plan.md` | planning-with-files | Read (task-workflow extracts tasks) |
| `findings.md` | planning-with-files | Read only |
| `progress.md` | planning-with-files | Append session entries |
| `triadev-handoff.json` | triadev (coordinator) | Read/write own section |
| `SPEC.yaml` | tdd-sdd | Read only (triadev, task-workflow) |
| `.tdd-state.json` | tdd-sdd | Not accessed by others |

## Project Structure

### Core Path
```
project/
├── task_plan.md            # Planning (planning-with-files)
├── findings.md             # Research (planning-with-files)
├── progress.md             # Session log (planning-with-files)
└── triadev-handoff.json    # Orchestration state (triadev)
```

### Extended Path
```
project/
├── task_plan.md
├── findings.md
├── progress.md
├── triadev-handoff.json
├── SPEC.yaml               # Specification (tdd-sdd)
├── .tdd-state.json         # TDD cycle evidence (tdd-sdd)
├── src/                    # Implementation
├── tests/                  # Tests
└── changes/                # Change tracking
    ├── active/
    └── archive/
```

## Brownfield Mode

For existing codebases:
1. Planning phase: assess current state, define what to change
2. tdd-sdd creates delta specs (not full specs) via `delta_specs:` in SPEC.yaml
3. Use `changes/active/{change-name}/` for tracking modifications
4. Archive on completion to `changes/archive/`

## Artifact Flow Mode

For complex features needing design documents:
1. Planning phase produces: `proposal.md` → `specs/` → `design.md` → `tasks.md`
2. Each artifact lives in `artifacts/` directory
3. Tasks extracted from `tasks.md` into handoff.json
4. Normal scheduling + implementation follows

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Skip route announcement | Always announce Core or Extended explicitly |
| Start coding without handoff.json | Create handoff.json first, even for simple projects |
| Let skills write to each other's files | Respect boundary rules above |
| Skip value gate on Extended path | Always run value-first-gate before TDD |
| Modify handoff.json without reading it first | Always read current state before writing |

## When NOT to Use TriaDev

- Single-file edits or quick fixes (< 5 tool calls)
- Pure Q&A or explanation requests
- Documentation-only changes with no research phase
- Bug fixes that are already well-understood

For these, just do the work directly without orchestration overhead.
