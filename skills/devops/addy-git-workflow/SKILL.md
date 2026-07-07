---
name: addy-git-workflow
description: 生产级Git工作流与版本控制——主干开发、原子提交、变更规模控制(~100行)、提交即保存点模式。来自addyosmani/agent-skills
category: devops
---

# Git Workflow and Versioning (生产级Git工作流)

## 概述

主干开发——在主干（main/master）上工作，使用短寿命功能分支。原子提交——每个提交代表一个单一的、可验证的变更。提交即保存点。

## 核心原则

### 主干开发
```
main: 始终可部署
  │
  ├── feature/login (短寿命，1-2天)
  │   ├── commit 1: 添加登录表单UI
  │   ├── commit 2: 添加认证API
  │   └── commit 3: 添加E2E测试
  │
  └── → 合并回main
```

### 原子提交
- 每个提交 = 一个逻辑变更
- 包括测试
- 提交后系统保持功能性
- 清晰的提交消息

### 提交即保存点
- 每个提交应该代表一个可以恢复的状态
- 频繁提交（至少一天一次）
- 提交前测试

## 提交消息格式

```
<类型>(<范围>): <简短的描述>

<可选的更详细描述>

<可选的闭包问题>
```

### 类型
| 类型 | 使用场景 |
|------|---------|
| feat | 新功能 |
| fix | Bug修复 |
| refactor | 代码重构 |
| test | 添加/修改测试 |
| docs | 文档变更 |
| chore | 杂务（构建、CI、依赖） |
| perf | 性能改进 |
| style | 格式化 |

### 示例
```
feat(auth): 添加OAuth2.0登录流程

实现Google和GitHub OAuth集成。包括：
- OAuth回调处理
- JWT令牌生成
- 会话管理

Closes #1234
```

## 分支策略

| 分支 | 用途 | 寿命 |
|------|------|------|
| main | 生产就绪代码 | 永久 |
| feature/* | 新功能开发 | 1-2天 |
| fix/* | Bug修复 | 1天 |
| release/* | 版本发布准备 | 可选 |

## 工作流

### 日常开发
```
1. 从main签出feature分支: git checkout -b feature/add-tasks
2. 原子提交: git commit -m "feat: 添加任务模型"
3. 推送并打开PR: gh pr create
4. 代码审查通过后合并: gh pr merge
```

### Bug修复
```
1. 从main签出fix分支: git checkout -b fix/login-error
2. 写复现测试 → 提交
3. 修复bug → 提交
4. 推送并打开PR
5. 审查后合并
```
