# Task SOP Guarantee - 任务执行保证系统

**版本：** 1.0.0  
**创建时间：** 2026-03-23  
**创建者：** 虾王 🦐

---

## 📖 简介

这是一个**强制化的任务执行保证系统**，确保每个任务都：
- ✅ 不丢失（三重备份）
- ✅ 按 SOP 执行（创建→执行→验证→完成）
- ✅ 可验证（自动跑验证脚本）
- ✅ 可追溯（完整执行日志）

---

## 🎯 核心机制

### 1️⃣ 任务生命周期

```
创建 → 执行 → 验证 → 完成/失败 → 归档
  ↓      ↓      ↓        ↓         ↓
记录 ID  执行中  跑脚本  必须 PASS  写入历史
```

### 2️⃣ SOP 强制执行

**每个任务必须通过 4 个阶段：**

1. **创建任务** → 立即记录到 `task-database.json`
   ```bash
   ./task-manager.sh create "产品页面部署" "部署到服务器"
   # → TASK-1711166400
   ```

2. **执行任务** → 实时记录步骤到 `task-execution.log`
   ```bash
   echo "[$(date)] 执行步骤 1: xxx" >> task-execution.log
   ```

3. **验证任务** → 必须运行验证脚本
   ```bash
   ./task-manager.sh verify "TASK-xxx" "http" "http://..."
   # → ✅ HTTP 状态：200
   ```

4. **完成任务** → 只有验证 PASS 才能标记完成
   ```bash
   ./task-manager.sh complete "TASK-xxx" "PASS"
   # → ✅ 任务完成
   ```

### 3️⃣ 自动验证机制

**每小时自动检查：**
- ✅ 产品页面可访问性（HTTP 200）
- ✅ 服务进程运行状态
- ✅ 定时任务配置
- ✅ 任务执行进度

**如果发现异常：**
- 自动写入日志
- 下次汇报时主动告知
- 连续 2 次异常 → 飞书推送告警

### 4️⃣ 三重备份

```
1. 本地文件 → task-database.json + task-execution.log
2. 飞书任务表 → 云端备份（可选同步）
3. MemOS 记忆 → 对话自动记录
```

**系统重置后恢复：**
```bash
# 1. 读取飞书任务表恢复任务状态
# 2. 读取 task-database.json 恢复数据库
# 3. 调用 memory_search("任务") 恢复对话记忆
# 4. 继续执行未完成的任务
```

---

## 📦 安装

### 方法 1：从 ClawHub 安装（推荐）

```bash
# 安装 skill
clawhub install task-sop-guarantee

# 初始化系统
./skills/task-sop-guarantee/scripts/init-task-system.sh
```

### 方法 2：手动安装

```bash
# 1. 复制 skill 目录
cp -r /path/to/task-sop-guarantee ~/.openclaw/workspace/skills/

# 2. 运行初始化
cd ~/.openclaw/workspace/skills/task-sop-guarantee
./scripts/init-task-system.sh
```

---

## 🚀 快速开始

### 1. 创建任务

```bash
cd /root/.openclaw/workspace

# 语法
./scripts/task-manager.sh create "任务名称" "任务描述"

# 示例
./scripts/task-manager.sh create "产品页面部署" "部署 OfferPath 产品页面到服务器 http://43.162.90.39:5173"
# → 输出：TASK-1711166400
```

### 2. 执行任务

```bash
# 执行你的任务...
# 同时记录关键步骤
echo "[$(date '+%Y-%m-%d %H:%M:%S')] EXEC TASK-1711166400: 创建 HTML 页面" >> task-execution.log
```

### 3. 验证任务

**HTTP 验证：**
```bash
./scripts/task-manager.sh verify "TASK-1711166400" "http" "http://43.162.90.39:5173"
# 🔍 验证任务：TASK-1711166400
#    ✅ HTTP 状态：200
#    结果：PASS
```

**进程验证：**
```bash
./scripts/task-manager.sh verify "TASK-1711166400" "process" "python.*5173"
#    ✅ 进程运行中：python.*5173
#    结果：PASS
```

**内容验证：**
```bash
./scripts/task-manager.sh verify "TASK-1711166400" "content" "http://43.162.90.39:5173" "Offer 路书"
#    ✅ 内容验证通过：Offer 路书
#    结果：PASS
```

### 4. 完成任务

```bash
# 只有验证 PASS 才能完成
./scripts/task-manager.sh complete "TASK-1711166400" "PASS"
# ✅ 任务完成：TASK-1711166400
```

### 5. 查询任务

```bash
# 查看所有任务
./scripts/task-manager.sh list

# 查看执行日志
cat task-execution.log | tail -50

# 查询特定任务
grep "TASK-1711166400" task-execution.log
```

