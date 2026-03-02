# Skill Orchestrator（技能编排器）

智能技能编排器，在开始任何任务前自动识别并调用相关技能。

## 特性

- **智能判断**：不是强制执行，而是根据任务复杂度智能决策
- **用户可控**：支持用户主动触发或跳过技能流程
- **多平台支持**：兼容 Claude Code 和 OpenCode
- **灵活配置**：通过配置文件自定义行为

## 安装

### Claude Code

将此目录复制到 Claude Code 的技能目录：

```bash
cp -r skill-orchestrator ~/.claude/skills/
```

或在项目中使用：

```bash
cp -r skill-orchestrator .claude/skills/
```

### OpenCode

将此目录复制到 OpenCode 的技能目录：

```bash
cp -r skill-orchestrator ~/.opencode/skills/
```

## 使用方法

### 自动触发

当用户发起任务时，技能编排器会自动分析并推荐合适的技能：

```
用户：帮我实现一个用户登录功能

AI：🎯 检测到新功能开发，将使用 brainstorming 技能来处理。
    该技能会帮助我们梳理需求、设计方案。

    如需跳过，请回复"跳过"或"直接处理"。
```

### 手动触发

```
用户：/skill-orchestrator
```

或

```
用户：使用技能编排器来分析这个任务
```

### 跳过技能

```
用户：快速实现一个登录功能，跳过流程

AI：好的，我将直接实现登录功能...
```

## 配置

在项目根目录创建 `.claude/skill-orchestrator.yaml`：

```yaml
orchestrator:
  auto_invoke: true          # 自动调用技能
  confidence_threshold: 0.7  # 自动调用的置信度阈值
  allow_skip: true           # 允许用户跳过
  mode: balanced             # 工作模式：strict/balanced/fast
```

### 工作模式

| 模式 | 说明 |
|------|------|
| `strict` | 严格遵循技能流程，适合重要项目 |
| `balanced` | 平衡规范与效率，推荐日常使用 |
| `fast` | 优先效率，仅在必要时调用技能 |

## 与 using-superpowers 的区别

| 方面 | using-superpowers | skill-orchestrator |
|------|-------------------|-------------------|
| 语气 | 强制性 | 引导性 |
| 灵活性 | 低 | 高 |
| 用户体验 | 可能繁琐 | 友好可控 |
| 平台支持 | Claude Code | Claude Code + OpenCode |
| 配置能力 | 无 | 支持 YAML 配置 |

## 技能优先级

编排器按以下优先级调用技能：

1. **流程控制类**：brainstorming → debugging
2. **执行指导类**：TDD → code-review
3. **领域专用类**：frontend-design → api-design

## 最佳实践

1. **新项目**：使用 `strict` 模式，确保流程规范
2. **快速迭代**：使用 `fast` 模式，提高效率
3. **团队协作**：统一配置，保持一致性

## 版本历史

- v1.0.0 - 初始版本，支持 Claude Code 和 OpenCode

## 许可证

MIT License
