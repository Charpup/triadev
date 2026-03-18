# Task Plan — Linux Fallback for TriadDev Plan Runtime

## Context
Branch: `triadev-core-runtime-gate-contract`
Route: `extended` execution path for implementation checks, plus `core` smoke path.

## Objectives
- [x] Identify where planning runtime invokes PowerShell.
- [x] Add minimal Linux fallback without breaking Windows behavior.
- [x] Run smoke matrix for core + extended gate contract.
- [ ] Commit and push if all smoke checks pass.

## Route/Gate Notes
- Core route (`plan -> workflow -> status`) should run without implementation.
- Extended route must enforce gate contract:
  - `implement` blocked before `value-gate`
  - `implement --all` allowed after gate pass.

## Acceptance Criteria
1. `triadev plan` succeeds on Linux hosts without `powershell` binary.
2. If `pwsh`/`powershell` exists, existing PowerShell path remains preferred.
3. Smoke checks all pass for required command set.
4. Changes are minimal and targeted.
5. Commit message exactly: `fix: add Linux fallback for planning runtime and pass smoke tests`.
