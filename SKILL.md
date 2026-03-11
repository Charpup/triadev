---
name: triadev
description: >-
  TRIGGER: triadev, Golden Triangle, 三元开发, TriadDev, brownfield workflow, delta spec, OpenSpec.
  TriadDev v2.0 - Golden Triangle Development Workflow unifying planning-with-files + task-workflow +
  tdd-sdd-development v2.0. Use for: multi-step projects needing structured planning, task dependency
  management, TDD enforcement, greenfield/brownfield/artifact-based workflows.
  NOT for: simple one-off tasks, single-file edits, or generic "plan" requests.
---

# TriadDev 🜁 v2.0 - Golden Triangle Development

**Version:** 2.0.0 | **Author:** Galatea | **Homepage:** https://github.com/Charpup/triadev

> **TriadDev** integrates the "Golden Triangle" of OpenClaw development: **planning-with-files** + **task-workflow** + **tdd-sdd-development v2.0**.

## What's New in v2.0

### 🆕 Brownfield Support
Initialize projects from existing codebases:
```bash
triadev init-brownfield ./existing-project --name "Legacy Migration"
```

### 🆕 Delta Spec Integration
Track changes to existing systems:
```bash
triadev delta --add "new feature" --modify "existing behavior"
```

### 🆕 Artifact Flow Mode
OpenSpec-inspired full workflow:
```bash
triadev init "Complex Feature" --mode artifact
# Creates: proposal → specs → design → tasks
```

### 🆕 Archive & Spec Evolution
Complete changes and track spec history:
```bash
triadev archive "feature-name"
# Merges deltas, moves to archive/, updates main specs
```

## The Golden Triangle v2.0

```
        📋 PLANNING
       (planning-with-files)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
📊 WORKFLOW          🧪 TDD/SDD v2.0
(task-workflow)    (tdd-sdd-development)
    │                   │
    │   ┌───────────┐   │
    └───┤ Brownfield├───┘
        │  Support  │
        └───────────┘
```

## Workflow Modes

### Mode A: Greenfield (Default) - New Projects
For building from scratch:
```bash
triadev init "My Project" --template web
triadev plan --objectives "API,Tests,Deploy"
triadev analyze
triadev implement --all
triadev archive
```

### Mode B: Brownfield (NEW) - Existing Projects
For working with existing code:
```bash
triadev init-brownfield ./existing-project --name "Migration"
triadev detect-specs  # Auto-generate base specs
triadev delta --add "new feature"
triadev implement
triadev archive
```

### Mode C: Artifact Flow (NEW) - Complex Projects
For features needing design docs:
```bash
triadev init "Complex Feature" --mode artifact
triadev propose "Add real-time sync"
triadev spec  # Create from proposal
triadev design  # Technical approach
triadev tasks   # Implementation steps
triadev implement
triadev archive
```

## Quick Start

### Greenfield Project
```bash
# Initialize
triadev init "User Service API" --template api
cd user-service-api

# Plan
triadev plan --objectives "Design schema,Implement CRUD,Add auth,Write tests"

# Execute everything
triadev run --from plan
```

### Brownfield Project (NEW)
```bash
# Initialize from existing code
triadev init-brownfield ./legacy-app --name "Modernization"

# Detect current specs
triadev detect-specs

# Plan changes
triadev delta --add "OAuth support" --modify "session handling"

# Execute
triadev implement --all

# Archive changes
triadev archive "oauth-migration"
```

### Artifact Flow (NEW)
```bash
# Initialize with full artifacts
triadev init "Payment System" --mode artifact

# Create proposal
triadev propose --intent "Add Stripe integration" \
                --scope "in: payment processing" \
                --scope "out: tax calculation"

# Generate specs from proposal
triadev spec --from-proposal

# Create design doc
triadev design --approach "Webhook-based async processing"

# Create task list
triadev tasks

# Implement
triadev implement --all

# Archive
triadev archive
```

## Commands Reference

### Initialization Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize greenfield project | `triadev init "Name" --template web` |
| `init-brownfield` | Initialize from existing code (NEW) | `triadev init-brownfield ./project` |
| `propose` | Create proposal.md (artifact mode) | `triadev propose "intent"` |

### Planning Commands

| Command | Description | Example |
|---------|-------------|---------|
| `plan` | Create planning docs | `triadev plan --objectives "obj1,obj2"` |
| `detect-specs` | Auto-generate specs from code (NEW) | `triadev detect-specs` |
| `delta` | Create delta specs (NEW) | `triadev delta --add "feature"` |

### Analysis Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze and schedule | `triadev analyze` |
| `spec` | Generate specs (artifact mode) | `triadev spec --from-proposal` |
| `design` | Create design.md (artifact mode) | `triadev design` |
| `tasks` | Create tasks.md (artifact mode) | `triadev tasks` |

### Implementation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `implement` | Run TDD workflow | `triadev implement task-001` |
| `run` | Execute full workflow | `triadev run --from plan` |

### Completion Commands (NEW)

| Command | Description | Example |
|---------|-------------|---------|
| `archive` | Complete and archive change | `triadev archive "feature"` |
| `sync` | Merge deltas to main specs | `triadev sync` |
| `status` | Show project status | `triadev status --verbose` |

## Project Structure

