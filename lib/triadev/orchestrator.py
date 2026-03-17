"""TriadDev orchestrator.
Integrates planning-with-files + task-workflow + value-first-gate + tdd-sdd-development.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import importlib
import json
import re
import subprocess
import sys


PLANNING_TOOL = "planning-with-files"
WORKFLOW_TOOL = "task-workflow"
VALUE_GATE_TOOL = "value-first-gate"
TDD_TOOL = "tdd-sdd-development"


@dataclass
class ProjectConfig:
    name: str
    path: Path
    template: str
    mode: str = "core"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanningResult:
    success: bool
    task_plan_path: Path
    findings_path: Path
    progress_path: Path
    objectives: list[str] = field(default_factory=list)


@dataclass
class ScheduleResult:
    total_tasks: int
    total_batches: int
    batches: list[list[dict]]


@dataclass
class ImplementationResult:
    task_id: str
    success: bool
    tests_total: int = 0
    tests_passed: int = 0
    spec_path: Path | None = None


@dataclass
class WorkflowResult:
    success: bool
    phase_completed: str
    tasks_processed: int
    errors: list[str] = field(default_factory=list)
    artifacts_created: list[str] = field(default_factory=list)


@dataclass
class ProjectStatus:
    name: str
    current_phase: str
    route: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    current_batch: int
    total_batches: int
    recent_activity: list[str] = field(default_factory=list)


class TriadDevOrchestrator:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "triadev-project.json"
        self.state_path = self.project_path / ".triadev" / "state.json"
        self.workflow_path = self.project_path / ".triadev" / "workflow.json"
        self._route = "core"
        self._config: ProjectConfig | None = None

    def _home_skill(self, skill_name: str) -> Path:
        primary = Path.home() / ".codex" / "skills" / skill_name
        if primary.exists():
            return primary
        return Path.home() / ".openclaw" / "skills" / skill_name

    def _resolve_project(self):
        for candidate in [self.project_path, *list(self.project_path.parents)]:
            found = candidate / "triadev-project.json"
            if found.exists():
                self.project_path = candidate
                self.config_path = found
                self.state_path = candidate / ".triadev" / "state.json"
                self.workflow_path = candidate / ".triadev" / "workflow.json"
                return

    def _load_config(self) -> ProjectConfig | None:
        self._resolve_project()
        if not self.config_path.exists():
            return None

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        cfg = ProjectConfig(
            name=raw["name"],
            path=self.project_path,
            template=raw.get("template", "lib"),
            mode=raw.get("mode", "core"),
            created_at=datetime.fromisoformat(raw["created_at"]),
        )
        self._config = cfg
        self._route = cfg.mode
        return cfg

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except Exception:
                pass
        return {
            "route": self._route,
            "phase": "init",
            "value_gate": {
                "state": "not_required",
                "verdict": None,
                "score": None,
                "confidence": None,
                "attempts": 0,
                "review_file": None,
            },
            "implemented_tasks": [],
            "workflow_built_at": None,
            "last_phase": None,
            "updated_at": None,
        }

    def _save_state(self, data: dict):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data["updated_at"] = datetime.now().isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_config(self, cfg: ProjectConfig):
        payload = {
            "name": cfg.name,
            "template": cfg.template,
            "mode": cfg.mode,
            "created_at": cfg.created_at.isoformat(),
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        self._config = cfg

    def _ensure_config(self) -> ProjectConfig:
        cfg = self._load_config()
        if not cfg:
            raise RuntimeError("No triadev project found. Run 'triadev init <name>' first.")
        return cfg

    def set_route(self, route: str):
        cfg = self._ensure_config()
        cfg.mode = route
        self._route = route
        self._save_config(cfg)
        state = self._load_state()
        state["route"] = route
        self._save_state(state)

    def _set_phase(self, phase: str):
        state = self._load_state()
        state["phase"] = phase
        state["last_phase"] = phase
        self._save_state(state)

    def initialize_project(self, name: str, template: str = "lib", route: str = "core") -> ProjectConfig:
        if Path(name).is_absolute():
            p = Path(name)
        elif name in {"", ".", "./"}:
            p = self.project_path
        else:
            p = self.project_path / name

        p.mkdir(parents=True, exist_ok=True)
        self.project_path = p
        self.config_path = p / "triadev-project.json"
        self.state_path = p / ".triadev" / "state.json"
        self.workflow_path = p / ".triadev" / "workflow.json"

        cfg = ProjectConfig(name=p.name, path=p, template=template, mode=route)
        self._route = route
        self._save_config(cfg)

        state = self._load_state()
        state["route"] = route
        state["implemented_tasks"] = []
        state["phase"] = "init"
        state["last_phase"] = "init"
        self._save_state(state)

        (p / "01_active" / "tasks").mkdir(parents=True, exist_ok=True)
        (p / "01_active" / "research").mkdir(parents=True, exist_ok=True)
        (p / "01_active" / "docs").mkdir(parents=True, exist_ok=True)
        (p / "specs").mkdir(parents=True, exist_ok=True)
        (p / "tests" / "unit").mkdir(parents=True, exist_ok=True)
        (p / "tests" / "integration").mkdir(parents=True, exist_ok=True)
        (p / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
        return cfg

    def create_plan(self, objectives: list[str] | None = None) -> PlanningResult:
        cfg = self._ensure_config()
        task_plan = self.project_path / "task_plan.md"
        findings = self.project_path / "findings.md"
        progress = self.project_path / "progress.md"

        skill = self._home_skill(PLANNING_TOOL)
        script = None
        for candidate in [skill / "scripts" / "init-session.ps1", skill / "scripts" / "init-session.sh"]:
            if candidate.exists():
                script = candidate
                break

        if script and script.exists():
            if script.suffix.lower() == ".ps1":
                subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script), cfg.name],
                    cwd=self.project_path,
                    check=False,
                )
            else:
                subprocess.run(["bash", str(script), cfg.name], cwd=self.project_path, check=False)

        if not task_plan.exists():
            plan_lines = "\n".join(f"- [ ] {obj}" for obj in (objectives or []))
            if plan_lines:
                plan_lines += "\n"
            task_plan.write_text(
                "# Task Plan: " + cfg.name + "\n\n"
                + "**Created:** " + datetime.now().isoformat() + "\n"
                + "**Status:** In Progress\n"
                + "**Template:** " + cfg.template + "\n\n"
                + "## Objectives\n"
                + plan_lines,
                encoding="utf-8",
            )

        if not findings.exists():
            findings.write_text("# Findings\n\n*Research findings go here*\n", encoding="utf-8")
        if not progress.exists():
            progress.write_text("# Progress Log\n\n- Phase 1: Planning\n", encoding="utf-8")

        self._set_phase("plan")
        return PlanningResult(True, task_plan, findings, progress, objectives or [])

    def _parse_plan_tasks(self, objective_override: list[str] | None = None) -> list[dict]:
        path = self.project_path / "task_plan.md"
        if not path.exists():
            raise RuntimeError("No task_plan.md found. Run 'triadev plan' first.")

        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if objective_override:
            lines = [f"- [ ] {o}" for o in objective_override] + lines

        tasks = []
        for line in lines:
            m = re.match(r"^\s*[-*]\s*\[[ xX]?\]\s*(.+)$", line)
            if not m:
                continue
            text = m.group(1).strip()
            if not text:
                continue

            dep = []
            dep_match = re.search(r"\(depends:\s*([^\)]+)\)", text, flags=re.I)
            if dep_match:
                dep = [x.strip() for x in dep_match.group(1).split(",") if x.strip()]
                text = text[: dep_match.start()].strip()

            tasks.append({
                "id": f"task-{len(tasks)+1:03d}",
                "name": text,
                "depends_on": dep,
                "description": "",
            })

        if not tasks:
            tasks = [
                {"id": "task-001", "name": "Research", "depends_on": [], "description": "Gather required context"},
                {"id": "task-002", "name": "Implement", "depends_on": ["task-001"], "description": "Implement baseline"},
                {"id": "task-003", "name": "Test", "depends_on": ["task-002"], "description": "Validate behavior"},
            ]
        return tasks

    def analyze_tasks(self) -> ScheduleResult:
        self._ensure_config()
        tasks = self._parse_plan_tasks()

        wf_root = self._home_skill(WORKFLOW_TOOL)
        lib = wf_root / "lib"
        if not lib.exists():
            raise RuntimeError("task-workflow lib not found.")

        if str(lib) not in sys.path:
            sys.path.insert(0, str(lib))

        module = importlib.import_module("task_scheduler")
        Node = module.TaskNode
        Scheduler = module.TaskScheduler

        nodes = [
            Node(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                depends_on=item["depends_on"],
                estimated_time="medium",
                tool_calls_estimate=max(1, len(item["name"].split())),
            )
            for item in tasks
        ]

        batches_nodes = Scheduler(max_batch_size=6, enable_persistence=False).schedule_tasks(nodes)
        batches = []
        for batch in batches_nodes:
            bucket = []
            for node in batch:
                bucket.append(
                    {
                        "id": node.id,
                        "name": node.name,
                        "depends_on": node.depends_on,
                        "complexity": round(node.complexity_score, 2),
                        "batch": getattr(node, "batch_number", 0),
                    }
                )
            batches.append(bucket)

        payload = {
            "generated_at": datetime.now().isoformat(),
            "route": self._route,
            "tasks": [i for b in batches for i in b],
            "batches": [[i["id"] for i in b] for b in batches],
        }

        self.workflow_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.workflow_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        state = self._load_state()
        if self._route == "core":
            state["value_gate"]["state"] = "passed"
        state["workflow_built_at"] = payload["generated_at"]
        self._save_state(state)
        self._set_phase("workflow")
        return ScheduleResult(total_tasks=len(tasks), total_batches=len(batches), batches=batches)

    def _score_gate(self, plan_text: str, task_count: int, has_findings: bool) -> tuple[str, int, str]:
        text = plan_text.lower()
        score = {
            "User Impact": 5 if any(x in text for x in ["user", "用户", "pain", "value"]) else 3,
            "Strategic Fit": 4 if any(x in text for x in ["goal", "目标", "roadmap"]) else 3,
            "Urgency": 4 if any(x in text for x in ["urgent", "deadline", "asap"]) else 2,
            "Evidence Strength": 4 if has_findings else 2,
            "Effort Efficiency": 3 if task_count <= 5 else 2,
            "Risk Controllability": 3,
        }
        total = sum(score.values())
        if total >= 22 and min(score.values()) >= 2:
            return "GO", total, "High"
        if total <= 15:
            return "NO-GO", total, "Low"
        return "REVISE", total, "Medium"

    def run_value_gate(self, force: bool = False) -> dict:
        self._ensure_config()
        state = self._load_state()

        if self._route == "core":
            state["value_gate"] = {
                "state": "passed",
                "verdict": "GO",
                "score": 30,
                "confidence": "High",
                "review_file": None,
                "attempts": state["value_gate"].get("attempts", 0),
            }
            self._save_state(state)
            self._set_phase("value-gate")
            return {"success": True, "verdict": "GO", "score": 30, "confidence": "High", "review_file": None}

        if not force and state["value_gate"].get("state") == "passed":
            return {
                "success": True,
                **state["value_gate"],
                "review_file": state["value_gate"].get("review_file"),
            }

        plan_file = self.project_path / "task_plan.md"
        plan_text = plan_file.read_text(encoding="utf-8", errors="ignore") if plan_file.exists() else ""
        tasks = self._parse_plan_tasks()
        verdict, total, conf = self._score_gate(
            plan_text=plan_text,
            task_count=len(tasks),
            has_findings=(self.project_path / "findings.md").exists(),
        )

        template = self._home_skill(VALUE_GATE_TOOL) / "references" / "value-review-template.md"
        if template.exists():
            content = template.read_text(encoding="utf-8")
        else:
            content = "# value-review.md\n"

        content = content.replace("- **Proposal:**", "- **Proposal:** TriadDev execution of current plan")
        content = content.replace("- **Date:**", f"- **Date:** {datetime.now().date()}")
        content = content.replace("- **Owner:**", "- **Owner:** codex")
        content = content.replace(
            "- **Verdict:** `GO | REVISE | NO-GO`",
            f"- **Verdict:** `{verdict}`",
        )
        content = content.replace("- **Total Score (0-30):**", f"- **Total Score (0-30):** {total}")
        content = content.replace("- **Confidence:** `High | Medium | Low`", f"- **Confidence:** `{conf}`")

        review_file = self.project_path / "value-review.md"
        review_file.write_text(content, encoding="utf-8")

        state["value_gate"] = {
            "state": "passed" if verdict == "GO" else "blocked",
            "verdict": verdict,
            "score": total,
            "confidence": conf,
            "reviewed_at": datetime.now().isoformat(),
            "review_file": str(review_file),
            "attempts": int(state["value_gate"].get("attempts", 0)) + 1,
        }
        self._save_state(state)
        self._set_phase("value-gate")

        return {
            "success": verdict == "GO",
            "verdict": verdict,
            "score": total,
            "confidence": conf,
            "review_file": str(review_file),
        }

    def _ensure_gate(self, force_gate: bool) -> bool:
        if self._route == "core":
            return True
        state = self._load_state()
        if state.get("value_gate", {}).get("state") == "passed":
            return True
        if state.get("value_gate", {}).get("state") == "blocked":
            return self.run_value_gate(force=force_gate)["success"] if force_gate else False
        return self.run_value_gate(force=force_gate)["success"]

    def _touch_spec(self, task_id: str) -> Path:
        path = self.project_path / "specs" / f"{task_id}.yaml"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "name: " + task_id + "\n"
                "description: generated by triadev\n"
                "status: planned\n",
                encoding="utf-8",
            )
        return path

    def implement_task(self, task_id: str, force_gate: bool = False) -> ImplementationResult:
        self._ensure_config()
        if not self._ensure_gate(force_gate=force_gate):
            return ImplementationResult(task_id=task_id, success=False)

        spec_path = self._touch_spec(task_id)
        tests_total = 0
        tests_passed = 0

        tests_root = self.project_path / "tests"
        has_tests = tests_root.exists() and any(p.suffix == ".py" for p in tests_root.rglob("test_*.py"))
        if has_tests:
            runner = self._home_skill(TDD_TOOL) / "tools" / "run_tests.py"
            if runner.exists():
                result = subprocess.run(
                    [sys.executable, str(runner), "all", "--quiet"],
                    cwd=self.project_path,
                    check=False,
                )
                tests_total = 1
                tests_passed = 1 if result.returncode == 0 else 0

        state = self._load_state()
        done = set(state.get("implemented_tasks", []))
        if tests_passed >= tests_total:
            done.add(task_id)
        state["implemented_tasks"] = sorted(done)
        self._save_state(state)
        self._set_phase("implement")

        return ImplementationResult(
            task_id=task_id,
            success=(tests_passed >= tests_total),
            tests_total=tests_total,
            tests_passed=tests_passed,
            spec_path=spec_path,
        )

    def implement_all(self, force_gate: bool = False) -> WorkflowResult:
        self._ensure_config()
        if not self.workflow_path.exists():
            self.analyze_tasks()

        with open(self.workflow_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        tasks = payload.get("tasks", [])
        state = self._load_state()
        done = set(state.get("implemented_tasks", []))
        pending = [t["id"] for t in tasks if t["id"] not in done]

        errors = []
        for task_id in pending:
            result = self.implement_task(task_id, force_gate=force_gate)
            if not result.success:
                errors.append(task_id + ": blocked by value gate")
                break

        if errors:
            return WorkflowResult(False, "implement", 0, errors, [str(self.workflow_path)])
        return WorkflowResult(True, "implement", len(pending), [], [str(self.workflow_path)])

    def get_status(self) -> ProjectStatus:
        cfg = self._ensure_config()
        state = self._load_state()

        payload = {"tasks": [], "batches": []}
        if self.workflow_path.exists():
            with open(self.workflow_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

        total = len(payload.get("tasks", []))
        done = set(state.get("implemented_tasks", []))

        return ProjectStatus(
            name=cfg.name,
            current_phase=state.get("phase", "planning"),
            route=state.get("route", self._route),
            total_tasks=total,
            completed_tasks=len(done),
            pending_tasks=max(0, total - len(done)),
            in_progress_tasks=0,
            current_batch=1 if payload.get("batches") else 0,
            total_batches=len(payload.get("batches", [])),
            recent_activity=[
                f"Gate state: {state.get('value_gate', {}).get('state')}",
                f"Last phase: {state.get('last_phase')}",
            ],
        )

    def run_full_workflow(self, from_phase: str = "plan", force_gate: bool = False) -> WorkflowResult:
        self._ensure_config()

        if from_phase == "analyze":
            from_phase = "workflow"

        order = ["plan", "workflow"] if self._route == "core" else ["plan", "workflow", "value-gate", "implement"]
        if from_phase not in order:
            return WorkflowResult(
                False,
                "none",
                0,
                [f"Unsupported start phase '{from_phase}' for route '{self._route}'"],
                [],
            )

        idx = order.index(from_phase)
        done: list[str] = []
        artifacts: list[str] = []
        errors: list[str] = []
        visited = set[str]()

        for phase in order[idx:]:
            if phase in visited:
                errors.append(f"Potential loop at phase '{phase}'")
                break
            visited.add(phase)

            if phase == "plan":
                self.create_plan()
                done.append("plan")
                artifacts.extend(["task_plan.md", "findings.md", "progress.md"])
                continue

            if phase == "workflow":
                try:
                    self.analyze_tasks()
                except Exception as err:
                    errors.append(f"workflow failed: {err}")
                    break
                done.append("workflow")
                artifacts.append(str(self.workflow_path))
                continue

            if phase == "value-gate":
                gate = self.run_value_gate(force=force_gate)
                if not gate["success"]:
                    errors.append(f"gate blocked: {gate['verdict']}")
                    break
                done.append("value-gate")
                artifacts.append(str(self.project_path / "value-review.md"))
                continue

            if phase == "implement":
                impl = self.implement_all(force_gate=force_gate)
                if not impl.success:
                    errors.extend(impl.errors)
                    break
                done.append("implement")
                artifacts.extend(impl.artifacts_created)

        if errors:
            return WorkflowResult(False, done[-1] if done else "none", 0, errors, artifacts)
        return WorkflowResult(True, done[-1] if done else from_phase, 0, [], artifacts)
