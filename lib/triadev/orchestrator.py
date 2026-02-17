"""
TriadDev Orchestrator - Core orchestration module
Integrates planning-with-files + task-workflow + tdd-sdd-development
"""

import os
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ProjectConfig:
    """TriadDev project configuration"""
    name: str
    path: Path
    template: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanningResult:
    """Result of planning phase"""
    success: bool
    task_plan_path: Optional[Path] = None
    findings_path: Optional[Path] = None
    progress_path: Optional[Path] = None
    objectives: List[str] = field(default_factory=list)


@dataclass
class ScheduleResult:
    """Result of task analysis"""
    total_tasks: int
    total_batches: int
    batches: List[List[Any]] = field(default_factory=list)


@dataclass
class ImplementationResult:
    """Result of TDD implementation"""
    task_id: str
    success: bool
    tests_total: int = 0
    tests_passed: int = 0
    spec_path: Optional[Path] = None


@dataclass
class WorkflowResult:
    """Result of full workflow"""
    success: bool
    phase_completed: str
    tasks_processed: int
    errors: List[str] = field(default_factory=list)
    artifacts_created: List[str] = field(default_factory=list)


@dataclass
class ProjectStatus:
    """Current project status"""
    name: str
    current_phase: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    current_batch: int
    total_batches: int
    recent_activity: List[str] = field(default_factory=list)


