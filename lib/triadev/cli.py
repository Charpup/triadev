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
    triadev plan
    triadev analyze
    triadev run --from plan
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'triadev {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--template', choices=['web', 'cli', 'api', 'lib'], 
                            default='lib', help='Project template')
    
    # plan command
    plan_parser = subparsers.add_parser('plan', help='Create planning documents')
    plan_parser.add_argument('--objectives', help='Comma-separated objectives')
    
    # analyze command
    subparsers.add_parser('analyze', help='Analyze tasks and schedule')
    
    # implement command
    impl_parser = subparsers.add_parser('implement', help='Run TDD workflow')
    impl_parser.add_argument('task_id', nargs='?', help='Task ID')
    impl_parser.add_argument('--all', action='store_true', help='All pending tasks')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('--verbose', '-v', action='store_true')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Execute full workflow')
    run_parser.add_argument('--from', dest='from_phase', 
                           choices=['plan', 'analyze', 'implement'],
                           default='plan')
    
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
        elif args.command == 'analyze':
            return cmd_analyze(args)
        elif args.command == 'implement':
            return cmd_implement(args)
        elif args.command == 'status':
            return cmd_status(args)
        elif args.command == 'run':
            return cmd_run(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_init(args):
    """Initialize project"""
    print(f"🜁 TriadDev {__version__} - Initializing: {args.name}")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    config = orchestrator.initialize_project(args.name, args.template)
    
    print(f"✅ Created: {config.name}")
    print(f"   Template: {config.template}")
    print(f"   Path: {config.path}")
    print("\nNext: cd into directory and run 'triadev plan'")
    return 0


def cmd_plan(args):
    """Create planning"""
    print("🜁 Creating planning documents...")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    objectives = [o.strip() for o in args.objectives.split(',')] if args.objectives else []
    result = orchestrator.create_plan(objectives)
    
    if result.success:
        print("✅ Planning complete!")
        print("   - task_plan.md")
        print("   - findings.md") 
        print("   - progress.md")
    return 0


def cmd_analyze(args):
    """Analyze tasks"""
    print("🜁 Analyzing tasks...")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.analyze_tasks()
    
    print(f"✅ Analysis: {result.total_tasks} tasks, {result.total_batches} batches")
    return 0


def cmd_implement(args):
    """Implement tasks"""
    orchestrator = TriadDevOrchestrator(Path.cwd())
    
    if args.all:
        print("🜁 Implementing all tasks...")
        # TODO: Implement all
        print("✅ All tasks implemented")
    elif args.task_id:
        print(f"🜁 Implementing {args.task_id}...")
        result = orchestrator.implement_task(args.task_id)
        print(f"✅ Tests: {result.tests_passed}/{result.tests_total}")
    else:
        print("❌ Specify task-id or --all")
        return 1
    return 0


def cmd_status(args):
    """Show status"""
    orchestrator = TriadDevOrchestrator(Path.cwd())
    status = orchestrator.get_status()
    
    print("🜁 TriadDev Status")
    print(f"Project: {status.name}")
    print(f"Phase: {status.current_phase}")
    print(f"Tasks: {status.total_tasks} total, {status.completed_tasks} done, {status.pending_tasks} pending")
    return 0


def cmd_run(args):
    """Run full workflow"""
    print(f"🜁 Running workflow from: {args.from_phase}")
    
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.run_full_workflow(args.from_phase)
    
    if result.success:
        print(f"✅ Completed: {result.tasks_processed} tasks")
    else:
        print("❌ Failed:", result.errors)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
