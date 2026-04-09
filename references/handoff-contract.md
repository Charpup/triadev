# Handoff Contract — triadev-handoff.json

The handoff file is the inter-skill coordination mechanism. It lives in the project root
and tracks the orchestration state machine.

## Schema

```json
{
  "version": "1.0.0",
  "project": "<string: project name>",
  "route": "<string: core|extended>",
  "current_phase": "<string: planning|scheduling|value-gate|implementation|complete>",

  "planning": {
    "status": "<string: pending|complete>",
    "files": ["task_plan.md", "findings.md", "progress.md"],
    "tasks_extracted": [
      {
        "id": "<string: kebab-case, e.g. 'research-gateways'>",
        "name": "<string: human-readable>",
        "complexity": "<number: 1-10>",
        "dependencies": ["<string: task id>"]
      }
    ]
  },

  "scheduling": {
    "status": "<string: pending|complete>",
    "batches": [
      ["<task-id>", "<task-id>"],
      ["<task-id>"]
    ]
  },

  "value_gate": {
    "status": "<string: pending|passed|blocked|skipped>",
    "verdict": "<string: GO|REVISE|NO-GO|null>",
    "review_path": "<string: path to value-review.md or null>"
  },

  "implementation": {
    "status": "<string: pending|in_progress|complete>",
    "completed": ["<task-id>"],
    "current": "<string: task-id or null>",
    "spec_path": "<string: path to SPEC.yaml or null>",
    "tdd_state_path": "<string: path to .tdd-state.json or null>"
  }
}
```

## State Machine

```
planning → scheduling → value-gate (Extended only) → implementation → complete
                ↓ (Core path)
              complete
```

### Transitions

| From | To | Trigger |
|------|----|---------|
| planning | scheduling | All tasks extracted from task_plan.md |
| scheduling | value-gate | Batches computed (Extended only) |
| scheduling | complete | Batches computed (Core path, if no execution tasks remain) |
| value-gate | implementation | Verdict is GO |
| value-gate | planning | Verdict is REVISE (narrow scope) |
| implementation | complete | All tasks in all batches completed |

### Core Path Shortcut

On Core path, `value_gate.status` is set to `"skipped"` and `implementation` stays `"pending"`.
The work (research, writing, analysis) happens directly after scheduling — no TDD needed.

## Ownership Rules

| Section | Written by | Read by |
|---------|-----------|---------|
| `version`, `project`, `route`, `current_phase` | triadev | all skills |
| `planning.*` | triadev (after planning-with-files completes) | task-workflow |
| `scheduling.*` | task-workflow | triadev, tdd-sdd |
| `value_gate.*` | value-first-gate | triadev |
| `implementation.*` | tdd-sdd | triadev |

## Task Extraction Rules

When extracting tasks from `task_plan.md`:

1. Look for checkbox items (`- [ ]`) that represent discrete work units
2. Ignore section headers, sub-items that are part of a larger task, and completed items
3. Assign IDs using kebab-case derived from the task name
4. Estimate complexity based on:
   - 1-3: Well-understood, single-file changes
   - 4-6: Some exploration needed, multi-file changes
   - 7-10: Significant unknowns, architecture decisions
5. Infer dependencies from task ordering and explicit mentions

## Completion Sync

When tdd-sdd marks a task as completed in `implementation.completed`:
- triadev finds the corresponding checkbox in `task_plan.md`
- Updates it from `- [ ]` to `- [x]`
- Logs the completion in `progress.md`
