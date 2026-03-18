# Findings

## Code Location
- Planning runtime hook is in `lib/triadev/orchestrator.py` at `_run_planning_script`.
- Existing behavior selected `init-session.ps1` first when file exists, then invoked hardcoded `powershell`.
- On Linux without PowerShell, this can fail even if shell script fallback exists.

## Fix Strategy (Minimal)
- Detect executable availability with `shutil.which`.
- Prefer `pwsh` then `powershell` when PowerShell script exists.
- If no PowerShell executable, fallback to `bash` then `sh` for `init-session.sh`.
- Preserve `check=False` behavior to avoid hard failures from optional planner bootstrap script.

## Risk Notes
- Low risk: contained to one helper function.
- Windows path preserved by prioritizing PowerShell executables.
