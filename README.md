# TriadDev 🜁

**The Golden Triangle of OpenClaw Development**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/Charpup/triadev/releases/tag/v2.1.0)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-4CAF50.svg)](https://openclaw.ai)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![evals](https://img.shields.io/badge/evals-3%20cases-blueviolet.svg)](evals/evals.json)

> **TriadDev** (三元开发) unifies the three essential OpenClaw skills — **planning-with-files** + **task-workflow** + **tdd-sdd-development v2.0** — into a single orchestrated workflow for both new and existing projects.

---

## AI Agent Quick Reference

```yaml
# Skill identity (SKILL.md frontmatter)
name: triadev
version: "2.1.0"
triggers:
  - "triadev"
  - "Golden Triangle"
  - "plan workflow"
  - "task management"
  - "brownfield"
  - "delta spec"
  - "init project with planning and TDD"

# Runtime requirements
requires:
  bins: [python3, triadev]
  env: []
  os: [linux, macos]

# Install
run: bash ~/.openclaw/skills/triadev/install.sh
```

**When to invoke:**
- Starting a new project that needs planning + task scheduling + TDD (greenfield)
- Modernizing / adding features to an existing codebase (brownfield)
- Any project requiring structured planning, dependency management, and test coverage

**When NOT to invoke:**
- Simple single-file edits or quick bug fixes
- Projects that need only one of the three component skills

---

## The Golden Triangle v2.0

```
                    📋 PLANNING
               (planning-with-files)
                task_plan.md
                findings.md
                progress.md
                      ↓
         ┌────────────┴────────────┐
         ↓                         ↓
   📊 WORKFLOW              🧪 TDD/SDD v2.0
  (task-workflow)       (tdd-sdd-development)
  Dependency DAG         SPEC.yaml + delta specs
  Complexity Score       RED → GREEN → REFACTOR
  Batch Schedule         80% coverage enforced
         │                         │
         └──────── Brownfield ──────┘
                    Support
```

---

## What's New in v2.0

### Brownfield Support

Initialize from existing codebases:

```bash
triadev init-brownfield ./existing-project --name "Legacy Migration"
triadev detect-specs    # auto-generate base SPEC.yaml from code
triadev delta --add "OAuth support" --modify "session handling"
triadev implement
triadev archive "oauth-migration"
```

### Delta Spec Integration

Track changes to existing systems with OpenSpec-inspired delta specs:

```bash
triadev delta --add "new feature" --modify "existing behavior" --remove "deprecated API"
```

### Artifact Flow Mode

Full design pipeline for complex features:

```bash
triadev init "Payment System" --mode artifact
triadev propose --intent "Add Stripe integration" --scope "in: payments, out: taxes"
triadev spec --from-proposal
triadev design --approach "Webhook-based async"
triadev tasks
triadev implement --all
triadev archive
```

### Archive & Spec Evolution

```bash
triadev archive "feature-name"
# → merges delta specs into main SPEC.yaml
# → moves artifacts to changes/archive/YYYY-MM-DD-feature-name/
```

---

## Workflow Modes

### Mode A: Greenfield (new projects)

```bash
triadev init "User Service API" --template api
cd user-service-api
triadev plan --objectives "Design schema,Implement CRUD,Add auth,Write tests"
triadev analyze           # build DAG, assign complexity, create batch schedule
triadev implement --all   # TDD cycle for each task
triadev archive           # complete project
```

### Mode B: Brownfield (existing projects)

```bash
triadev init-brownfield ./legacy-app --name "Auth Modernization"
triadev detect-specs      # scan existing code → generate base SPEC.yaml
triadev delta --add "JWT support" --modify "session storage" --remove "legacy tokens"
triadev analyze
triadev implement --all
triadev archive "auth-modernization"
```

### Mode C: Artifact Flow (complex features)

```bash
triadev init "Payment Gateway" --mode artifact
triadev propose --intent "Add Stripe integration"
triadev spec
triadev design --approach "Webhook-based async processing"
triadev tasks
triadev implement --all
triadev archive
```

---

## Commands Reference

### Initialization

| Command | Description |
|---------|-------------|
| `triadev init "Name" --template [web\|cli\|api\|lib]` | Start greenfield project |
| `triadev init-brownfield ./dir --name "Name"` | Start from existing code |
| `triadev init "Name" --mode artifact` | Full artifact flow mode |

### Planning & Analysis

| Command | Description |
|---------|-------------|
| `triadev plan --objectives "obj1,obj2"` | Create planning docs via planning-with-files |
| `triadev detect-specs` | Auto-generate SPEC.yaml from existing code |
| `triadev delta --add "X" --modify "Y"` | Create delta specs |
| `triadev analyze` | Build DAG, score complexity, create batch schedule |

### Implementation

| Command | Description |
|---------|-------------|
| `triadev implement <task-id>` | TDD cycle for one task |
| `triadev implement --all` | TDD cycle for all scheduled tasks |
| `triadev run --from [plan\|analyze\|implement]` | Run full pipeline from a stage |

### Completion

| Command | Description |
|---------|-------------|
| `triadev archive "name"` | Merge deltas, archive artifacts, mark complete |
| `triadev sync` | Merge delta specs to main SPEC.yaml (without archive) |
| `triadev status --verbose` | Show project status, DAG, batch progress |

---

## Project Templates

| Template | Use Case | Structure |
|----------|----------|-----------|
| `web` | Web applications | Frontend + Backend + Tests |
| `cli` | CLI tools | Command-line + Args + Tests |
| `api` | REST/GraphQL APIs | Endpoints + Schemas + Tests |
| `lib` | Libraries / SDKs | Core + Interfaces + Tests |

---

## Dependencies

| Skill | Version | Purpose |
|-------|---------|---------|
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files) | ≥ 2.10.0 | File-based planning (Manus pattern) |
| [task-workflow](https://github.com/Charpup/openclaw-task-workflow) | ≥ 3.0.0 | DAG scheduling and complexity analysis |
| [tdd-sdd-development](https://github.com/Charpup/openclaw-tdd-sdd-skill) | ≥ 2.0.0 | TDD/SDD with delta specs |

---

## Installation

```bash
git clone --recursive https://github.com/Charpup/triadev.git ~/.openclaw/skills/triadev
cd ~/.openclaw/skills/triadev
./install.sh

triadev --version
```

---

## Evals

Test cases in [`evals/evals.json`](evals/evals.json):

| ID | Scenario | Expected Trigger |
|----|----------|-----------------|
| 1 | Init new "payment-gateway" project with full Golden Triangle | ✅ Yes |
| 2 | Brownfield init for legacy e-commerce checkout modernization | ✅ Yes |
| 3 | Change a button color in a React component | ❌ No |

---

## Real-World Results

Projects built with TriadDev Golden Triangle workflow:

| Project | Tasks | Time | Success |
|---------|-------|------|---------|
| MCP Migration | 6 | 28 min | 100% |
| Schema Sync System | 8 | 50 min | 100% |
| Task-Workflow v3.1.0 | 6 | 10 min | 100% |
| Auto-Pilot Skill Pack | 5 | 30 min | 100% |

---

## Version History

| Version | Changes |
|---------|---------|
| **v2.1.0** | Add `metadata.openclaw` compliance; add `evals/evals.json` (3 cases) |
| **v2.0.0** | Brownfield support, delta spec integration, artifact flow mode, archive & evolution |
| **v1.0.0** | Initial Golden Triangle: greenfield workflow, planning + workflow + TDD |

---

## Architecture

```
triadev/
├── bin/triadev                   # CLI entry point
├── lib/
│   └── triadev_orchestrator.py   # Core orchestration logic
├── templates/                    # Project templates (web, cli, api, lib)
├── install.sh                    # Installer (adds triadev to PATH)
├── SKILL.md                      # OpenClaw skill manifest
└── tests/

Project structure (created by init):
my-project/
├── triadev-project.json          # Project config + mode
├── task_plan.md                  # planning-with-files
├── findings.md
├── progress.md
├── SPEC.yaml                     # Source of truth (tdd-sdd)
├── SPEC-delta.yaml               # Active changes (brownfield mode)
├── changes/                      # Change tracking
│   ├── active/
│   └── archive/
├── src/
└── tests/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Brownfield detection fails | `triadev detect-specs --manual` |
| Delta spec conflicts | `triadev check-conflicts` before archive |
| Artifact mode issues | `triadev config mode greenfield` to reset |

---

## Acknowledgments

- [planning-with-files](https://github.com/OthmanAdi/planning-with-files) by OthmanAdi — Manus-pattern planning
- [task-workflow](https://github.com/Charpup/openclaw-task-workflow) — DAG scheduling
- [tdd-sdd-development](https://github.com/Charpup/openclaw-tdd-sdd-skill) — TDD/SDD v2.0
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — Inspiration for delta specs and artifact flow
- **Charpup** — Project sponsor
- **Galatea** 🜁 — TriadDev architect

## License

MIT — [Charpup](https://github.com/Charpup)

---

```bash
git clone --recursive https://github.com/Charpup/triadev.git ~/.openclaw/skills/triadev
~/.openclaw/skills/triadev/install.sh
triadev init "My Project" && triadev run
```
