# Phase Transitions — triadev-handoff.json state machine

**Load this reference when:** about to change `current_phase` or any `*.status` field in
`triadev-handoff.json`. Lookup the source/target pair in the tables below and confirm
the transition is legal before writing.

## The canonical state machine

```
planning ──→ scheduling ──→ value-gate ──→ implementation ──→ complete
   │              │              │                                ↑
   │              │              └── (REVISE) → planning          │
   │              │                                               │
   │              └── (Core path, skip value-gate) ───────────────┘
   │                                                              │
   └── (Core path finishes after scheduling, no implementation) ──┘
```

## Legal `current_phase` transitions

| From | To | Path | Precondition |
|------|----|----|--------------|
| planning | scheduling | Core + Extended | `planning.status = complete` AND `planning.tasks_extracted` non-empty |
| scheduling | value-gate | Extended only | `scheduling.status = complete` AND `scheduling.batches` non-empty |
| scheduling | complete | Core only | `scheduling.status = complete` AND no tasks need implementation |
| value-gate | implementation | Extended only | `value_gate.verdict = GO` |
| value-gate | planning | Extended only | `value_gate.verdict = REVISE` (scope change required) |
| value-gate | — | Extended only | `value_gate.verdict = NO-GO` → halt, do not transition |
| implementation | complete | Extended only | All tasks in `scheduling.batches` appear in `implementation.completed` |

## Illegal transitions (reject or repair)

| Attempted | Why illegal | Repair |
|-----------|-------------|--------|
| planning → implementation | Skips scheduling + value-gate | Roll back to planning, complete scheduling first |
| scheduling → implementation (Extended) | Skips value-gate (required for Extended) | Roll back to scheduling, run value-first-gate |
| value-gate → implementation (verdict ≠ GO) | Gate blocks progression | Either re-run gate after addressing REVISE conditions, or accept NO-GO and halt |
| value-gate → implementation (rubber-stamp flag triggered) | Review is shallow; see `value-review.json.rubber_stamp_flags.any_triggered` | Re-do the review with honest thinking; one or more of the 5 validator rules is firing |
| implementation → value-gate | Cannot revisit value gate after starting impl | Start a new project or accept incomplete state |
| complete → any | Terminal state | Create a fresh handoff for new work |
| any → planning (except REVISE from value-gate) | Planning is the entry, not a revert target | Use REVISE path, or start fresh |

## Value-Gate → Implementation Preconditions

Transitioning `current_phase` from `value-gate` to `implementation` requires **both**:

1. `value_gate.verdict == "GO"`
2. The associated sidecar at `value_gate.review_path.replace('.md', '.json')` has `rubber_stamp_flags.any_triggered == false`

The second check is a safety net: even if the author manually wrote `verdict: "GO"` in the sidecar, the rubber-stamp flags are computed from the review content (score spread, empty evidence, blank Devil's Advocate, etc.) and cannot be silenced without fixing the underlying issue. Triadev reads both before allowing the transition.

Details: [../../value-first-gate/references/rubber-stamp-rules.md](../../value-first-gate/references/rubber-stamp-rules.md).

## Verdict-to-Status Mapping (value_gate)

When triadev reads `value-review.json` from value-first-gate, it writes into `triadev-handoff.json.value_gate` using this deterministic mapping:

| Source: `value-review.json.verdict` | Target: `value_gate.status` | Target: `value_gate.verdict` |
|---|---|---|
| `GO` | `passed` | `GO` |
| `REVISE` | `blocked` | `REVISE` |
| `NO-GO` | `blocked` | `NO-GO` |
| *(Core path — gate not invoked)* | `skipped` | `null` |

**Ownership reminder**: value-first-gate owns the sidecar (it writes `value-review.json`). Triadev owns the copy+mapping (it reads the sidecar and writes `triadev-handoff.json`). Value-first-gate never writes `status` directly.

## Drift patterns observed (canonical field values)

### `planning.status`

| Observed drift | Canonical value | Notes |
|----------------|-----------------|-------|
| `"done"`, `"finished"` | `"complete"` | Use `complete`, matching the phase terminology |
| `"in_progress"` | `"pending"` | During planning, status stays `pending` until all tasks extracted |

### `scheduling.status`

| Observed drift | Canonical value |
|----------------|-----------------|
| `"done"`, `"scheduled"` | `"complete"` |
| `"running"` | `"pending"` |

### `value_gate.status`

Legal values: `"pending"` | `"passed"` | `"blocked"` | `"skipped"`

| Observed drift | Canonical value |
|----------------|-----------------|
| `"go"`, `"approved"` | `"passed"` (status) + `"GO"` (verdict) |
| `"no-go"`, `"rejected"` | `"blocked"` (status) + `"NO-GO"` (verdict) |
| Core path leaves as `"pending"` | `"skipped"` — be explicit for Core |

### `value_gate.verdict`

Legal values: `"GO"` | `"REVISE"` | `"NO-GO"` | `null`

Always uppercase. Null only when `status ∈ {pending, skipped}`.

### `implementation.status`

Legal values: `"pending"` | `"in_progress"` | `"complete"`

Note the underscore in `in_progress`. Common drift: `"in-progress"` (hyphen) or
`"running"`.

## Atomic update rule

When advancing a phase, update in this order within a single write:

1. Ensure source section has `status = complete` (or equivalent terminal state)
2. Change `current_phase` to the new phase name
3. Set target section's `status` to `pending` (if it starts a new phase's work)

Never leave the file with `current_phase = X` but `X.status = pending` for a phase
that has already been worked on — that's an ambiguous state.

## Validation checklist before each write

- [ ] Transition appears in the "Legal transitions" table above
- [ ] All precondition fields satisfied
- [ ] Field values are canonical (no drift terms)
- [ ] `version` field unchanged (we don't bump within a project)
- [ ] No section's data is accidentally overwritten to `null` or `[]`
- [ ] Run JSON schema validation against `contracts/triadev-handoff.schema.json` if
      available (non-blocking if schema path doesn't exist)

## When to consult this file

- Before advancing `current_phase`
- After `/clear` when deciding where to resume from
- When writing `*.status` in any section
- When an eval case fails with "illegal phase" reason
