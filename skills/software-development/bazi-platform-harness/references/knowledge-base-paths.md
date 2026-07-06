# 知识库路径与推库规范

## 路径

| 项目 | 路径 |
|:-----|:------|
| 知识库根目录 | `/root/weiwuji-knowledge-base` |
| 人物档案 | `07-国学哲学/八字命格/02-人物档案/` |
| 人物档案全路径 | `/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/` |
| GitHub | `git@github.com:corinwe/weiwuji-knowledge-base.git` |

## 编码规则

- 序号 = 当前目录最大号 + 1
- 格式: `{序号}-{姓名}/`
- 例: `57-梦/`

## 推库命令

```bash
cd /root/weiwuji-knowledge-base
git add -A
git commit -m "📊 新增人物档案：{序号}-{姓名}（{八字}）"
git push
```

## 排盘强制门禁

任何八字分析前，必须先跑排盘门禁脚本：

```bash
bash /root/bazi-platform/scripts/bazi-must-run-engine.sh \
  -n <姓名> -g <性别> -y <出生年> -m <出生月> -d <出生日> -h <出生时>
```

输出JSON即为后续分析的唯一数据源，禁止手算日柱/月柱/年柱。
