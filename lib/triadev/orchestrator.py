"""
TriadDev Orchestrator - Core orchestration module
Integrates planning-with-files + task-workflow + tdd-sdd-development.
"""

import importlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PLANNING_TOOL = "planning-with-files"
WORKFLOW_TOOL = "task-workflow"
VALUE_GATE_TOOL = "value-first-gate"
TDD_TOOL = "tdd-sdd-development"

STACK_COMPONENTS = {
    "triadev": "triadev",
    "planning-with-files": "planning-with-files",
    "task-workflow": "task-workflow",
    "tdd-sdd-development": "tdd-sdd-skill",
    "value-first-gate": "value-first-gate",
}


@dataclass
class ProjectConfig:
    name: str
    path: Path
    template: str
    mode: str = "core"
    value_gate_mode: str = "advisory"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanningResult:
    success: bool
    task_plan_path: Path
    findings_path: Path
    progress_path: Path
    objectives: List[str] = field(default_factory=list)


@dataclass
class ScheduleResult:
    total_tasks: int
    total_batches: int
    batches: List[List[Dict[str, Any]]]


@dataclass
class ImplementationResult:
    task_id: str
    success: bool
    tests_total: int = 0
    tests_passed: int = 0
    spec_path: Optional[Path] = None


@dataclass
class WorkflowResult:
    success: bool
    phase_completed: str
    tasks_processed: int
    errors: List[str] = field(default_factory=list)
    artifacts_created: List[str] = field(default_factory=list)


@dataclass
class ProjectStatus:
    name: str
    current_phase: str
    route: str
    value_gate_mode: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    current_batch: int
    total_batches: int
    recent_activity: List[str] = field(default_factory=list)


