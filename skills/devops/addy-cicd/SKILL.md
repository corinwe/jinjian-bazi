---
name: addy-cicd
description: 生产级CI/CD与自动化——Shift Left、更快更安全、功能标志、质量门禁管道、失败反馈循环。来自addyosmani/agent-skills
category: devops
---

# CI/CD and Automation (生产级CI/CD)

## 概述

持续集成和持续交付自动化。Shift Left——尽早发现问题，越早越便宜。更快更安全——小批量、频繁部署比大版本更安全。功能标志——用标志控制发布，而不是用代码部署。

## 核心原则

### Shift Left
尽早发现问题。在开发过程中测试，而不是在部署后。
```
发现的阶段         修复成本
需求阶段    ──── $1
设计阶段    ──── $10
编码阶段    ──── $100
测试阶段    ──── $1,000
生产阶段    ──── $10,000
```

### 更快更安全
小批量、频繁部署比大版本更安全。每次提交都应该能部署到生产环境。

### 功能标志
功能标志用于控制发布，而不是代码部署。主分支始终是可部署的。
```
// 好：用标志控制功能
if (isFeatureEnabled('new-checkout')) {
  return <NewCheckout />;
}
return <LegacyCheckout />;

// 坏：用分支控制功能
// feature/new-checkout 分支 —— 分支越老，合并越痛苦
```

## CI管道质量门禁

```
提交 → Lint → 类型检查 → 单元测试 → 构建 → 集成测试 → 安全扫描 → 部署
  │                                                                      │
  └── 每一步都必须通过 ──────────────────────────────────────────────→ 失败则阻止
```

每步的门禁标准：
- **Lint:** 无错误，无警告
- **类型检查:** 严格模式下通过
- **单元测试:** 100%通过，覆盖率≥80%
- **构建:** 生产构建成功
- **集成测试:** 关键路径测试通过
- **安全扫描:** 无高/严重漏洞

## 部署策略

### 分阶段回滚
```
Canary (5%) → 扩展 (25%) → 扩展 (50%) → 全面 (100%)
    │            │              │             │
    ▼            ▼              ▼             ▼
  监控响应时间  监控错误率    监控业务指标   完成
```

### 回滚流程
```
1. 检测到问题（监控告警或用户报告）
2. 立即回滚到上一个已知良好的版本
3. 停止管道——阻止更多部署
4. 在回滚版本上调查根因
5. 修复后正常管道部署
```

## 自动化规则

| 应该自动化 | 不应该自动化 |
|-----------|-------------|
| Lint和格式化 | 代码审查 |
| 测试运行 | 架构决策 |
| 构建和打包 | 安全检查（工具检查，人做判断） |
| 部署到staging | 部署到生产（需要批准） |
| 依赖更新（Dependabot） | 功能标志切换 |
| 监控告警 | 回滚（先自动检测，再人工确认） |

## ⚠️ GitHub PAT Workflow Scope 坑

推送CI/CD workflow文件(.github/workflows/*.yml)时，GitHub PAT**必须**有 `workflow` scope：
- 仅有 `repo` scope → 被拒绝：`refusing to allow a Personal Access Token to create or update workflow`
- 解决方式：
  1. 在GitHub Settings中生成带 `workflow` scope的PAT
  2. 或：将workflow文件放在 `docs/` 目录下，手动复制到 `.github/workflows/`
  3. 或：使用 `gh` CLI（已通过OAuth认证）
- 推荐做法：CI/CD workflow文件存两份：`docs/ci-cd.yml`（文档版）+ `.github/workflows/ci-cd.yml`（执行版）

## 参考文件

本技能包含以下参考文件：
- `references/bazi-ci-cd-pattern.md` — 八字平台实战CI/CD流程（GitHub Actions三阶段模板 + PAT workflow scope处理）

### GitHub PAT Workflow Scope
- 推送包含 `.github/workflows/*.yml` 的文件时，GitHub PAT**必须包含 `workflow` scope**
- 如果PAT只有 `repo` scope但无 `workflow` scope，推workflow文件会被拒绝：
  ```
  refus to allow a Personal Access Token to create or update workflow
  `.github/workflows/ci-cd.yml` without `workflow` scope
  ```
- 解决方案：
  - 方案A：生成一个有 `workflow` scope的PAT（在GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens中勾选Actions权限）
  - 方案B：先排除workflow文件（git rm --cached + .gitignore），推代码后手动配置workflow
  - 方案C：用SSH密钥替代PAT推workflow文件

### CI管道设计模式
生产级的CI管道分为三个阶段：
```
Phase 1: 验证（计算型优先）
  ├── 模块导入验证（import检查）
  ├── 单元测试（所有模块）
  ├── 集成测试（API端点）
  └── 全量验证（综合检查）

Phase 2: 构建
  ├── Docker构建（含缓存）
  └── Docker健康检查

Phase 3: 部署
  ├── 拉取最新代码
  ├── 运行验证
  ├── 重启服务
  └── 健康检查确认
```
