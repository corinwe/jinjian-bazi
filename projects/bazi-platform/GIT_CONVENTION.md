# 金鉴真人 · Git 提交规范

## 提交消息格式

```
<type>(<scope>): <description>
```

### Type（必填）

| Type | 使用场景 |
|:-----|:---------|
| `feat` | 新功能 |
| `fix` | Bug修复 |
| `refactor` | 代码重构（不改变功能） |
| `test` | 添加/修改测试 |
| `docs` | 文档变更 |
| `chore` | 杂务（构建、CI、依赖） |
| `perf` | 性能改进 |
| `style` | 格式化（不改变逻辑） |
| `ci` | CI/CD配置变更 |

### Scope（可选）

| Scope | 对应模块 |
|:------|:---------|
| `engine` | 规则引擎（36模块） |
| `api` | FastAPI服务 |
| `frontend` | 前端SPA |
| `database` | 数据库 |
| `ci` | CI/CD |
| `devops` | DevOps工具链 |
| `docs` | 文档 |

### 示例

```
feat(engine): 新增身弱从弱排查逻辑
fix(api): 修复农历转换闰月边界错误
refactor(frontend): 重构21§渲染为模块化组件
test(engine): 新增燥土规则测试用例（15条）
chore: 更新pyproject.toml ruff规则
docs: 更新API文档端点说明
```

## 分支策略

| 分支 | 用途 | 寿命 |
|:-----|:-----|:-----|
| `main` | 生产就绪代码 | 永久 |
| `develop` | 开发集成分支 | 永久 |
| `feature/*` | 新功能开发 | 1-2天 |
| `fix/*` | Bug修复 | 1天 |

## 工作流

```
1. 从main签出分支: git checkout -b feature/add-rate-limit
2. 原子提交: git commit -m "feat(api): 添加速率限制(30req/min)"
3. 推送: git push origin feature/add-rate-limit
4. 创建PR → 审查 → 合并到main
```

## 原子提交原则

- 每个提交 = 一个逻辑变更
- 包括测试
- 提交前跑本地验证
- 清晰的提交消息
