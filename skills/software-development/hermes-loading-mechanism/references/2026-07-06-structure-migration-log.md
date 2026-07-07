# 2026-07-06 结构迁移日志

## 最终结构

```
~/.hermes/profiles/jinjian-zhenren/
├── SOUL.md                         ← 系统级身份+3条系统铁律
├── HERMES.md                       ← 项目级SOP（8条bazi铁律+工作流）
├── projects/bazi-platform/         ← bazi代码（engine/api/frontend/scripts/）
│   └── .git/                       ← GitHub: corinwe/jinjian-bazi
├── skills/                         ← 实际技能文件（symlink → 实际文件）
├── memories/USER.md                ← 老板画像
└── .gitignore                      ← 追踪bazi文件，忽略Hermes系统文件
```

## 迁移命令速查

```bash
# 排盘
bash projects/bazi-platform/scripts/bazi-must-run-engine.sh -n姓名 -g性别 -y年 -m月 -d日 -h时

# 测试
cd projects/bazi-platform/engine/tests && python3 validate_all.py

# 四柱校验
python3 projects/bazi-platform/scripts/pillar-verify.py

# 推库
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && git push
# 或直接 profile根目录下：
cd /root/.hermes/profiles/jinjian-zhenren && git push
```

## 知识库HERMES.md位置

| 路径 | 负责人 | 内容 |
|:-----|:-------|:-----|
| `weiwuji-knowledge-base/HERMES.md` | 金久（别碰） | 知识库全局：结构/分工/沉淀流程 |
| `weiwuji-knowledge-base/07-国学哲学/八字命格/HERMES.md` | 金鉴真人 | bazi排盘SOP |

## 关键教训

1. **bazi-platform的.git不能放projects/bazi-platform/里** — 要放在profile根目录（追踪SOUL.md/HERMES.md/skills/projects/全部）
2. **config.yaml不能进git** — 含API密钥，gitignore排除
3. **skills/必须直接存在** — symlink导致skill_manage无法写入，实际文件才能被修改
4. **路径引用分3层**：
   - profile根目录内 → 用 `projects/bazi-platform/` 相对路径
   - skills/内的文档 → 用 `projects/bazi-platform/` 相对路径
   - 脚本(scripts/) → 用可执行相对路径
5. **知识库只动07-国学哲学/八字命格/** — 根目录的HERMES.md归金久
