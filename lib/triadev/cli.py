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
    triadev init demo --template web
    triadev init-brownfield ./legacy-app --name "Legacy Migration"
    triadev plan --route extended
    triadev detect-specs
    triadev delta --add "new feature" --modify "existing behavior"
    triadev run --from plan
    ''',
    )

    parser.add_argument('--version', action='version', version=f'triadev {__version__}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    init_parser = subparsers.add_parser('init', help='Initialize greenfield project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--template', choices=['web', 'cli', 'api', 'lib'], default='lib')
    init_parser.add_argument('--route', choices=['core', 'extended', 'artifact', 'brownfield'], default=None)
    init_parser.add_argument('--mode', choices=['core', 'extended', 'brownfield', 'artifact'], default=None, help='Compat alias with route; brownfield/artifact map to extended execution')

    bf_parser = subparsers.add_parser('init-brownfield', help='Initialize from existing codebase')
    bf_parser.add_argument('source_path', help='Existing directory path')
    bf_parser.add_argument('--name', help='Project name override')

    plan_parser = subparsers.add_parser('plan', help='Create planning documents')
    plan_parser.add_argument('--objectives', help='Comma-separated objectives')
    plan_parser.add_argument('--route', choices=['core', 'extended', 'artifact'], default='core')

    analyze_parser = subparsers.add_parser('analyze', help='Analyze tasks and schedule')
    workflow_parser = subparsers.add_parser('workflow', help='Analyze and schedule tasks')

    detect_parser = subparsers.add_parser('detect-specs', help='Detect and generate base specs from code')

    delta_parser = subparsers.add_parser('delta', help='Create delta specs')
    delta_parser.add_argument('--add', action='append', default=[], help='Additions')
    delta_parser.add_argument('--modify', action='append', default=[], help='Modifications')
    delta_parser.add_argument('--remove', action='append', default=[], help='Removals')
    delta_parser.add_argument('--name', help='Change id override')

    propose_parser = subparsers.add_parser('propose', help='Create proposal artifacts')
    propose_parser.add_argument('--intent', required=True)
    propose_parser.add_argument('--scope', action='append', default=[], help='Scope lines')

    spec_parser = subparsers.add_parser('spec', help='Generate specs from proposal')
    spec_parser.add_argument('--from-proposal', action='store_true', default=True)

    design_parser = subparsers.add_parser('design', help='Create design artifact')
    design_parser.add_argument('--approach', required=True)

    tasks_parser = subparsers.add_parser('tasks', help='Create artifact tasks list')

    gate_parser = subparsers.add_parser('value-gate', help='Run value-first gate')
    gate_parser.add_argument('--force', action='store_true', help='Re-run gate review')

    impl_parser = subparsers.add_parser('implement', help='Run TDD workflow')
    impl_parser.add_argument('task_id', nargs='?', help='Task ID')
    impl_parser.add_argument('--all', action='store_true', help='All pending tasks')
    impl_parser.add_argument('--route', choices=['core', 'extended'], default='extended')
    impl_parser.add_argument('--force-gate', action='store_true', help='Force rerun value gate if blocked')

    archive_parser = subparsers.add_parser('archive', help='Archive current change')
    archive_parser.add_argument('name', nargs='?', help='Active change name')
    archive_parser.add_argument('--force', action='store_true', help='Force archive even if destination exists')

    sync_parser = subparsers.add_parser('sync', help='Sync delta to SPEC')
    sync_parser.add_argument('--from-delta', action='store_true', help='Only sync unmerged delta entries')
    sync_parser.add_argument('--all', action='store_true', help='Sync all delta entries, including merged')

    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('--verbose', '-v', action='store_true')

    run_parser = subparsers.add_parser('run', help='Execute workflow from phase')
    run_parser.add_argument(
        '--from',
        dest='from_phase',
        choices=['plan', 'analyze', 'workflow', 'detect-specs', 'delta', 'artifact-propose', 'spec', 'design', 'tasks', 'value-gate', 'implement', 'sync'],
        default='plan',
    )
    run_parser.add_argument('--route', choices=['core', 'extended'], default='extended')
    run_parser.add_argument('--force-gate', action='store_true', help='Rerun value gate if not passed')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == 'init':
            return cmd_init(args)
        if args.command == 'init-brownfield':
            return cmd_init_brownfield(args)
        if args.command == 'plan':
            return cmd_plan(args)
        if args.command in {'analyze', 'workflow'}:
            return cmd_workflow(args)
        if args.command == 'detect-specs':
            return cmd_detect_specs(args)
        if args.command == 'delta':
            return cmd_delta(args)
        if args.command == 'propose':
            return cmd_propose(args)
        if args.command == 'spec':
            return cmd_spec(args)
        if args.command == 'design':
            return cmd_design(args)
        if args.command == 'tasks':
            return cmd_tasks(args)
        if args.command == 'value-gate':
            return cmd_value_gate(args)
        if args.command == 'implement':
            return cmd_implement(args)
        if args.command == 'archive':
            return cmd_archive(args)
        if args.command == 'sync':
            return cmd_sync(args)
        if args.command == 'status':
            return cmd_status(args)
        if args.command == 'run':
            return cmd_run(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_init(args):
    resolved_route = args.mode or args.route or 'core'
    if resolved_route in {'brownfield', 'artifact'}:
        resolved_route = 'extended'
    if args.mode and args.route:
        print(f"route preference: using --mode={resolved_route} over --route={args.route}")

    print(f"Initializing: {args.name}")
    orchestrator = TriadDevOrchestrator(Path.cwd())
    config = orchestrator.initialize_project(args.name, args.template, route=resolved_route)
    print(f"Created: {config.name}")
    print(f"Template: {config.template}")
    print(f"Path: {config.path}")
    print(f"Route: {config.mode}")
    return 0


def cmd_init_brownfield(args):
    print(f"Initializing brownfield project from: {args.source_path}")
    orchestrator = TriadDevOrchestrator(Path.cwd())
    config = orchestrator.init_brownfield_project(args.source_path, name=args.name)
    print(f"Created: {config.name}")
    print(f"Path: {config.path}")
    print("Route: extended")
    return 0


def cmd_plan(args):
    print('Creating planning documents...')
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route if args.route else 'core')
    objectives = [o.strip() for o in args.objectives.split(',')] if args.objectives else []
    result = orchestrator.create_plan(objectives)
    if result.success:
        print('Planning complete')
        print('  - task_plan.md')
        print('  - findings.md')
        print('  - progress.md')
    return 0


def cmd_workflow(args):
    print('Analyzing workflow tasks...')
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.analyze_tasks()
    print(f"Analysis: {result.total_tasks} tasks, {result.total_batches} batches")
    for idx, batch in enumerate(result.batches, 1):
        batch_ids = ', '.join(t['id'] for t in batch) if batch else '-'
        print(f"  Batch {idx}: {batch_ids}")
    return 0


def cmd_detect_specs(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    path = orchestrator.detect_specs()
    print(f"SPEC generated: {path}")
    return 0


def cmd_delta(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.build_delta(
        add=args.add,
        modify=args.modify,
        remove=args.remove,
        name=args.name,
    )
    print(f"Delta created: {result}")
    return 0


def cmd_propose(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    path = orchestrator.create_proposal(args.intent, args.scope)
    print(f"Proposal created: {path}")
    return 0


def cmd_spec(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    path = orchestrator.build_spec_from_proposal(from_proposal=args.from_proposal)
    print(f"Spec created: {path}")
    return 0


def cmd_design(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    path = orchestrator.build_design(args.approach)
    print(f"Design created: {path}")
    return 0


def cmd_tasks(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    path = orchestrator.build_tasks()
    print(f"Tasks created: {path}")
    return 0


def cmd_value_gate(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    result = orchestrator.run_value_gate(force=args.force)
    if result['success']:
        print(f"Value gate passed: {result['verdict']} (score={result['score']}, confidence={result['confidence']})")
        return 0
    print(f"Value gate blocked: {result['verdict']} (score={result['score']}, confidence={result['confidence']})")
    return 1


def cmd_implement(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route)
    if args.all:
        print('Implementing all tasks...')
        result = orchestrator.implement_all(force_gate=args.force_gate)
        if result.success:
            print(f"Implemented {result.tasks_processed} tasks")
        else:
            print('Some tasks blocked:')
            for item in result.errors:
                print(f"  - {item}")
            return 1
    elif args.task_id:
        result = orchestrator.implement_task(args.task_id, force_gate=args.force_gate)
        print(f"{args.task_id}: {result.tests_passed}/{result.tests_total}")
        if not result.success:
            return 1
    else:
        print('Specify task-id or --all')
        return 1
    return 0


def cmd_archive(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    target = orchestrator.archive_change(args.name, force=args.force)
    print(f"Archived to: {target}")
    return 0


def cmd_sync(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    summary = orchestrator.sync_specs(from_delta=args.from_delta, from_all=args.all)
    print(f"Synced: {summary.get('merged', [])}")
    if summary.get('skipped'):
        print(f"Skipped: {summary.get('skipped')}")
    print(f"Total entries: {summary.get('total', 0)}")
    return 0


def cmd_status(args):
    orchestrator = TriadDevOrchestrator(Path.cwd())
    status = orchestrator.get_status()
    print('TriadDev Status')
    print(f"Project: {status.name}")
    print(f"Route: {status.route}")
    print(f"Phase: {status.current_phase}")
    print(f"Tasks: {status.total_tasks} total, {status.completed_tasks} done, {status.pending_tasks} pending")
    print(f"Recent activity: {len(status.recent_activity)}")
    if args.verbose:
        for item in status.recent_activity:
            print(f" - {item}")
    return 0


def cmd_run(args):
    print(f"Running workflow from: {args.from_phase}")
    orchestrator = TriadDevOrchestrator(Path.cwd())
    orchestrator.set_route(args.route)
    result = orchestrator.run_full_workflow(from_phase=args.from_phase, force_gate=args.force_gate)
    if result.success:
        print(f"Completed: {result.tasks_processed} tasks")
        return 0
    print('Failed:', result.errors)
    return 1


if __name__ == '__main__':
    sys.exit(main())
