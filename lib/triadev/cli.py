#!/usr/bin/env python3
"""
TriadDev CLI - Command Line Interface
Golden Triangle Development Workflow
"""

import argparse
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from triadev import TriadDevOrchestrator, __version__


def main():
    parser = argparse.ArgumentParser(
        description='TriadDev - Golden Triangle Development Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    triadev init "My Project" --template web
    triadev plan --route extended
    triadev workflow
    triadev run --from plan --route extended
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'triadev {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--template', choices=['web', 'cli', 'api', 'lib'], 
                            default='lib', help='Project template')
    init_parser.add_argument('--route', choices=['core', 'extended'], default='core',
                            help='Default workflow route for this project')
    
    # plan command
    plan_parser = subparsers.add_parser('plan', help='Create planning documents')
    plan_parser.add_argument('--objectives', help='Comma-separated objectives')
    plan_parser.add_argument('--route', choices=['core', 'extended'], default='core',
                            help='Route intent for downstream implementation control')
    
    # analyze command (legacy name)
    analyze_parser = subparsers.add_parser('analyze', help='Analyze tasks and schedule')
    analyze_parser.set_defaults(phase='workflow')
    
    # workflow command (explicit, clear route)
    workflow_parser = subparsers.add_parser('workflow', help='Analyze and schedule tasks')
    workflow_parser.set_defaults(phase='workflow')
    
    # value-gate command
    gate_parser = subparsers.add_parser('value-gate', help='Run value-first gate review')
    gate_parser.add_argument('--force', action='store_true',
                            help='Regenerate review file and re-evaluate')
    
    # implement command
    impl_parser = subparsers.add_parser('implement', help='Run TDD workflow')
    impl_parser.add_argument('task_id', nargs='?', help='Task ID')
    impl_parser.add_argument('--all', action='store_true', help='All pending tasks')
    impl_parser.add_argument('--route', choices=['core', 'extended'], default='extended',
                            help='Implementation requires Extended route')
    impl_parser.add_argument('--force-gate', action='store_true',
                            help='Force regenerate gate review first when blocked/revised')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('--verbose', '-v', action='store_true')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Execute full workflow')
    run_parser.add_argument('--from', dest='from_phase', 
                           choices=['plan', 'workflow', 'value-gate', 'implement'],
                           default='plan')
    run_parser.add_argument('--route', choices=['core', 'extended'], default='extended',
                            help='Execution route (core only runs plan+workflow)')
    run_parser.add_argument('--force-gate', action='store_true',
                            help='Regenerate gate review if block/revise')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute
    try:
        if args.command == 'init':
            return cmd_init(args)
        elif args.command == 'plan':
            return cmd_plan(args)
        elif args.command in {'analyze', 'workflow'}:
            return cmd_workflow(args)
        elif args.command == 'value-gate':
            return cmd_value_gate(args)
        elif args.command == 'implement':
            return cmd_implement(args)
        elif args.command == 'status':
            return cmd_status(args)
        elif args.command == 'run':
            return cmd_run(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_init(args):
    """Initialize project"""
    print(f"[TriadDev] Initializing: {args.name}")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    config = orchestrator.initialize_project(args.name, args.template, route=args.route)
    
    print(f"Created: {config.name}")
    print(f"   Template: {config.template}")
    print(f"   Path: {config.path}")
    print(f"   Route: {config.mode}")
    print("\nNext: cd into directory and run 'triadev plan'")
    return 0


def cmd_plan(args):
    """Create planning"""
    print("[TriadDev] Creating planning documents...")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route)
    objectives = [o.strip() for o in args.objectives.split(',')] if args.objectives else []
    result = orchestrator.create_plan(objectives)
    
    if result.success:
        print("Planning complete")
        print("   - task_plan.md")
        print("   - findings.md") 
        print("   - progress.md")
    return 0


def cmd_workflow(args):
    """Analyze tasks"""
    print("[TriadDev] Analyzing workflow tasks...")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.analyze_tasks()
    
    print(f"Analysis: {result.total_tasks} tasks, {result.total_batches} batches")
    for idx, batch in enumerate(result.batches, 1):
        batch_ids = ", ".join(t["id"] for t in batch) if batch else "-"
        print(f"   Batch {idx}: {batch_ids}")
    return 0


def cmd_value_gate(args):
    """Run value-first gate"""
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.run_value_gate(force=args.force)
    if result["success"]:
        print(f"Value gate passed: {result['verdict']} (score={result['score']}, confidence={result['confidence']})")
        return 0
    print(f"Value gate blocked: {result['verdict']} (score={result['score']}, confidence={result['confidence']})")
    return 1


def cmd_implement(args):
    """Implement tasks"""
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route)
    
    if args.all:
        print("Implementing all tasks...")
        result = orchestrator.implement_all(force_gate=args.force_gate)
        if result.success:
            print(f"Implemented {result.tasks_processed} tasks")
        else:
            print("Some tasks blocked:")
            for item in result.errors:
                print(f"  - {item}")
            return 1
    elif args.task_id:
        print(f"Implementing {args.task_id}...")
        result = orchestrator.implement_task(args.task_id, force_gate=args.force_gate)
        print(f"{args.task_id}: {result.tests_passed}/{result.tests_total} tests")
    else:
        print("Specify task-id or --all")
        return 1
    return 0


def cmd_status(args):
    """Show status"""
    orchestrator = TriadDevOrchestrator(Path.cwd())
    status = orchestrator.get_status()
    
    print("TriadDev Status")
    print(f"Project: {status.name}")
    print(f"Phase: {status.current_phase}")
    print(f"Route: {status.route}")
    print(f"Tasks: {status.total_tasks} total, {status.completed_tasks} done, {status.pending_tasks} pending")
    print(f"Recent activity: {len(status.recent_activity)}")
    if args.verbose:
        for item in status.recent_activity:
            print(f" - {item}")
    return 0


def cmd_run(args):
    """Run full workflow"""
    print(f"[TriadDev] Running workflow from: {args.from_phase}")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route)
    result = orchestrator.run_full_workflow(
        from_phase=args.from_phase,
        force_gate=args.force_gate
    )
    
    if result.success:
        print(f"Completed: {result.tasks_processed} tasks")
    else:
        print("Failed:", result.errors)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
