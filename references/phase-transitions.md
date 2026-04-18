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

---

## Skill Invocation Rules (Round-3, 混合架构边界)

TriaDev v3.1+ 采用**混合架构**：中央 orchestrator（triadev）协调跨 phase 转移，同时允许同 phase 内的 skill-to-skill 直接调用以降低编排开销。为避免"两套体系共存的复杂度税"，以下规则**显式化**边界。

### 必走 triadev orchestrator（中央协调）

跨越任何主 phase 边界的转移，必须由 triadev 发起并写入 `current_phase`：

| 源 phase → 目标 phase | 路径 | 触发者 |
|---|---|---|
| planning → scheduling | Core + Extended | triadev（读 planning-with-files 产出后发起） |
| scheduling → value-gate | Extended | triadev（读 task-workflow 产出后发起） |
| scheduling → complete | Core（Core 无实现阶段） | triadev |
| value-gate → implementation | Extended | triadev（校验 verdict=GO AND any_triggered=false 后发起） |
| value-gate → planning | Extended（REVISE 回退） | triadev |
| implementation → complete | Extended | triadev（校验全任务 completed 后发起） |

**规则核心**：`current_phase` 字段**只有 triadev 可写**。其他 skill 必须通过 triadev 请求 phase 转移，不可自行修改此字段。

### 允许 skill-to-skill invoke（同 phase 内纵向调用）

同一 phase 内的 skill 链调用无需回到 triadev，但**被调 skill 必须先读 handoff.json 校验前置条件**：

| 调用 | 前置条件（被调 skill 必须校验） |
|---|---|
| planning-with-files → task-workflow | `planning.status == "complete"` AND `planning.tasks_extracted` 非空 |
| task-workflow → value-first-gate（Extended） | `scheduling.status == "complete"` AND `scheduling.batches` 非空 |
| value-first-gate → tdd-sdd-development | `value_gate.verdict == "GO"` AND sidecar `rubber_stamp_flags.any_triggered == false` |
| Any skill → verification-before-completion | 总是允许（横切 skill，无前置） |
| Any skill → using-git-worktrees | 总是允许（独立 skill，无前置） |

### 禁止

- ❌ 任何 skill（除 triadev 外）修改 `current_phase`
- ❌ 任何 skill 修改其他 skill 的 handoff section（各 skill 只写自己的 section，见 `handoff-contract.md` 的 Ownership Rules 表）
- ❌ 跳过前置条件校验直接 invoke 下游 skill

### 违反后果

- 违反"只有 triadev 可写 current_phase"：下次 triadev 读 handoff 时发现 phase 矛盾（如 phase=implementation 但 value_gate.status=pending），会强制 REVISE 回退
- 违反"skill section 边界"：导致 handoff schema 校验失败（被引用 skill 的 contracts/stack-handshake.json 的 reads/writes 声明与实际不符）

### 设计意图

此规则来自 Round-3 的 comparison-matrix.md 冲突 C4 的裁决：
- 纯中央化（所有调用走 triadev）→ 编排开销大，skill 无法复用
- 纯去中心化（skill 自由互调）→ handoff.json 的"唯一 SoT"假设被破坏

混合的代价是"需要规则文档"（本段）；收益是"两种优势兼得"。相关讨论见 `projects/superpowers-comparison/decision.md`。
