---
name: triadev
description: >
  TRIGGER: triadev, Golden Triangle, 三元开发, TriadDev, brownfield workflow, delta spec, OpenSpec.
  TriadDev v2.1 style route+gate runtime in this repo: Core for planning, Extended for implementation.
---

# TriadDev Runtime Contract (Local Build)

**Version (this workspace):** runtime-aligned v2.1 (current branch)

## Core/Extended + Value Gate Contract

- `Core` route:
  - 执行目标：规划、梳理、DAG 调度、状态跟踪，不进行实现。
  - 典型入口：`triadev init --route core`。
  - 价值门默认通过（`GO`）。
- `Extended` 路线：任何实现意图（包括 brownfield / artifact）都走扩展路线。
  - 默认扩展模式包括 `extended` / `brownfield` / `artifact`。
  - 实现前必须经过 value-first gate：`value-gate`。
  - 如果 gate 结果 `REVISE`/`NO-GO`，`implement` 不能进入执行。
- 路由约束：
  - `init --mode` 与 `init --route` 为兼容参数，`brownfield` 与 `artifact` 会映射到执行层的 Extended。
  - `plan --route` 支持 `core/extended/artifact/brownfield`（解析时按路由语义进入）。

## 1) Implemented

### 命令入口（已实现）
- `init`
- `init-brownfield`
- `plan`
- `detect-specs`
- `delta`
- `propose`
- `spec`
- `design`
- `tasks`
- `analyze`
- `workflow`
- `value-gate`
- `implement`
- `archive`
- `sync`
- `status`
- `run`

### 运行时产物（已实现）
- `triadev-project.json`
- `.triadev/state.json`
- `.triadev/workflow.json`
- `task_plan.md`, `findings.md`, `progress.md`
- `SPEC.yaml`
- `SPEC-delta.yaml`
- `artifacts/proposal.md`
- `artifacts/specs/*.yaml`
- `artifacts/design.md`
- `artifacts/tasks.md`
- `changes/active/*/meta.json`
- `changes/archive/*`
- `value-review.md`（由 `value-gate` 生成）
- `specs/task-*.yaml`（`implement` 最小占位输出）

### 命令执行链（最小闭环）
- Core: `plan -> workflow`
- Extended/Brownfield/Artifact: `plan -> workflow -> value-gate -> implement -> sync`
- `run --from` 支持：
  - `plan`
  - `workflow`
  - `detect-specs`
  - `delta`
  - `artifact-propose`
  - `spec`
  - `design`
  - `tasks`
  - `value-gate`
  - `implement`
  - `sync`

## 2) Minimal Semantics (这版最小实现语义)

- `init`
  - 创建项目目录结构、配置文件、`.triadev`、`artifacts/`、`changes/`。
  - 如上游脚本缺失，仍保证本地骨架可落地。
- `init-brownfield`
  - 把现有目录标记为 `mode=extended`，写入 `.triadev/state.json`。
  - 不自动创建 delta，需后续 `detect-specs`。
- `detect-specs`
  - 扫描现有代码骨架，产出 `SPEC.yaml`（最小语义骨架）。
- `delta`
  - 产出 `SPEC-delta.yaml`，记录变更，并写入 `changes/active/<slug>/meta.json`。
- `propose / spec / design / tasks`
  - 产出对应 artifact 文档。
- `archive`
  - 移动 `changes/active/<name>` 到 `changes/archive/...`，然后合并 delta 到 `SPEC.yaml`。
- `sync`
  - 幂等化合并 `SPEC-delta.yaml` 到 `SPEC.yaml`，返回 merge summary。
- `value-gate`
  - 生成 `value-review.md`，更新 `state.value_gate`。
  - `run` 与 `implement` 双重检查：未通过不进入实现。

## 3) Future Enhancements (非本次契约)

- 复杂冲突合并策略（当前为最小幂等合并）
- 运行期自动回滚与可逆状态恢复
- 与更多外部 CI/CD 工具链的深度绑定

## Commands Reference（建议优先顺序）

### Core path
```bash
triadev init <name> --template lib --route core
triadev plan --route core --objectives "Research,Analyze,Execute"
triadev workflow
triadev run --from plan --route core
```

### Extended / Artifact / Brownfield path
```bash
triadev init <name> --mode extended
triadev plan --route extended --objectives "Spec,Design,Test"
triadev detect-specs
triadev delta --add "new api" --modify "flow"
triadev propose --intent "Modernize auth" --scope "in: login" --scope "out: deprecate legacy oauth"
triadev spec --from-proposal
triadev design --approach "incremental migration"
triadev tasks
triadev value-gate
triadev implement --all
triadev sync --all
triadev archive --force
```

### Brownfield entry
```bash
triadev init-brownfield <legacy_dir> --name legacy-demo
triadev detect-specs
triadev delta --add "new api"
triadev run --from detect-specs
triadev run --from workflow --route extended
```

## CLI 与状态核查

```bash
python -m triadev --help
triadev --help
triadev status --verbose
```

### First Verification (推荐)
- `triadev init demo-core --template lib`
- `triadev plan --objectives "Research,Implement,Test" --route core`
- `triadev workflow`
- `triadev status --verbose`
- `triadev init-brownfield <temp_dir> --name legacy-demo`（或任一已有目录）
- `triadev detect-specs`
- `cat .triadev/state.json` 检查 `brownfield.base_spec_generated=true`（在执行后）

## Project Structure (Runtime Snapshot)

```text
my-project/
├── triadev-project.json
├── task_plan.md
├── findings.md
├── progress.md
├── SPEC.yaml
├── SPEC-delta.yaml
├── value-review.md
├── artifacts/
│   ├── proposal.md
│   ├── specs/
│   ├── design.md
│   └── tasks.md
├── changes/
│   ├── active/
│   │   └── <change-id>/meta.json
│   └── archive/
├── .triadev/
│   ├── state.json
│   └── workflow.json
├── 01_active/
│   ├── tasks/
│   ├── research/
│   └── docs/
├── specs/
└── tests/
```

## Notes

- `artifact` 与 `brownfield` 是入口语义，不是新增运行阶段名；二者会走 Extended 执行语义并使用 value-first gate 阈值约束。
- `run --from` 中 `value-gate` 与 `implement` 会按状态机复核 gate；被阻断时会返回失败并停在阻塞阶段。
