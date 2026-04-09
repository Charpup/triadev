# Routing Rules — Core vs Extended Path

## Decision Tree

```
User request arrives
  │
  ├─ Contains coding keywords? ──→ Extended Path
  │   (implement, build, create module, refactor, add feature,
  │    write tests, fix bug in code, add endpoint, new API)
  │
  ├─ Contains research/planning keywords? ──→ Core Path
  │   (research, analyze, compare, plan, document, investigate,
  │    evaluate, review architecture, audit, report)
  │
  └─ Ambiguous? ──→ Default to Core, escalate if coding emerges
```

## Route Escalation

If you start on Core path and discover coding is needed:

1. Announce: "Escalating to Extended path — implementation required for [reason]."
2. Update `triadev-handoff.json` → `route` to `"extended"`
3. Before any implementation, run value-first-gate
4. Continue with TDD/SDD

De-escalation (Extended → Core) is also allowed if coding turns out unnecessary.

## Edge Cases

### "Fix this bug"
- If the bug is well-understood (< 5 lines): **Don't use TriaDev at all**
- If the bug requires investigation: **Core path** (research phase)
- If the fix involves multiple files + tests: **Extended path**

### "Refactor this module"
- Always **Extended path** — refactoring needs tests to verify behavior preservation

### "Write documentation"
- **Core path** — documentation is research + writing, not coding

### "Create a new skill"
- **Extended path** — skills have SKILL.md + potential scripts that benefit from spec-driven approach

### "Evaluate three options and recommend one"
- **Core path** — pure analysis, no implementation

## Examples

| Request | Route | Rationale |
|---------|-------|-----------|
| "Research API gateway options for our stack" | Core | Analysis, no code |
| "Build a rate limiter with Redis" | Extended | New feature, needs spec + tests |
| "Plan the Q3 migration strategy" | Core | Planning, no code |
| "Add OAuth support to our auth module" | Extended | Feature addition, existing code |
| "What's the best approach for caching?" | Don't use TriaDev | Simple Q&A |
| "Change the button color to blue" | Don't use TriaDev | Trivial edit |
