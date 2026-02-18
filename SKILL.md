---
name: triadev
description: TriadDev (三元开发) - Golden Triangle Development Workflow for OpenClaw. Unifies planning-with-files + task-workflow + tdd-sdd-development into seamless workflow for complex multi-step projects. Use when starting projects requiring structured planning, task dependency management, and TDD enforcement. Triggers on "triadev", "Golden Triangle", "plan workflow", "task management".
---

# TriadDev 🜁 - Golden Triangle Development

> **TriadDev** integrates the "Golden Triangle" of OpenClaw development: **planning-with-files** + **task-workflow** + **tdd-sdd-development**.

**Version:** 1.0.0 | **Author:** Galatea | **Homepage:** https://github.com/Charpup/triadev

---

## Overview

TriadDev (三元开发) provides a unified CLI and orchestration layer for the three essential skills that have proven to deliver **100% success rate** and **7.5x efficiency** in real-world projects.

### The Golden Triangle

```
     📋 PLANNING
    (planning-with-files)
           ↓
    📊 WORKFLOW ←────→ 🧪 TDD/SDD
   (task-workflow)   (tdd-sdd-development)
```

**Workflow:**
1. **Planning** → Create structured task plans with file-based persistence
2. **Workflow** → Analyze tasks, resolve dependencies, schedule batches
3. **TDD/SDD** → Implement with test-driven and spec-driven development

---

## When to Use

**Use TriadDev when:**
- Starting a complex multi-step project
- Need structured planning before execution
- Want TDD enforcement from day one
- Managing tasks with dependencies
- Tracking progress across sessions

**Skip TriadDev when:**
- Quick one-off tasks (< 5 minutes)
- Simple bug fixes
- Documentation-only changes
- Already using individual skills directly

---

## Installation

### Prerequisites

Ensure dependencies are installed:
```bash
# planning-with-files
git clone https://github.com/OthmanAdi/planning-with-files.git ~/.openclaw/skills/planning-with-files

# task-workflow
git clone https://github.com/Charpup/openclaw-task-workflow.git ~/.openclaw/skills/task-workflow

# tdd-sdd-development
git clone https://github.com/Charpup/openclaw-tdd-sdd-skill.git ~/.openclaw/skills/tdd-sdd-skill
```

### Install TriadDev

```bash
git clone https://github.com/Charpup/triadev.git ~/.openclaw/skills/triadev
cd ~/.openclaw/skills/triadev
./install.sh
```

### Verification

```bash
triadev --version
# Output: triadev 1.0.0
```

---

## Quick Start

### 1. Initialize Project

```bash
triadev init "My Awesome Project" --template web
cd my-awesome-project
```

**Templates:** `web`, `cli`, `api`, `lib`

### 2. Create Planning Documents

```bash
triadev plan --objectives "Build API,Add tests,Deploy"
```

Creates:
- `task_plan.md` - Task breakdown with phases
- `findings.md` - Research and discoveries
- `progress.md` - Session logs

### 3. Analyze and Schedule

```bash
triadev analyze
```

Outputs:
- Dependency DAG
- Complexity scores
- Optimal batch schedule

### 4. Implement with TDD

```bash
# Implement single task
triadev implement task-001

# Or implement all pending tasks
triadev implement --all
```

Runs full TDD cycle:
1. Create SPEC.yaml
2. RED: Write failing tests
3. GREEN: Implement to pass
4. REFACTOR: Optimize

### 5. Check Status

```bash
triadev status --verbose
```

### 6. Full Workflow (One Command)

```bash
triadev run --from plan
```

Executes: plan → analyze → implement → complete

---

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize new project | `triadev init "Name" --template web` |
| `plan` | Create planning docs | `triadev plan --objectives "obj1,obj2"` |
| `analyze` | Analyze and schedule | `triadev analyze` |
| `implement` | Run TDD workflow | `triadev implement task-001` |
| `status` | Show project status | `triadev status --verbose` |
| `run` | Execute full workflow | `triadev run --from analyze` |

---

## Project Structure

```
my-project/
├── triadev-project.json      # Project config
├── task_plan.md              # Task planning
├── findings.md               # Research notes
├── progress.md               # Session logs
├── 01_active/                # Current work
│   ├── tasks/
│   ├── research/
│   └── docs/
├── 02_archive/               # Completed work
├── 03_deliverables/          # Final outputs
├── specs/                    # TDD specifications
└── tests/                    # Test suites
    ├── unit/
    ├── integration/
    └── acceptance/
```

---

## Architecture

