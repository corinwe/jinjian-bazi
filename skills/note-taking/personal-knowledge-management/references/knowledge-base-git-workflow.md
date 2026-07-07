# 知识库 Git 初始化与每日推送工作流

## 首次初始化（新机器/新克隆）

```bash
# 克隆已有仓库
cd /root
git clone git@github.com:corinwe/weiwuji-knowledge-base.git

# 或从零初始化新仓库
cd /root/weiwuji-knowledge-base
git init
git remote add origin git@github.com:corinwe/weiwuji-knowledge-base.git
```

## 目录结构（2026-06-14已验证）

```
/root/weiwuji-knowledge-base/
├── 07-国学哲学/
│   └── 八字命格/
│       └── 人物档案/           # 八字分析报告存放处
│           └── {姓名}_完整命理深析报告_v{X.Y}_{YYYYMMDD}.md
├── 09-投资财富/               # 投资分析笔记
└── ...其他领域目录
```

## 每日推送流程

```bash
cd /root/weiwuji-knowledge-base

# 1. 如果有远程，先拉取避免冲突
git pull --rebase origin master 2>/dev/null || true

# 2. 添加所有变更
git add -A

# 3. 提交
git commit -m "新增/更新：{内容简述}（{YYYY-MM-DD}）"

# 4. 推送到 GitHub
git push -u origin master
```

## 注意事项

- SSH key 路径：`~/.ssh/id_ed25519`（已配好 GitHub 公钥）
- 首次 push 用 `git push -u origin master` 建立跟踪
- 后续直接用 `git push`
- 如果 knowledge-base 目录不存在 → 先 clone
- 如果某个领域目录不存在（如 `07-国学哲学/八字命格/人物档案`）→ 用 `mkdir -p` 创建
- 仓库不含 .git → 说明未初始化，需执行初始化流程