### Greenfield Structure
```
my-project/
├── triadev-project.json
├── task_plan.md
├── findings.md
├── progress.md
├── SPEC.yaml
├── src/
└── tests/
```

### Brownfield Structure (NEW)
```
my-project/
├── triadev-project.json
├── task_plan.md
├── SPEC.yaml              # Base specs (auto-generated)
├── SPEC-delta.yaml        # Current changes (NEW)
├── changes/               # Change tracking (NEW)
│   ├── active/
│   │   └── oauth-migration/
│   └── archive/
│       └── 2026-02-25-oauth-migration/
├── src/                   # Existing code
└── tests/
```

### Artifact Mode Structure (NEW)
```
my-project/
├── triadev-project.json
├── task_plan.md
├── artifacts/             # Current change artifacts
│   ├── proposal.md
│   ├── specs/
│   ├── design.md
│   └── tasks.md
├── changes/
│   └── archive/
├── SPEC.yaml              # Main specs (source of truth)
├── src/
└── tests/
```

## Integration with tdd-sdd-development v2.0

TriadDev v2.0 leverages new tdd-sdd features:

### Brownfield Integration
```python
# TriadDev calls tdd-sdd v2.0
tdd_sdd.init_brownfield(project_dir=".")
tdd_sdd.create_delta_spec(...)
tdd_sdd.archive_change(...)
```

### Artifact Flow Integration
```python
# TriadDev orchestrates artifact creation
tdd_sdd.init_artifact_flow(skill_name="...")
tdd_sdd.create_proposal(...)
tdd_sdd.create_specs_from_proposal()
tdd_sdd.create_design_doc()
tdd_sdd.create_task_list()
```

### Delta Spec in Workflow
```yaml
# task_plan.md includes delta spec phases
## Phase 1: Detect Base Specs (brownfield)
## Phase 2: Create Delta Specs
## Phase 3: Generate Tests
## Phase 4: Implement Changes
## Phase 5: Archive
```

## Configuration

### Project Config (triadev-project.json)

```json
{
  "name": "My Project",
  "template": "web",
  "mode": "greenfield",
  "created_at": "2026-02-25T10:00:00",
  "triadev_version": "2.0.0",
  "tdd_sdd_version": "2.0.0"
}
```

### Mode-Specific Config

**Brownfield mode:**
```json
{
  "mode": "brownfield",
  "base_specs_generated": true,
  "active_changes": ["oauth-migration"]
}
```

**Artifact mode:**
```json
{
  "mode": "artifact",
  "artifacts": ["proposal", "specs", "design", "tasks"],
  "current_artifact": "design"
}
```

## Real-World Examples

### Example 1: Greenfield API
```bash
triadev init "Payment API" --template api
triadev plan --objectives "Design schema,Implement CRUD,Add Stripe,Write tests"
triadev run --from plan
```

### Example 2: Brownfield Migration (NEW)
```bash
triadev init-brownfield ./legacy-auth --name "Auth Modernization"
triadev detect-specs
triadev delta --add "JWT support" --modify "session storage" --remove "legacy tokens"
triadev analyze
triadev implement --all
triadev archive "auth-modernization"
```

### Example 3: Complex Feature with Artifacts (NEW)
```bash
triadev init "Real-time Sync" --mode artifact
triadev propose --intent "Add WebSocket sync"
triadev spec
triadev design --approach "Event-driven with Redis"
triadev tasks
triadev implement task-001
triadev implement task-002
triadev verify
triadev archive
```

## Migration from v1.x

v1.x projects are **fully compatible** with v2.0:

1. Update `triadev-project.json`:
   ```json
   {"triadev_version": "2.0.0"}
   ```

2. To use brownfield features:
   ```bash
   triadev init-brownfield . --name "Current Project"
   ```

3. To use artifact mode:
   ```bash
   triadev config mode artifact
   ```

No breaking changes - all v1.x commands continue to work.

## Dependencies

TriadDev v2.0 requires:

| Skill | Version | Purpose |
|-------|---------|---------|
| planning-with-files | >= 2.10.0 | File-based planning |
| task-workflow | >= 3.0.0 | DAG scheduling |
| tdd-sdd-development | >= 2.0.0 | TDD/SDD with delta specs |

## Troubleshooting

### Brownfield Detection Fails
```bash
# Manual spec generation
triadev detect-specs --manual
```

### Delta Spec Conflicts
```bash
# Check for conflicts before archive
triadev check-conflicts
```

### Artifact Mode Issues
```bash
# Reset to standard mode
triadev config mode greenfield
```

## Roadmap

- [x] Brownfield support (v2.0)
- [x] Delta specs (v2.0)
- [x] Artifact flow (v2.0)
- [ ] Web UI for visual workflow
- [ ] CI/CD pipeline integration
- [ ] Multi-agent collaborative projects

## Acknowledgments

- **OpenSpec** - Inspiration for delta specs and artifact flow
- **planning-with-files** by OthmanAdi
- **task-workflow** - DAG scheduling
- **tdd-sdd-development v2.0** - Enhanced TDD/SDD
- **Charpup** - Project sponsor
- **Galatea** 🜁 - TriadDev architect

---

**Build with the Golden Triangle v2.0!** 🚀

```bash
git clone https://github.com/Charpup/triadev.git ~/.openclaw/skills/triadev
~/.openclaw/skills/triadev/install.sh
triadev init "My Project" && triadev run
```
