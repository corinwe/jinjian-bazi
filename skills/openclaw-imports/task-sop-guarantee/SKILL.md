---
name: task-sop-guarantee
description: 任务执行 SOP 保证系统。强制任务追踪、自动验证、三重备份，确保任务不丢失、100% 按 SOP 执行。
metadata:
  {
    "openclaw":
      {
        "emoji": "✅",
        "requires": { "bins": ["bash", "curl", "jq"] },
        "install":
          [
            {
              "id": "scripts",
              "kind": "copy",
              "source": "./scripts",
              "target": "./scripts",
              "label": "安装任务管理脚本",
            },
          ],
      },
  }
---

# Task SOP Guarantee - 任务执行保证系统

**强制化任务追踪与验证系统**，确保每个任务都不丢失、都按 SOP 执行。

## 核心机制

### 1️⃣ 任务生命周期追踪

```
创建 → 执行 → 验证 → 完成/失败 → 归档
  ↓      ↓      ↓        ↓         ↓
记录 ID  执行中  跑脚本  必须 PASS  写入历史
```

### 2️⃣ SOP 强制执行流程

**每个任务必须通过 4 个阶段：**

1. **创建任务** → 立即记录到 task-database.json
2. **执行任务** → 实时记录步骤到 task-execution.log
3. **验证任务** → 必须运行验证脚本（HTTP/进程/内容检查）
4. **完成任务** → 只有验证 PASS 才能标记完成

### 3️⃣ 自动验证机制

**每小时自动检查：**
- ✅ 产品页面可访问性
- ✅ 服务进程运行状态
- ✅ 定时任务配置
- ✅ 任务执行进度

### 4️⃣ 三重备份（系统重置不丢）

```
1. 本地文件 → task-database.json + task-execution.log
2. 飞书任务表 → 云端备份（可选同步）
3. MemOS 记忆 → 对话自动记录
```

---

## 安装

### 1. 安装 Skill

```bash
# 从 ClawHub 安装（如果已发布）
clawhub install task-sop-guarantee

# 或手动安装
cp -r /path/to/task-sop-guarantee ~/.openclaw/workspace/skills/
```

### 2. 初始化任务系统

```bash
# 运行初始化脚本
./scripts/init-task-system.sh
```

这会创建：
- ✅ `task-database.json` - 任务数据库
- ✅ `task-execution.log` - 执行日志
- ✅ `cron-hourly-verify.sh` - 每小时验证任务
- ✅ `task-verify.sh` - 验证脚本

### 3. 配置定时任务（可选）

```bash
# 添加到 crontab（每小时自动验证）
(crontab -l 2>/dev/null; echo "0 * * * * /root/.openclaw/workspace/cron-hourly-verify.sh") | crontab -
```

---

## 使用方法

### 创建任务

```bash
# 语法
./scripts/task-manager.sh create "任务名称" "任务描述"

# 示例
./scripts/task-manager.sh create "产品页面部署" "部署 OfferPath 产品页面到服务器"
# → 输出：TASK-1711166400
```

### 验证任务

**HTTP 验证：**
```bash
./scripts/task-manager.sh verify "TASK-xxx" "http" "http://43.162.90.39:5173"
```

**进程验证：**
```bash
./scripts/task-manager.sh verify "TASK-xxx" "process" "python.*5173"
```

**文件验证：**
```bash
./scripts/task-manager.sh verify "TASK-xxx" "file" "/var/www/offerpath/index.html"
```

**内容验证：**
```bash
./scripts/task-manager.sh verify "TASK-xxx" "content" "http://43.162.90.39:5173" "Offer 路书"
```

### 完成任务

```bash
# 只有验证 PASS 才能完成
./scripts/task-manager.sh complete "TASK-xxx" "PASS"
```

### 查询任务

```bash
# 查看所有任务
./scripts/task-manager.sh list

# 查看执行日志
cat /root/.openclaw/workspace/task-execution.log | tail -50

# 查询特定任务
grep "TASK-xxx" /root/.openclaw/workspace/task-execution.log
```

---

## 文件结构

```
task-sop-guarantee/
├── SKILL.md                    # 技能说明（本文件）
├── scripts/
│   ├── task-manager.sh         # 任务管理主脚本
│   ├── task-verify.sh          # 验证脚本
│   ├── init-task-system.sh     # 初始化脚本
│   └── update-status.sh        # 状态更新脚本
├── task-database.json          # 任务数据库（运行时生成）
├── task-execution.log          # 执行日志（运行时生成）
└── README.md                   # 详细文档
```

---

## 验证类型

| 类型 | 参数 | 示例 | 说明 |
|------|------|------|------|
| HTTP | `http` | `verify "TASK-1" "http" "http://..."` | 检查 HTTP 状态码 |
| 进程 | `process` | `verify "TASK-1" "process" "python.*5173"` | 检查进程是否运行 |
| 文件 | `file` | `verify "TASK-1" "file" "/path/to/file"` | 检查文件是否存在 |
| 内容 | `content` | `verify "TASK-1" "content" "http://..." "关键词"` | 检查页面内容 |

---

## 自动化

### 每小时自动验证

```bash
# cron-hourly-verify.sh
#!/bin/bash
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/hourly-verify.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 更新系统状态
$WORKSPACE/scripts/update-status.sh >> $LOG_FILE 2>&1

# 运行验证脚本
echo "[$TIMESTAMP] 开始验证..." >> $LOG_FILE
$WORKSPACE/scripts/task-verify.sh >> $LOG_FILE 2>&1
```

### 状态 Dashboard（可选）

```bash
# 部署 Dashboard
cp dashboard.html /var/www/offerpath/
# 访问：http://your-server/dashboard.html
```

---

## 系统重置后恢复

```bash
# 1. 读取飞书任务表恢复任务状态
# 2. 读取 task-database.json 恢复数据库
# 3. 调用 memory_search("任务") 恢复对话记忆
# 4. 继续执行未完成的任务
```

---

## 示例工作流

### 示例 1：部署产品页面

```bash
# 1. 创建任务
./task-manager.sh create "产品页面部署" "部署 OfferPath 到服务器"
# → TASK-001

# 2. 执行部署
# ... 执行操作 ...

# 3. 验证
./task-manager.sh verify "TASK-001" "http" "http://43.162.90.39:5173"
./task-manager.sh verify "TASK-001" "content" "http://43.162.90.39:5173" "Offer 路书"
# → PASS

# 4. 完成
./task-manager.sh complete "TASK-001" "PASS"
# → ✅ 任务完成
```

### 示例 2：配置定时任务

```bash
# 1. 创建任务
./task-manager.sh create "早 8 点汇报" "创建 cron 任务每天 8 点推送日报"
# → TASK-002

# 2. 执行配置
echo "0 8 * * * /path/to/report.sh" | crontab -

# 3. 验证
./task-manager.sh verify "TASK-002" "process" "cron"
crontab -l | grep "report.sh"
# → PASS

# 4. 完成
./task-manager.sh complete "TASK-002" "PASS"
```

---

## 核心承诺

> **"不创建记录不干活，不验证通过不汇报，不相同错误犯两次"**

---

## 相关资源

- **任务追踪表：** `/root/.openclaw/workspace/task-tracker.md`
- **SOP 文档：** `/root/.openclaw/workspace/task-sop-enforcement.md`
- **保证机制：** `/root/.openclaw/workspace/task-guarantee-mechanism.md`

---

## 版本

- **当前版本：** 1.0.0
- **创建时间：** 2026-03-23
- **创建者：** 虾王 🦐
