# Example: d-to-x-migration (BRONZE — partial / reconstructed handoff)

## What this is

A real Core-path project (D:\ → X:\ workspace migration, 2026-04-16) that used
`planning-with-files` directly. The `task_plan.md`, `findings.md`, `progress.md` here
are **verbatim snapshots** of the original sandbox run.

The `triadev-handoff.json` is **reconstructed** — the original run did not actually
use triadev orchestration. The handoff shown here is what the handoff file **should**
have looked like had triadev been driving the work.

## Why BRONZE

- ✅ Real planning trio (not constructed)
- ✅ Real mid-flow state (Stage A complete, Stages B–D pending)
- ✅ Captures Core-path characteristics (non-coding, `value_gate.status=skipped`)
- ⚠️ Handoff was retrofitted — not observed
- ⚠️ Project is paused mid-flow; `current_phase=scheduling`, not `complete`

Use this example to learn **handoff field shapes** for a mid-Core-path state, not as
a template of a completed workflow.

For a fully-completed reference, see `tdd-sdd-development/examples/pdf-ocr-skill/`
(GOLD — Extended-path, completed cycle).

## Files

| File | Status | Source |
|------|--------|--------|
| task_plan.md | real snapshot | `sandbox/d-to-x-migration/task_plan.md` |
| findings.md | real snapshot | `sandbox/d-to-x-migration/findings.md` |
| progress.md | real snapshot | `sandbox/d-to-x-migration/progress.md` |
| triadev-handoff.json | reconstructed | derived from above three files |

## Characteristic lessons

1. **Core path, not Extended**: `route=core` because the work is migration + decision,
   not coding. `value_gate.status=skipped`, `implementation.status=pending`.
2. **Mid-flow handoff**: `current_phase=scheduling` even though planning is complete,
   because not all extracted tasks are scheduled yet.
3. **tasks_extracted is subset of task_plan**: completed Stage A tasks (A1–A3) are
   NOT in tasks_extracted; only remaining actionable items are.
4. **Progress entries in progress.md**: informal and human-facing; handoff.json
   mirrors the structural state, not the narrative.

## What would make this GOLD

- Complete Stages B–D
- Transition `current_phase` through `scheduling → complete`
- Append completion timestamps in progress.md
- Archive the project post-completion (triadev Phase 5)
