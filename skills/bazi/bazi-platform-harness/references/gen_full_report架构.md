# gen_full_report.py — 完整21§盲派报告生成器

## 位置
engine/gen_full_report.py

## 功能
读取 rules_mangpai/ 规则文件 + /tmp/{name}_ds.json 数据源
生成完整21§盲派命理报告 → 保存到知识库人物档案目录

## 依赖
- engine/gen_report_images.py（自动出配图）
- rules_mangpai/*.yaml（16个规则文件）
- /tmp/{name}_ds.json（数据源）

## 调用方式
```bash
python3 engine/gen_full_report.py
```

## 21§标准格式
1. 一页总览 2. 格局分析 3. 身强弱 4. 喜用神
5. 灾祸疾病 6. 性格 7. 外貌 8. 财富(含等级+发财年份)
9. 置业 10. 事业(含等级+升官年份) 11. 学业(含文昌+印分析)
12. 婚姻 13. 子女 14. 健康 15. 六亲
16. 人生关键事件表 17. 事件总表 18. 大运精析
19. 三决断 20. 运程总评 21. 五行补充 22. 人生建议
23. 佩戴推荐
