---
name: triadev
description: >
  TRIGGER: triadev, Golden Triangle, 三元开发, TriadDev, brownfield workflow, delta spec, OpenSpec.
  TriadDev v2.1 style route+gate runtime: Core for planning, Extended for implementation.
---

# TriadDev Runtime Contract (Local Build)

## Core/Extended + Value Gate Contract

- Core route: planning/scheduling only (`init --route core`, `plan`, `workflow`).
- Extended route: implementation path (`extended|brownfield|artifact`).
- Value gate is explicit and configurable:
  - `disabled`: skip gate checks (audit event still written)
  - `advisory`: evaluate and log verdict, do not block implementation
  - `enforced`: block non-GO unless explicit bypass with reason
- Audit log path: `.triadev/value-gate-audit.jsonl`

## Commands

- `init`
- `init-brownfield`
- `plan`
- `detect-specs`
- `delta`
- `propose`
- `spec`
- `design`
- `tasks`
- `workflow` / `analyze`
- `value-gate`
- `implement`
- `archive`
- `sync`
- `status`
- `run`
- `stack-health`
- `stack-capabilities`
- `stack-export-state`
- `stack-import-state`

## Runtime Artifacts

- `triadev-project.json`
- `.triadev/state.json`
- `.triadev/workflow.json`
- `.triadev/value-gate-audit.jsonl`
- `task_plan.md`, `findings.md`, `progress.md`
- `SPEC.yaml`, `SPEC-delta.yaml`
- `artifacts/proposal.md`, `artifacts/specs/*.yaml`, `artifacts/design.md`, `artifacts/tasks.md`
- `value-review.md`

## Workflow Chains

- Core: `plan -> workflow`
- Extended/Brownfield/Artifact: `plan -> workflow -> value-gate -> implement -> sync`

## Value Gate Examples

```bash
triadev value-gate --mode advisory
triadev value-gate --mode enforced
triadev implement --all --bypass-gate --bypass-reason "incident mitigation with owner approval"
```

## Stack Handshake Examples

```bash
triadev stack-health --json
triadev stack-capabilities --json
triadev stack-export-state --output /tmp/stack-state.json
triadev stack-import-state --input /tmp/stack-state.json
```

## Notes

- `artifact` and `brownfield` are entry semantics that map to Extended execution.
- `run --from` respects gate mode and records bypass decisions.