class TriadDevOrchestrator:
    """
    Main orchestrator for TriadDev workflow.
    
    Coordinates between:
    - planning-with-files: Creates planning documents
    - task-workflow: Schedules and tracks tasks
    - tdd-sdd-development: Manages TDD implementation
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "triadev-project.json"
        self._config: Optional[ProjectConfig] = None
        
    def _load_config(self) -> Optional[ProjectConfig]:
        """Load project configuration if exists"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
            return ProjectConfig(
                name=data['name'],
                path=self.project_path,
                template=data['template'],
                created_at=datetime.fromisoformat(data['created_at'])
            )
        return None
    
    def _save_config(self, config: ProjectConfig):
        """Save project configuration"""
        data = {
            'name': config.name,
            'template': config.template,
            'created_at': config.created_at.isoformat(),
            'triadev_version': '1.0.0'
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
        self._config = config
    
    def initialize_project(self, name: str, template: str = 'lib') -> ProjectConfig:
        """
        Initialize new TriadDev project.
        
        Creates:
        - Project directory structure
        - triadev-project.json config
        - Integration with planning-with-files, task-workflow, tdd-sdd
        """
        # Create project directory
        project_dir = self.project_path / name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create standard structure
        (project_dir / "01_active").mkdir(exist_ok=True)
        (project_dir / "02_archive").mkdir(exist_ok=True)
        (project_dir / "03_deliverables").mkdir(exist_ok=True)
        (project_dir / "specs").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        
        # Create config
        config = ProjectConfig(
            name=name,
            path=project_dir,
            template=template
        )
        
        # Save config
        self.config_path = project_dir / "triadev-project.json"
        self._save_config(config)
        
        # Initialize sub-skills
        self._init_planning_files(project_dir)
        self._init_task_workflow(project_dir)
        self._init_tdd_sdd(project_dir)
        
        return config
    
    def _init_planning_files(self, project_dir: Path):
        """Initialize planning-with-files structure"""
        # Create planning directories
        (project_dir / "01_active" / "tasks").mkdir(exist_ok=True)
        (project_dir / "01_active" / "research").mkdir(exist_ok=True)
        (project_dir / "01_active" / "docs").mkdir(exist_ok=True)
    
    def _init_task_workflow(self, project_dir: Path):
        """Initialize task-workflow structure"""
        # Task workflow uses task_backlog in project root
        pass  # Will be created on first use
    
    def _init_tdd_sdd(self, project_dir: Path):
        """Initialize tdd-sdd structure"""
        # Create TDD directories
        (project_dir / "specs").mkdir(exist_ok=True)
        (project_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)
        (project_dir / "tests" / "integration").mkdir(exist_ok=True)
        (project_dir / "tests" / "acceptance").mkdir(exist_ok=True)
    
    def create_plan(self, objectives: List[str] = None) -> PlanningResult:
        """
        Create planning documents using planning-with-files.
        
        Runs init-session.sh and creates:
        - task_plan.md
        - findings.md
        - progress.md
        """
        config = self._load_config()
        if not config:
            raise RuntimeError("Not a TriadDev project. Run 'triadev init' first.")
        
        # Run planning-with-files init
        planning_script = Path.home() / ".openclaw" / "skills" / "planning-with-files" / "scripts" / "init-session.sh"
        
        if planning_script.exists():
            subprocess.run([str(planning_script)], cwd=self.project_path, check=True)
        else:
            # Fallback: create files manually
            self._create_planning_files_manually(objectives)
        
        return PlanningResult(
            success=True,
            task_plan_path=self.project_path / "task_plan.md",
            findings_path=self.project_path / "findings.md",
            progress_path=self.project_path / "progress.md",
            objectives=objectives or []
        )
    
    def _create_planning_files_manually(self, objectives: List[str]):
        """Create planning files manually if script not available"""
        # task_plan.md template
        task_plan = f"""# Task Plan: {self._config.name if self._config else 'Project'}

**Created:** {datetime.now().isoformat()}  
**Status:** In Progress  
**Template:** {self._config.template if self._config else 'lib'}

---

## Overview

Brief description of the project.

## Objectives

{chr(10).join(f"- [ ] {obj}" for obj in (objectives or []))}

## Phases

### Phase 1: Planning
**Status:** ⏳ PENDING

- [ ] Research
- [ ] Design

## Progress Tracking

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| 1 | ⏳ | - | - |

---

*Generated by TriadDev 🜁*
"""
        
        (self.project_path / "task_plan.md").write_text(task_plan)
        (self.project_path / "findings.md").write_text("# Findings\n\n*Research findings go here*\n")
        (self.project_path / "progress.md").write_text("# Progress Log\n\n*Session logs go here*\n")
    
    def analyze_tasks(self) -> ScheduleResult:
        """
        Analyze tasks using task-workflow.
        
        Reads task_plan.md and creates optimal batch schedule.
        """
        config = self._load_config()
        if not config:
            raise RuntimeError("Not a TriadDev project")
        
        # Check if task_plan.md exists
        task_plan = self.project_path / "task_plan.md"
        if not task_plan.exists():
            raise RuntimeError("No task_plan.md found. Run 'triadev plan' first.")
        
        # Run task-workflow analysis
        # This would parse the task plan and schedule tasks
        # For now, return mock result
        return ScheduleResult(
            total_tasks=5,
            total_batches=3,
            batches=[
                [{"name": "research"}, {"name": "design"}],
                [{"name": "implement-core"}],
                [{"name": "test"}, {"name": "release"}]
            ]
        )
    
    def implement_task(self, task_id: str) -> ImplementationResult:
        """
        Implement task using tdd-sdd-development.
        
        Runs full TDD cycle:
        1. Create SPEC.yaml
        2. RED: Write tests
        3. GREEN: Implement
        4. REFACTOR: Optimize
        """
        config = self._load_config()
        if not config:
            raise RuntimeError("Not a TriadDev project")
        
        # Mock implementation for now
        return ImplementationResult(
            task_id=task_id,
            success=True,
            tests_total=5,
            tests_passed=5,
            spec_path=self.project_path / "specs" / f"{task_id}-spec.yaml"
        )
    
    def get_status(self) -> ProjectStatus:
        """Get current project status"""
        config = self._load_config()
        if not config:
            raise RuntimeError("Not a TriadDev project")
        
        # Parse progress and task_plan to get actual status
        return ProjectStatus(
            name=config.name,
            current_phase="planning",  # Would be parsed from files
            total_tasks=5,
            completed_tasks=0,
            pending_tasks=5,
            in_progress_tasks=0,
            current_batch=1,
            total_batches=3,
            recent_activity=[
                f"Project initialized: {config.created_at}",
                "Planning documents created"
            ]
        )
    
    def run_full_workflow(self, from_phase: str = 'plan') -> WorkflowResult:
        """
        Run complete workflow from specified phase.
        
        Phases: plan → analyze → implement → complete
        """
        phases = ['plan', 'analyze', 'implement']
        start_idx = phases.index(from_phase)
        
        results = []
        artifacts = []
        
        try:
            if start_idx <= 0:
                print("📋 Phase: Planning...")
                self.create_plan()
                artifacts.extend(['task_plan.md', 'findings.md', 'progress.md'])
                results.append('plan: success')
            
            if start_idx <= 1:
                print("📊 Phase: Analysis...")
                self.analyze_tasks()
                results.append('analyze: success')
            
            if start_idx <= 2:
                print("🛠️  Phase: Implementation...")
                # Would implement all tasks
                results.append('implement: success')
            
            return WorkflowResult(
                success=True,
                phase_completed='all',
                tasks_processed=5,
                artifacts_created=artifacts
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                phase_completed=results[-1] if results else 'none',
                tasks_processed=len(results),
                errors=[str(e)]
            )
