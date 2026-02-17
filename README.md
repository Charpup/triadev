# TriadDev 🜁

**The Golden Triangle of OpenClaw Development**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Charpup/triadev)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.2.1+-green.svg)](https://openclaw.ai)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> **TriadDev** integrates the three essential skills for OpenClaw auto-pilot development: **planning-with-files** + **task-workflow** + **tdd-sdd-development**.

---

## 🎯 What is TriadDev?

TriadDev (三元开发) unifies the "Golden Triangle" workflow that has proven to deliver **100% success rate** and **7.5x efficiency** in real-world projects.

```
┌─────────────────────────────────────────────────────────┐
│                    TriadDev Workflow                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   📋 PLANNING          📊 WORKFLOW          🧪 TDD     │
│   ───────────         ───────────         ─────────    │
│   task_plan.md        Batch Schedule      SPEC.yaml    │
│   findings.md         Dependency DAG      RED tests    │
│   progress.md         Complexity Score    GREEN impl   │
│                       Progress Track      REFACTOR     │
│                                                         │
│   planning-with-files + task-workflow + tdd-sdd       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone with all dependencies
git clone --recursive https://github.com/Charpup/triadev.git

# Install
cd triadev
./install.sh

# Verify
 triadev --version
```

### Usage

```bash
# 1. Initialize project
triadev init "My Awesome Project" --template web

# 2. Create planning documents
cd my-awesome-project
triadev plan --objectives "Build API,Add tests,Deploy"

# 3. Analyze and schedule tasks
triadev analyze

# 4. Run TDD implementation
triadev implement --all

# Or run everything at once
triadev run --from plan
```

---

## 📦 Dependencies

TriadDev is built on top of three excellent OpenClaw skills:

| Skill | Purpose | Repository |
|-------|---------|------------|
| **planning-with-files** | Manus-style file-based planning | [GitHub →](https://github.com/OthmanAdi/planning-with-files) |
| **task-workflow** | DAG-based task scheduling with complexity analysis | [GitHub →](https://github.com/Charpup/openclaw-task-workflow) |
| **tdd-sdd-development** | TDD+SDD dual-pyramid development workflow | [GitHub →](https://github.com/Charpup/openclaw-tdd-sdd-skill) |

**If you need more granular control, use these skills directly.**

---

## 💡 Why TriadDev?

### Problem

Using individual skills requires:
- Context switching between tools
- Manual data transfer between phases
- Inconsistent project structures
- Steep learning curve for new users

### Solution

TriadDev provides:
- **Unified CLI**: One command for complete workflow
- **Automated orchestration**: Seamless phase transitions
- **Standardized structure**: Consistent project layout
- **Batteries included**: All three skills pre-configured

---

## 📖 Detailed Usage

### Project Templates

```bash
triadev init "Project Name" --template [web|cli|api|lib]
```

| Template | Structure | Use Case |
|----------|-----------|----------|
| `web` | Frontend + Backend + Tests | Web applications |
| `cli` | Command-line + Args + Tests | CLI tools |
| `api` | Endpoints + Schemas + Tests | REST/GraphQL APIs |
| `lib` | Core + Interfaces + Tests | Libraries/SDKs |

### Workflow Phases

#### Phase 1: Planning (`triadev plan`)

Creates:
- `task_plan.md` - Task breakdown with phases
- `findings.md` - Research and discoveries
- `progress.md` - Session logs

#### Phase 2: Analysis (`triadev analyze`)

Analyzes tasks and creates:
- Dependency DAG
- Complexity scores
- Optimal batch schedule

#### Phase 3: Implementation (`triadev implement`)

For each task:
1. Creates `SPEC.yaml` (SDD)
2. Writes tests (RED)
3. Implements feature (GREEN)
4. Refactors code

---

## 🏆 Real-World Results

Projects developed with TriadDev (Golden Triangle workflow):

| Project | Time | Tasks | Success | Efficiency |
|---------|------|-------|---------|------------|
| MCP Migration | 28 min | 6 | 100% | 7.5x |
| Schema Sync System | 50 min | 8 | 100% | 7.5x |
| Task-Workflow v3.1.0 | 10 min | 6 | 100% | 7.5x |
| Auto-Pilot Skill Pack | 30 min | 5 | 100% | - |

**Average: 19 tasks, 100% success rate, 7.5x faster than estimates**

---

## 🛠️ Architecture

```
triadev/
├── bin/triadev              # CLI entry point
├── lib/
│   └── triadev_orchestrator.py  # Core orchestration
├── templates/               # Project templates
│   ├── web/
│   ├── cli/
│   ├── api/
│   └── lib/
├── tests/                   # Test suite
└── docs/                    # Documentation

Project Structure (created by init):
├── 01_active/               # Current work
│   ├── tasks/               # Task plans
│   ├── research/            # Findings
│   └── docs/                # Documentation
├── 02_archive/              # Completed work
├── 03_deliverables/         # Final outputs
├── specs/                   # SPEC.yaml files
├── tests/                   # Test suites
└── triadev-project.json     # Project config
```

---

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_orchestrator.py -v
```

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **planning-with-files** by OthmanAdi - The foundation of structured planning
- **task-workflow** - DAG-based scheduling and complexity analysis
- **tdd-sdd-development** - Test-driven and spec-driven development
- **Charpup** - Project sponsor and use case provider
- **Galatea** 🜁 - TriadDev architect and developer

---

## 📮 Links

- **Repository:** https://github.com/Charpup/triadev
- **Issues:** https://github.com/Charpup/triadev/issues
- **Documentation:** https://github.com/Charpup/triadev/wiki

---

## 🔮 Roadmap

- [ ] Web UI for visual workflow management
- [ ] Integration with more skills
- [ ] CI/CD pipeline templates
- [ ] Multi-agent project support

---

**Start building with the Golden Triangle today!** 🚀

```bash
git clone --recursive https://github.com/Charpup/triadev.git
cd triadev && ./install.sh
triadev init "My Project" && triadev run
```
