import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from triadev.orchestrator import TriadDevOrchestrator


def _seed_low_value_plan(project_dir: Path):
    # 6 tasks + low-signal text => NO-GO in current scoring model
    lines = ["# Task Plan", ""]
    for i in range(1, 7):
        lines.append(f"- [ ] neutral task {i}")
    (project_dir / "task_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (project_dir / "findings.md").write_text("# Findings\n\n", encoding="utf-8")
    (project_dir / "progress.md").write_text("# Progress\n\n", encoding="utf-8")


def test_stack_handshake_health_and_capabilities(tmp_path: Path):
    orchestrator = TriadDevOrchestrator(tmp_path)
    orchestrator.initialize_project("demo", template="lib", route="extended")

    health = orchestrator.stack_health()
    assert "status" in health
    assert "checks" in health
    assert len(health["checks"]) >= 5

    caps = orchestrator.stack_capabilities()
    assert "triadev" in caps
    assert "planning-with-files" in caps


def test_value_gate_mode_advisory_allows_no_go(tmp_path: Path):
    orchestrator = TriadDevOrchestrator(tmp_path)
    project = tmp_path / "demo"
    orchestrator.initialize_project("demo", template="lib", route="extended")
    _seed_low_value_plan(project)

    # Build workflow tasks for implement_all
    orchestrator.analyze_tasks()
    orchestrator.set_value_gate_mode("advisory")
    result = orchestrator.implement_all(force_gate=True)

    assert result.success is True

    state = orchestrator.state_snapshot()
    assert state["value_gate"]["mode"] == "advisory"
    assert state["value_gate"]["verdict"] in {"REVISE", "NO-GO"}


def test_value_gate_mode_enforced_blocks_without_bypass(tmp_path: Path):
    orchestrator = TriadDevOrchestrator(tmp_path)
    project = tmp_path / "demo"
    orchestrator.initialize_project("demo", template="lib", route="extended")
    _seed_low_value_plan(project)

    orchestrator.analyze_tasks()
    orchestrator.set_value_gate_mode("enforced")
    blocked = orchestrator.implement_all(force_gate=True)
    assert blocked.success is False

    allowed = orchestrator.implement_all(force_gate=True, bypass_gate=True, bypass_reason="risk accepted for integration test")
    assert allowed.success is True

    audit = (project / ".triadev" / "value-gate-audit.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(line)["event"] for line in audit if line.strip()]
    assert "gate-enforced-block" in events
    assert "gate-enforced-bypass" in events


def test_export_import_stack_state_roundtrip(tmp_path: Path):
    orchestrator = TriadDevOrchestrator(tmp_path)
    project = tmp_path / "demo"
    orchestrator.initialize_project("demo", template="lib", route="extended")
    _seed_low_value_plan(project)
    orchestrator.analyze_tasks()

    out = project / "stack-state.json"
    orchestrator.export_stack_state(out)
    assert out.exists()

    payload = json.loads(out.read_text(encoding="utf-8"))
    payload["triadev"]["state"]["phase"] = "imported-phase"
    modified = project / "stack-state-mod.json"
    modified.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    orchestrator.import_stack_state(modified)
    state = orchestrator.state_snapshot()
    assert state["phase"] == "imported-phase"