class TriadDevOrchestrator:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "triadev-project.json"
        self.state_path = self.project_path / ".triadev" / "state.json"
        self.workflow_path = self.project_path / ".triadev" / "workflow.json"
        self.gate_audit_path = self.project_path / ".triadev" / "value-gate-audit.jsonl"
        self._route = "core"
        self._config: Optional[ProjectConfig] = None

    def _home_skill(self, skill_name: str) -> Path:
        codex = Path.home() / ".codex" / "skills" / skill_name
        if codex.exists():
            return codex
        openclaw = Path.home() / ".openclaw" / "skills" / skill_name
        if openclaw.exists():
            return openclaw
        return Path.home() / ".gemini" / "antigravity" / "skills" / skill_name

    def _stack_skill_path(self, repo_dir_name: str) -> Path:
        return Path.home() / ".openclaw" / "skills" / repo_dir_name

    def _read_manifest(self, repo_dir_name: str) -> Dict[str, Any]:
        manifest = self._stack_skill_path(repo_dir_name) / "contracts" / "stack-handshake.json"
        if not manifest.exists():
            return {"exists": False, "path": str(manifest)}
        try:
            return json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as err:
            return {"exists": True, "path": str(manifest), "error": str(err)}

    def _resolve_project(self):
        for candidate in [self.project_path, *list(self.project_path.parents)]:
            found = candidate / "triadev-project.json"
            if found.exists():
                self.project_path = candidate
                self.config_path = found
                self.state_path = candidate / ".triadev" / "state.json"
                self.workflow_path = candidate / ".triadev" / "workflow.json"
                self.gate_audit_path = candidate / ".triadev" / "value-gate-audit.jsonl"
                return

    def _load_config(self) -> Optional[ProjectConfig]:
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
            value_gate_mode=raw.get("value_gate_mode", "advisory"),
            created_at=datetime.fromisoformat(raw["created_at"]),
        )
        self._config = cfg
        self._route = cfg.mode
        return cfg

    def _save_config(self, cfg: ProjectConfig):
        payload = {
            "name": cfg.name,
            "template": cfg.template,
            "mode": cfg.mode,
            "value_gate_mode": cfg.value_gate_mode,
            "created_at": cfg.created_at.isoformat(),
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        self._config = cfg

    def _default_value_gate_state(self, mode: str = "advisory") -> Dict[str, Any]:
        return {
            "mode": mode,
            "state": "not_run",
            "verdict": None,
            "score": None,
            "confidence": None,
            "attempts": 0,
            "review_file": None,
            "last_checked_at": None,
            "last_bypass": None,
        }

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                if "value_gate" not in state:
                    state["value_gate"] = self._default_value_gate_state(mode="advisory")
                else:
                    state["value_gate"].setdefault("mode", "advisory")
                    state["value_gate"].setdefault("state", "not_run")
                    state["value_gate"].setdefault("attempts", 0)
                    state["value_gate"].setdefault("last_bypass", None)
                return state
            except Exception:
                pass
        return self._default_state()

    def _save_state(self, state: Dict[str, Any]):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = datetime.now().isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def _append_gate_audit(self, event: Dict[str, Any]):
        self.gate_audit_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"ts": datetime.now().isoformat(), **event}
        with open(self.gate_audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

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

    def set_value_gate_mode(self, mode: str):
        if mode not in {"disabled", "advisory", "enforced"}:
            raise RuntimeError(f"invalid gate mode: {mode}")
        cfg = self._ensure_config()
        cfg.value_gate_mode = mode
        self._save_config(cfg)
        state = self._load_state()
        state.setdefault("value_gate", self._default_value_gate_state(mode=mode))
        state["value_gate"]["mode"] = mode
        self._save_state(state)
        self._append_gate_audit({"event": "mode-change", "mode": mode})

    def _set_phase(self, phase: str):
        state = self._load_state()
        state["phase"] = phase
        state["last_phase"] = phase
        self._save_state(state)

    def _init_structure(self, project_dir: Path):
        (project_dir / "01_active" / "tasks").mkdir(parents=True, exist_ok=True)
        (project_dir / "01_active" / "research").mkdir(parents=True, exist_ok=True)
        (project_dir / "01_active" / "docs").mkdir(parents=True, exist_ok=True)
        (project_dir / "specs").mkdir(exist_ok=True)
        (project_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)
        (project_dir / "tests" / "integration").mkdir(exist_ok=True)
        (project_dir / "tests" / "acceptance").mkdir(exist_ok=True)
        (project_dir / ".triadev").mkdir(exist_ok=True)
        (project_dir / "artifacts" / "specs").mkdir(parents=True, exist_ok=True)
        (project_dir / "changes" / "active").mkdir(parents=True, exist_ok=True)
        (project_dir / "changes" / "archive").mkdir(parents=True, exist_ok=True)

    def _default_state(self) -> Dict[str, Any]:
        return {
            "route": self._route,
            "phase": "init",
            "value_gate": self._default_value_gate_state(mode="advisory"),
            "implemented_tasks": [],
            "workflow_built_at": None,
            "last_phase": None,
            "artifact_stage": "none",
            "brownfield": {"source_path": None, "base_spec_generated": False},
            "active_change_id": None,
            "artifact_change_id": None,
        }

    def initialize_project(self, name: str, template: str = "lib", route: str = "core") -> ProjectConfig:
        if Path(name).is_absolute():
            project_dir = Path(name)
        elif name in {"", ".", "./"}:
            project_dir = self.project_path
        else:
            project_dir = self.project_path / name

        project_dir.mkdir(parents=True, exist_ok=True)
        self.project_path = project_dir
        self.config_path = project_dir / "triadev-project.json"
        self.state_path = project_dir / ".triadev" / "state.json"
        self.workflow_path = project_dir / ".triadev" / "workflow.json"
        self.gate_audit_path = project_dir / ".triadev" / "value-gate-audit.jsonl"

        cfg = ProjectConfig(name=project_dir.name, path=project_dir, template=template, mode=route, value_gate_mode="advisory")
        self._route = route
        self._save_config(cfg)
        state = self._default_state()
        state["route"] = route
        state["value_gate"]["mode"] = "advisory"
        self._save_state(state)
        self._append_gate_audit({"event": "init", "mode": "advisory"})
        self._init_structure(project_dir)
        return cfg

    def init_brownfield_project(self, source_path: str, name: Optional[str] = None) -> ProjectConfig:
        project_dir = Path(source_path).expanduser().resolve()
        if not project_dir.exists():
            raise RuntimeError(f"source path not found: {source_path}")
        if not project_dir.is_dir():
            raise RuntimeError(f"source path is not a directory: {source_path}")

        self.project_path = project_dir
        self.config_path = project_dir / "triadev-project.json"
        self.state_path = project_dir / ".triadev" / "state.json"
        self.workflow_path = project_dir / ".triadev" / "workflow.json"
        self.gate_audit_path = project_dir / ".triadev" / "value-gate-audit.jsonl"

        cfg = ProjectConfig(name=name or project_dir.name, path=project_dir, template="brownfield", mode="extended", value_gate_mode="advisory")
        self._route = "extended"
        self._save_config(cfg)
        state = self._default_state()
        state["route"] = "extended"
        state["brownfield"]["source_path"] = str(project_dir)
        state["value_gate"]["mode"] = "advisory"
        self._save_state(state)
        self._append_gate_audit({"event": "init-brownfield", "mode": "advisory"})
        self._init_structure(project_dir)
        return cfg

    def _slug(self, text: str) -> str:
        base = re.sub(r"[^0-9a-zA-Z]+", "-", text.lower()).strip("-")
        return (base or "change")[:64]

    def _run_planning_script(self, cfg: ProjectConfig):
        skill = self._home_skill(PLANNING_TOOL)
        ps_script = skill / "scripts" / "init-session.ps1"
        sh_script = skill / "scripts" / "init-session.sh"

        if ps_script.exists():
            ps_exe = shutil.which("pwsh") or shutil.which("powershell")
            if ps_exe:
                subprocess.run(
                    [ps_exe, "-ExecutionPolicy", "Bypass", "-File", str(ps_script), cfg.name],
                    cwd=self.project_path,
                    check=False,
                )
                return

        if sh_script.exists():
            shell_exe = shutil.which("bash") or shutil.which("sh")
            if shell_exe:
                subprocess.run([shell_exe, str(sh_script), cfg.name], cwd=self.project_path, check=False)

    def create_plan(self, objectives: List[str] = None) -> PlanningResult:
        cfg = self._ensure_config()
        task_plan = self.project_path / "task_plan.md"
        findings = self.project_path / "findings.md"
        progress = self.project_path / "progress.md"

        self._run_planning_script(cfg)

        if not task_plan.exists():
            task_lines = "\n".join(f"- [ ] {o}" for o in (objectives or []))
            if task_lines:
                task_lines = "\n" + task_lines
            task_plan.write_text(
                "# Task Plan: " + cfg.name + "\n\n"
                + "**Created:** " + datetime.now().isoformat() + "\n"
                + "**Status:** In Progress\n"
                + "**Template:** " + cfg.template + "\n\n"
                + "## Objectives\n" + task_lines + "\n",
                encoding="utf-8",
            )
        if not findings.exists():
            findings.write_text("# Findings\n\n*Research findings go here*\n", encoding="utf-8")
        if not progress.exists():
            progress.write_text("# Progress Log\n\n- Phase 1: Planning\n", encoding="utf-8")

        self._set_phase("plan")
        return PlanningResult(True, task_plan, findings, progress, objectives or [])

    def _parse_plan_tasks(self, objective_override: List[str] = None) -> List[Dict[str, Any]]:
        path = self.project_path / "task_plan.md"
        if not path.exists():
            raise RuntimeError("No task_plan.md found. Run 'triadev plan' first.")

        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if objective_override:
            lines = [f"- [ ] {o}" for o in objective_override] + lines

        tasks: List[Dict[str, Any]] = []
        for line in lines:
            m = re.match(r"^\s*[-*]\s*\[[ xX]?\]\s*(.+)$", line)
            if not m:
                continue
            text = m.group(1).strip()
            if not text:
                continue
            depends = []
            dep_match = re.search(r"\(depends:\s*([^\)]+)\)", text, flags=re.I)
            if dep_match:
                depends = [x.strip() for x in dep_match.group(1).split(",") if x.strip()]
                text = text[: dep_match.start()].strip()
            tasks.append({"id": "task-%03d" % (len(tasks) + 1), "name": text, "depends_on": depends, "description": ""})

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

        batches = []
        wf_root = self._home_skill(WORKFLOW_TOOL)
        lib = wf_root / "lib"
        if lib.exists():
            try:
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
                for batch in batches_nodes:
                    bucket = []
                    for node in batch:
                        bucket.append({"id": node.id, "name": node.name, "depends_on": node.depends_on, "complexity": round(getattr(node, "complexity_score", 1.0), 2)})
                    batches.append(bucket)
            except Exception:
                batches = [[task] for task in tasks]
        else:
            batches = [[task] for task in tasks]

        payload = {
            "generated_at": datetime.now().isoformat(),
            "route": self._route,
            "tasks": [i for b in batches for i in b],
            "batches": [[i["id"] for i in b] for b in batches],
        }

        with open(self.workflow_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        state = self._load_state()
        state["workflow_built_at"] = payload["generated_at"]
        self._save_state(state)
        self._set_phase("workflow")
        return ScheduleResult(total_tasks=len(tasks), total_batches=len(batches), batches=batches)

    def _score_gate(self, plan_text: str, task_count: int, has_findings: bool) -> tuple:
        text = plan_text.lower()
        score = {
            "User Impact": 5 if any(x in text for x in ["user", "价值", "pain", "impact"]) else 3,
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
        state = self._load_state()
        mode = state.get("value_gate", {}).get("mode", "advisory")
        gate = state.get("value_gate", {})
        if gate.get("verdict") and not force:
            return {
                "success": gate.get("verdict") == "GO",
                "verdict": gate.get("verdict"),
                "score": gate.get("score"),
                "confidence": gate.get("confidence"),
                "review_file": gate.get("review_file"),
                "mode": mode,
                "cached": True,
            }

        task_plan = self.project_path / "task_plan.md"
        findings = self.project_path / "findings.md"
        plan_text = task_plan.read_text(encoding="utf-8", errors="ignore") if task_plan.exists() else ""
        tasks = self._parse_plan_tasks() if task_plan.exists() else []
        has_findings = findings.exists() and len(findings.read_text(encoding="utf-8", errors="ignore").strip()) > 20
        verdict, score, confidence = self._score_gate(plan_text=plan_text, task_count=len(tasks), has_findings=has_findings)

        review_file = self.project_path / "value-review.md"
        review_file.write_text(
            "# Value Gate Review\n\n"
            f"- Verdict: **{verdict}**\n"
            f"- Score: **{score}**\n"
            f"- Confidence: **{confidence}**\n"
            f"- Mode: **{mode}**\n"
            f"- Generated at: {datetime.now().isoformat()}\n",
            encoding="utf-8",
        )

        attempts = state.get("value_gate", {}).get("attempts", 0) + 1
        state["value_gate"] = {
            "mode": mode,
            "state": "passed" if verdict == "GO" else "reviewed",
            "verdict": verdict,
            "score": score,
            "confidence": confidence,
            "review_file": str(review_file),
            "attempts": attempts,
            "last_checked_at": datetime.now().isoformat(),
            "last_bypass": state.get("value_gate", {}).get("last_bypass"),
        }
        self._save_state(state)
        self._append_gate_audit({
            "event": "gate-evaluated",
            "mode": mode,
            "verdict": verdict,
            "score": score,
            "confidence": confidence,
            "attempt": attempts,
        })
        return {
            "success": verdict == "GO",
            "verdict": verdict,
            "score": score,
            "confidence": confidence,
            "review_file": str(review_file),
            "mode": mode,
            "cached": False,
        }

    def _ensure_gate(self, force_gate: bool, bypass_gate: bool = False, bypass_reason: str = "") -> bool:
        state = self._load_state()
        mode = state.get("value_gate", {}).get("mode", "advisory")

        if mode == "disabled":
            self._append_gate_audit({"event": "gate-skipped", "mode": mode, "reason": "mode_disabled"})
            return True

        gate = self.run_value_gate(force=force_gate)
        verdict = gate.get("verdict")

        if verdict == "GO":
            return True

        if mode == "advisory":
            self._append_gate_audit({"event": "gate-advisory-allow", "mode": mode, "verdict": verdict})
            return True

        # enforced
        if bypass_gate:
            reason = (bypass_reason or "").strip()
            if not reason:
                self._append_gate_audit({"event": "gate-enforced-bypass-denied", "mode": mode, "verdict": verdict, "reason": "missing_bypass_reason"})
                return False
            state = self._load_state()
            state["value_gate"]["last_bypass"] = {
                "at": datetime.now().isoformat(),
                "reason": reason,
                "verdict": verdict,
            }
            self._save_state(state)
            self._append_gate_audit({"event": "gate-enforced-bypass", "mode": mode, "verdict": verdict, "reason": reason})
            return True

        self._append_gate_audit({"event": "gate-enforced-block", "mode": mode, "verdict": verdict})
        return False

    def _touch_spec(self, task_id: str) -> Path:
        path = self.project_path / "specs" / f"{task_id}.yaml"
        if not path.exists():
            path.write_text(
                "name: " + task_id + "\n"
                "description: generated by triadev\n"
                "status: planned\n",
                encoding="utf-8",
            )
        return path

    def implement_task(self, task_id: str, force_gate: bool = False, bypass_gate: bool = False, bypass_reason: str = "") -> ImplementationResult:
        self._ensure_config()
        if not self._ensure_gate(force_gate=force_gate, bypass_gate=bypass_gate, bypass_reason=bypass_reason):
            return ImplementationResult(task_id=task_id, success=False)

        spec_path = self._touch_spec(task_id)
        runner = self._home_skill(TDD_TOOL) / "tools" / "run_tests.py"
        tests_total = 1 if any(self.project_path.glob("tests/**/*.py")) else 0
        tests_passed = 0
        if tests_total:
            if runner.exists():
                result = subprocess.run([sys.executable, str(runner), "all", "--quiet"], cwd=self.project_path, check=False)
                tests_passed = 1 if result.returncode == 0 else 0
            else:
                tests_passed = 1

        state = self._load_state()
        done = set(state.get("implemented_tasks", []))
        if tests_passed >= tests_total:
            done.add(task_id)
        state["implemented_tasks"] = sorted(done)
        self._save_state(state)
        self._set_phase("implement")

        return ImplementationResult(
            task_id=task_id,
            success=(tests_total == 0 or tests_passed >= tests_total),
            tests_total=tests_total,
            tests_passed=tests_passed,
            spec_path=spec_path,
        )

    def implement_all(self, force_gate: bool = False, bypass_gate: bool = False, bypass_reason: str = "") -> WorkflowResult:
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
            result = self.implement_task(task_id, force_gate=force_gate, bypass_gate=bypass_gate, bypass_reason=bypass_reason)
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
        vg = state.get("value_gate", {})
        return ProjectStatus(
            name=cfg.name,
            current_phase=state.get("phase", "planning"),
            route=state.get("route", self._route),
            value_gate_mode=vg.get("mode", cfg.value_gate_mode),
            total_tasks=total,
            completed_tasks=len(done),
            pending_tasks=max(0, total - len(done)),
            in_progress_tasks=0,
            current_batch=1 if payload.get("batches") else 0,
            total_batches=len(payload.get("batches", [])),
            recent_activity=[
                f"Gate mode: {vg.get('mode')}",
                f"Gate verdict: {vg.get('verdict')}",
                f"Route: {state.get('route')}",
                f"Brownfield base spec generated: {state.get('brownfield', {}).get('base_spec_generated')}",
                f"Active change: {state.get('active_change_id')}",
            ],
        )

    def _read_delta(self) -> Dict[str, Any]:
        path = self.project_path / "SPEC-delta.yaml"
        if not path.exists():
            return {"changes": []}
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data.setdefault("changes", [])
                return data
        except Exception:
            pass
        return {"changes": []}

    def _write_delta(self, payload: Dict[str, Any]):
        path = self.project_path / "SPEC-delta.yaml"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _read_spec(self) -> Dict[str, Any]:
        path = self.project_path / "SPEC.yaml"
        if not path.exists():
            return {"name": self._ensure_config().name, "features": [], "changes": [], "artifacts": []}
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data.setdefault("features", [])
                data.setdefault("changes", [])
                data.setdefault("artifacts", [])
                return data
        except Exception:
            pass
        return {"name": self._ensure_config().name, "features": [], "changes": [], "artifacts": [], "legacy_text": raw}

    def _write_spec(self, payload: Dict[str, Any]):
        path = self.project_path / "SPEC.yaml"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _scan_codebase(self) -> List[Dict[str, Any]]:
        ignore = {".git", ".triadev", "node_modules", ".venv", "vendor", "__pycache__"}
        stats: Dict[str, int] = {}
        for entry in self.project_path.rglob("*"):
            if not entry.is_file():
                continue
            rel_parts = set(entry.relative_to(self.project_path).parts[:-1])
            if rel_parts & ignore:
                continue
            ext = entry.suffix.lower() or ".noext"
            stats[ext] = stats.get(ext, 0) + 1

        features = [{"file_type": ext, "count": count} for ext, count in sorted(stats.items())]
        if not features:
            features.append({"file_type": "no-source", "count": 0})
        return features

    def detect_specs(self) -> Path:
        cfg = self._ensure_config()
        spec_payload = {
            "name": cfg.name,
            "mode": "brownfield",
            "generated_at": datetime.now().isoformat(),
            "features": self._scan_codebase(),
        }
        self._write_spec(spec_payload)

        state = self._load_state()
        state["brownfield"]["base_spec_generated"] = True
        state["brownfield"]["source_path"] = str(self.project_path)
        self._save_state(state)
        self._set_phase("detect-specs")
        return self.project_path / "SPEC.yaml"

    def build_delta(self, add: List[str], modify: List[str], remove: List[str], name: Optional[str] = None) -> Path:
        if not (add or modify or remove):
            raise RuntimeError("delta requires --add/--modify/--remove")
        cfg = self._ensure_config()
        change_id = name or (self._slug((add or modify or remove)[0]) + "-" + datetime.now().strftime("%Y%m%d%H%M%S"))
        entry = {
            "id": change_id,
            "project": cfg.name,
            "created_at": datetime.now().isoformat(),
            "add": add,
            "modify": modify,
            "remove": remove,
            "merged": False,
        }
        active_dir = self.project_path / "changes" / "active" / change_id
        active_dir.mkdir(parents=True, exist_ok=True)
        (active_dir / "meta.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")

        payload = self._read_delta()
        existing = [d for d in payload.get("changes", []) if d.get("id") != change_id]
        existing.append(entry)
        self._write_delta({"changes": existing})
        state = self._load_state()
        state["active_change_id"] = change_id
        self._save_state(state)
        return self.project_path / "SPEC-delta.yaml"

    def create_proposal(self, intent: str, scopes: List[str]) -> Path:
        path = self.project_path / "artifacts" / "proposal.md"
        lines = [f"- {s}" for s in scopes] if scopes else ["- in: define scope", "- out: define boundary"]
        path.write_text(
            "# Proposal\n\n"
            f"Intent: {intent}\n\n"
            "## Scope\n" + "\n".join(lines) + "\n\n"
            f"Created: {datetime.now().isoformat()}\n",
            encoding="utf-8",
        )
        state = self._load_state()
        state["artifact_stage"] = "proposal"
        state["artifact_change_id"] = self._slug(intent)
        self._save_state(state)
        return path

    def build_spec_from_proposal(self, from_proposal: bool = True) -> Path:
        proposal = self.project_path / "artifacts" / "proposal.md"
        if not proposal.exists():
            raise RuntimeError("No proposal found. Run 'triadev propose' first.")
        spec_file = self.project_path / "artifacts" / "specs" / f"{self._slug(proposal.stem)}-spec.yaml"
        spec_payload = {
            "id": self._slug(proposal.stem) + "-spec",
            "source": "proposal.md",
            "created_at": datetime.now().isoformat(),
            "status": "generated",
            "from_proposal": from_proposal,
        }
        spec_file.write_text(json.dumps(spec_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        spec_root = self._read_spec()
        spec_root.setdefault("artifacts", [])
        spec_root["artifacts"].append({"type": "spec", "file": str(spec_file.relative_to(self.project_path))})
        self._write_spec(spec_root)

        state = self._load_state()
        state["artifact_stage"] = "spec"
        self._save_state(state)
        return spec_file

    def build_design(self, approach: str) -> Path:
        proposal = self.project_path / "artifacts" / "proposal.md"
        if not proposal.exists():
            raise RuntimeError("No proposal found. Run 'triadev propose' first.")
        path = self.project_path / "artifacts" / "design.md"
        path.write_text(
            "# Design\n\n"
            f"Approach: {approach}\n"
            f"Based on: {proposal.as_posix()}\n"
            f"Created: {datetime.now().isoformat()}\n",
            encoding="utf-8",
        )
        state = self._load_state()
        state["artifact_stage"] = "design"
        self._save_state(state)
        return path

    def build_tasks(self) -> Path:
        tasks = self._parse_plan_tasks()
        path = self.project_path / "artifacts" / "tasks.md"
        lines = ["# Tasks", "", "| id | name | depends | status |", "|---|---|---|---|"]
        for item in tasks:
            deps = ", ".join(item["depends_on"]) if item["depends_on"] else "-"
            lines.append(f"| {item['id']} | {item['name']} | {deps} | not-started |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        state = self._load_state()
        state["artifact_stage"] = "tasks"
        self._save_state(state)
        return path

    def archive_change(self, name: Optional[str], force: bool = False) -> Path:
        cfg = self._ensure_config()
        state = self._load_state()
        change_name = name or state.get("active_change_id")
        if not change_name:
            raise RuntimeError("No active change to archive")

        active_dir = self.project_path / "changes" / "active" / change_name
        if not active_dir.exists():
            raise RuntimeError(f"No change directory found for '{change_name}'")

        archive_to = self.project_path / "changes" / "archive" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{change_name}"
        if force and archive_to.exists():
            shutil.rmtree(archive_to)
        shutil.move(str(active_dir), str(archive_to))

        self.sync_specs(from_all=True)
        if cfg.path and cfg.path.exists():
            state["active_change_id"] = None
            state["artifact_change_id"] = None
        self._save_state(state)
        return archive_to

    def sync_specs(self, from_delta: bool = False, from_all: bool = False) -> Dict[str, Any]:
        spec = self._read_spec()
        delta = self._read_delta()
        changes = delta.get("changes", [])

        merged = []
        skipped = []
        for item in changes:
            if item.get("merged") and not from_delta:
                skipped.append(item.get("id"))
                continue
            if not from_all and item.get("merged") and from_delta:
                skipped.append(item.get("id"))
                continue
            spec["changes"].append(item)
            item["merged"] = True
            merged.append(item.get("id"))

        spec["mode"] = spec.get("mode", "greenfield")
        spec["synced_at"] = datetime.now().isoformat()
        self._write_spec(spec)
        self._write_delta({"changes": changes})
        return {"merged": merged, "skipped": skipped, "total": len(changes)}

    def run_full_workflow(
        self,
        from_phase: str = "plan",
        force_gate: bool = False,
        bypass_gate: bool = False,
        bypass_reason: str = "",
    ) -> WorkflowResult:
        self._ensure_config()

        if from_phase == "analyze":
            from_phase = "workflow"

        core_order = ["plan", "workflow", "implement"]
        ext_order = ["plan", "detect-specs", "delta", "workflow", "value-gate", "implement", "sync"]
        if self._route == "core":
            order = core_order
        elif from_phase in {"artifact-propose", "spec", "design", "tasks"}:
            order = ["artifact-propose", "spec", "design", "tasks", "workflow", "value-gate", "implement", "sync"]
        else:
            order = ext_order

        if from_phase not in order:
            return WorkflowResult(False, "none", 0, [f"Unsupported start phase '{from_phase}' for route '{self._route}'"], [])

        idx = order.index(from_phase)
        done = []
        artifacts = []
        errors = []
        visited = set()

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

            if phase == "detect-specs":
                self.detect_specs()
                done.append("detect-specs")
                artifacts.append("SPEC.yaml")
                continue

            if phase == "delta":
                if self._load_state().get("active_change_id"):
                    done.append("delta")
                    artifacts.append("SPEC-delta.yaml")
                continue

            if phase == "artifact-propose":
                if (self.project_path / "artifacts" / "proposal.md").exists():
                    done.append("artifact-propose")
                continue

            if phase == "spec":
                if (self.project_path / "artifacts" / "proposal.md").exists():
                    self.build_spec_from_proposal(from_proposal=True)
                    done.append("spec")
                    artifacts.append("artifacts/specs")
                continue

            if phase == "design":
                design = self.project_path / "artifacts" / "design.md"
                if (self.project_path / "artifacts" / "proposal.md").exists() and not design.exists():
                    self.build_design("run-driven implementation plan")
                if design.exists():
                    done.append("design")
                    artifacts.append("artifacts/design.md")
                continue

            if phase == "tasks":
                task_file = self.project_path / "artifacts" / "tasks.md"
                if not task_file.exists():
                    self.build_tasks()
                done.append("tasks")
                artifacts.append("artifacts/tasks.md")
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
                done.append("value-gate")
                if gate.get("review_file"):
                    artifacts.append(gate["review_file"])
                if self._load_state().get("value_gate", {}).get("mode") == "enforced" and gate.get("verdict") in {"REVISE", "NO-GO"} and not bypass_gate:
                    errors.append(f"gate blocked: {gate['verdict']}")
                    break
                continue

            if phase == "implement":
                impl = self.implement_all(force_gate=force_gate, bypass_gate=bypass_gate, bypass_reason=bypass_reason)
                if not impl.success:
                    errors.extend(impl.errors)
                    break
                done.append("implement")
                artifacts.extend(impl.artifacts_created)
                continue

            if phase == "sync":
                self.sync_specs(from_all=True)
                done.append("sync")
                artifacts.append("SPEC.yaml")
                continue

        if errors:
            return WorkflowResult(False, done[-1] if done else "none", 0, errors, artifacts)
        return WorkflowResult(True, done[-1] if done else from_phase, 0, [], artifacts)

    def stack_health(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        for component, repo in STACK_COMPONENTS.items():
            base = self._stack_skill_path(repo)
            manifest = base / "contracts" / "stack-handshake.json"
            status = "ok" if base.exists() and manifest.exists() else "missing"
            checks.append({
                "component": component,
                "repo_path": str(base),
                "manifest": str(manifest),
                "status": status,
            })
        overall = "healthy" if all(c["status"] == "ok" for c in checks) else "degraded"
        return {"status": overall, "checks": checks, "checked_at": datetime.now().isoformat()}

    def stack_capabilities(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        for component, repo in STACK_COMPONENTS.items():
            payload[component] = self._read_manifest(repo)
        return payload

    def export_stack_state(self, output: Path) -> Path:
        state = self._load_state()
        cfg = self._ensure_config()
        export = {
            "exported_at": datetime.now().isoformat(),
            "project": {
                "path": str(self.project_path),
                "name": cfg.name,
                "route": cfg.mode,
                "value_gate_mode": cfg.value_gate_mode,
            },
            "triadev": {
                "state": state,
                "workflow": json.loads(self.workflow_path.read_text(encoding="utf-8")) if self.workflow_path.exists() else None,
                "status": {
                    "phase": state.get("phase"),
                    "implemented_tasks": state.get("implemented_tasks", []),
                },
            },
            "contracts": self.stack_capabilities(),
            "health": self.stack_health(),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
        return output

    def import_stack_state(self, input_file: Path):
        payload = json.loads(input_file.read_text(encoding="utf-8"))
        triadev = payload.get("triadev", {})
        state = triadev.get("state")
        if isinstance(state, dict):
            state.setdefault("value_gate", self._default_value_gate_state(mode="advisory"))
            self._save_state(state)
        workflow = triadev.get("workflow")
        if isinstance(workflow, dict):
            self.workflow_path.parent.mkdir(parents=True, exist_ok=True)
            self.workflow_path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False), encoding="utf-8")

    def state_snapshot(self) -> Dict[str, Any]:
        self._ensure_config()
        return self._load_state()