---

## 📋 验证类型

| 类型 | 参数 | 示例 | 说明 |
|------|------|------|------|
| **HTTP** | `http` | `verify "TASK-1" "http" "http://..."` | 检查 HTTP 状态码（必须 200） |
| **进程** | `process` | `verify "TASK-1" "process" "python.*5173"` | 检查进程是否运行 |
| **文件** | `file` | `verify "TASK-1" "file" "/path/to/file"` | 检查文件是否存在 |
| **内容** | `content` | `verify "TASK-1" "content" "http://..." "关键词"` | 检查页面内容是否包含关键词 |

---

## ⚙️ 自动化配置

### 每小时自动验证

```bash
# 已自动添加到 crontab
0 * * * * /root/.openclaw/workspace/cron-hourly-verify.sh
```

**检查内容：**
- 产品页面 HTTP 状态
- Python 服务进程
- 定时任务配置
- 任务执行日志

### Dashboard（可选）

```bash
# 部署 Dashboard
cp dashboard.html /var/www/offerpath/

# 访问
http://your-server/dashboard.html
```

**功能：**
- 实时显示所有定时任务
- 系统状态监控
- 验证日志查看
- 下次执行倒计时

---

## 📊 任务状态定义

| 状态 | 说明 |
|------|------|
| `pending` | 已创建，未开始执行 |
| `in_progress` | 正在执行 |
| `verified` | 执行完成，验证通过 |
| `completed` | 已标记完成 |
| `failed` | 验证失败或执行失败 |

---

## 🔍 常见问题

### Q: 系统重置后怎么办？

**A:** 按以下步骤恢复：

```bash
# 1. 读取飞书任务表
# 访问：https://zhl7lcjncy.feishu.cn/base/KEA0bePepapdxpsvecFciL4qn3b

# 2. 读取本地数据库
cat task-database.json

# 3. 搜索记忆
memory_search("任务")

# 4. 继续执行未完成的任务
```

### Q: 如何保证不忘记任务？

**A:** 三重备份机制：
1. 本地文件（task-database.json）
2. 飞书云端（智能表格）
3. MemOS 记忆（对话自动记录）

### Q: 验证失败怎么办？

**A:** 
1. 不能标记完成
2. 立即修复问题
3. 重新验证
4. PASS 后才能完成

### Q: 如何避免相同错误犯两次？

**A:** 
- 所有失败记录到 `failed` 数组
- 每次创建任务时检查历史
- 发现重复任务时告警

---

## 📁 文件结构

```
task-sop-guarantee/
├── SKILL.md                    # 技能说明
├── README.md                   # 详细文档（本文件）
├── scripts/
│   ├── task-manager.sh         # 任务管理主脚本
│   ├── task-verify.sh          # 验证脚本
│   ├── init-task-system.sh     # 初始化脚本
│   ├── update-status.sh        # 状态更新脚本
│   └── cron-hourly-verify.sh   # 每小时验证
├── task-database.json          # 任务数据库（运行时生成）
├── task-execution.log          # 执行日志（运行时生成）
└── dashboard.html              # 可视化 Dashboard（可选）
```

---

## 🎯 核心承诺

> **"不创建记录不干活，不验证通过不汇报，不相同错误犯两次"**

---

## 📝 使用示例

### 示例 1：部署产品页面

```bash
# 1. 创建任务
./task-manager.sh create "产品页面部署" "部署 OfferPath 到服务器"
# → TASK-001

# 2. 执行部署
# ... 创建 HTML、上传到服务器 ...
echo "[$(date)] EXEC TASK-001: 创建 HTML 页面" >> task-execution.log
echo "[$(date)] EXEC TASK-001: 上传到 /var/www/offerpath/" >> task-execution.log

# 3. 验证
./task-manager.sh verify "TASK-001" "http" "http://43.162.90.39:5173"
./task-manager.sh verify "TASK-001" "content" "http://43.162.90.39:5173" "Offer 路书"
# → PASS

# 4. 完成
./task-manager.sh complete "TASK-001" "PASS"
# → ✅ 任务完成

# 5. 汇报
"老板，产品页面已完成！
✅ 访问验证：HTTP 200
✅ 内容验证：Offer 路书正常显示
✅ 任务 ID: TASK-001"
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

## 🔗 相关资源

- **ClawHub:** https://clawhub.com
- **OpenClaw Docs:** https://docs.openclaw.ai
- **飞书任务表:** https://zhl7lcjncy.feishu.cn/base/KEA0bePepapdxpsvecFciL4qn3b

---

**最后更新：** 2026-03-23  
**维护者：** 虾王 🦐
