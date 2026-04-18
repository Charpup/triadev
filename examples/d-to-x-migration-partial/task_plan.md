# Migration Task Plan — D:\ → X:\ ClaudeCodeWorkspace

## Stages

### Stage A — 全量内容迁移 ✅
- [x] A1. archive/ 11 个 D-only 子目录
- [x] A2. humanizer-skill/upstream-fork/ + bulk migration（含 sourcemap, .agents, projects, sandbox）
- [x] A3. 完整性验证（D-only 残留 = 0）
- [ ] A4. git commit Stage A 痕迹

### Stage B — Session 合并
- [ ] B1. 复制 D-- session JSONL → X-- 目录
- [ ] B2. 验证 claude --resume 可见历史
- [ ] B3. 不删 D-- 副本（观察 1 周）

### Stage C — KB-Distillation 决策
- [ ] C1. 在 X:\projects\kb-distillation\ 内运行 /brainstorm
- [ ] C2. 3 角色（数据保管员、KB 架构师、用户代表）
- [ ] C3. 输出 decision.md (GO/REVISE/NO-GO)
- [ ] C4. 根据决策执行后续

### Stage D — 配置切换收尾
- [ ] D1. Grep 全局替换 D:\ClaudeCodeWorkspace 引用
  - ~/.claude/CLAUDE.md (D-- → X-- memory 路径)
  - ~/.claude/protocol/devices-registry.json (workspace_root)
  - X:\ClaudeCodeWorkspace\.claude\rules\*.md
  - X:\ClaudeCodeWorkspace\CLAUDE.md (如有)
- [ ] D2. 验证启动协议 + skill 触发正常
- [ ] D3. D:\ClaudeCodeWorkspace\ 改名 D:\ClaudeCodeWorkspace.archived-20260416\
- [ ] D4. git push 到 Charpup/claude-workspace

## 阶段间审查点

每完成一个 Stage 暂停，向用户汇报关键产出 + 下一步范围，等待 ack 后推进。