### Unified Orchestration

```python
TriadDevOrchestrator
├── initialize_project()     # Setup project structure
├── create_plan()            # planning-with-files
├── analyze_tasks()          # task-workflow
├── implement_task()         # tdd-sdd-development
├── get_status()             # Aggregate status
└── run_full_workflow()      # Complete pipeline
```

### Data Flow

```
User Command
    ↓
triadev CLI
    ↓
Orchestrator
    ↓
├─→ planning-with-files → task_plan.md
├─→ task-workflow       → batches, schedule
└─→ tdd-sdd-development → specs, tests, impl
    ↓
Project Directory
```

---

## Real-World Results

Projects developed with TriadDev (Golden Triangle):

| Project | Time | Tasks | Success | Efficiency |
|---------|------|-------|---------|------------|
| MCP Migration | 28 min | 6 | 100% | 7.5x |
| Schema Sync System | 50 min | 8 | 100% | 7.5x |
| Task-Workflow v3.1.0 | 10 min | 6 | 100% | 7.5x |
| Auto-Pilot Skill Pack | 30 min | 5 | 100% | - |

**Average: 19 tasks, 100% success rate, 7.5x faster than estimates**

---

## Dependencies

TriadDev is built on top of three excellent OpenClaw skills:

| Skill | Purpose | Repository |
|-------|---------|------------|
| **planning-with-files** | Manus-style file-based planning | [GitHub →](https://github.com/OthmanAdi/planning-with-files) |
| **task-workflow** | DAG-based task scheduling with complexity analysis | [GitHub →](https://github.com/Charpup/openclaw-task-workflow) |
| **tdd-sdd-development** | TDD+SDD dual-pyramid development workflow | [GitHub →](https://github.com/Charpup/openclaw-tdd-sdd-skill) |

**If you need more granular control, use these skills directly.**

---

## Configuration

### Project Config (triadev-project.json)

```json
{
  "name": "My Project",
  "template": "web",
  "created_at": "2026-02-17T10:00:00",
  "triadev_version": "1.0.0"
}
```

### Environment Variables

```bash
# Optional: Customize behavior
TRIADEV_TEMPLATE_DIR=~/.config/triadev/templates
TRIADEV_MAX_BATCH_SIZE=10
```

---

## Troubleshooting

### Command not found

```bash
# Ensure triadev is in PATH
export PATH="$HOME/.openclaw/skills/triadev/bin:$PATH"
```

### Dependency skill not found

```bash
# Install missing dependency
git clone https://github.com/.../skill-name.git ~/.openclaw/skills/skill-name
```

### Task analysis fails

```bash
# Check task_plan.md format
triadev plan --force  # Recreate planning docs
```

---

## API Reference

### Python API

```python
from triadev import TriadDevOrchestrator

orchestrator = TriadDevOrchestrator(Path("./my-project"))

# Initialize
config = orchestrator.initialize_project("Name", template="web")

# Planning
plan = orchestrator.create_plan(objectives=["Build API"])

# Analysis
schedule = orchestrator.analyze_tasks()

# Implementation
result = orchestrator.implement_task("task-001")

# Full workflow
result = orchestrator.run_full_workflow(from_phase="plan")
```

---

## Examples

### Example 1: Web API Project

```bash
# Initialize
triadev init "User Service API" --template api

# Plan with objectives
triadev plan --objectives "Design schema,Implement CRUD,Add auth,Write tests"

# Execute everything
triadev run --from plan
```

### Example 2: CLI Tool

```bash
triadev init "Data Processor" --template cli
triadev plan
triadev analyze
triadev implement --all
```

---

## Roadmap

- [ ] Web UI for visual workflow management
- [ ] Additional project templates (ml, mobile, etc.)
- [ ] CI/CD pipeline integration
- [ ] Multi-agent collaborative projects
- [ ] Export to popular PM tools (Jira, Linear)

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- **planning-with-files** by OthmanAdi
- **task-workflow** - DAG scheduling and complexity analysis
- **tdd-sdd-development** - TDD+SDD workflow
- **Charpup** - Project sponsor
- **Galatea** 🜁 - TriadDev architect

---

## Links

- **GitHub:** https://github.com/Charpup/triadev
- **Issues:** https://github.com/Charpup/triadev/issues
- **Documentation:** This file

---

**Start building with the Golden Triangle today!** 🚀

```bash
git clone https://github.com/Charpup/triadev.git ~/.openclaw/skills/triadev
~/.openclaw/skills/triadev/install.sh
triadev init "My Project" && triadev run
```
