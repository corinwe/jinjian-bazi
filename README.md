# 金鉴真人·八字命理确定性规则引擎

**零大模型推理 · 全确定性计算 · 21§完整输出 · 320+自动化测试**

---

## 架构

```
用户浏览器 → FastAPI (api/) → 规则引擎 (engine/) → 结构化JSON/文本
                                  ↓
                               SQLite (database/)
```

## 引擎规模

| 模块 | 文件 | 行数 | 规则覆盖 |
|:----|:-----|:----:|:---------|
| 身强弱 | `shen_qiang_ruo.py` | 292 | 印40/0/0+比劫全算+燥土+从弱50分 |
| 财星 | `cai_xing.py` | 133 | 年干8分/月干12分+藏干比例 |
| 格局·喜用·调候 | `ge_ju.py` | 218 | 正八格+伟人格+调候用神 |
| 大运 | `da_yun.py` | 193 | 阳男阴女顺逆+10年一步+喜用排序 |
| 十神 | `shi_shen.py` | 122 | 生克关系+阴阳定正偏 |
| 神煞 | `shen_sha.py` | 279 | 22种神煞查表 |
| 排盘 | `paipan.py` | 206 | 年/月/日/时柱+节气分界 |
| 纳音/空亡 | `pipeline_v5.py` | 56行 | 完整60甲子+六甲旬空亡 |
| 事业v2 | `career_v2.py` | 378 | 36命格+伟人格+官杀分析+五行行业 |
| 财富v2 | `wealth_v2.py` | 198 | 五层动态体系+围克折扣+财库 |
| 婚姻v2 | `marriage_v2.py` | 351 | 配偶星定位+四大信号+夫妻宫十神+质量评分 |
| 学历v2 | `education_v2.py` | 318 | 年柱三档法+文昌双轨+六步排查+学校等级 |
| 健康v2 | `health_v2.py` | 1607 | 五行过三+七杀断病+偏印淤堵+流年预测 |
| 子女v2 | `children_v2.py` | 1546 | 十二长生基数+出生年份推理+父母合参 |
| 灾祸/化解 | `misfortune_analysis.py` | 256 | 四大神煞+恶神能量表+五行补运 |
| 8维度评分 | `dimensions_v2.py` | 222 | 校准版0-10分+大运赋能 |
| 21§编排 | `pipeline_v5.py` | 518 | 全部21§模块化输出 |
| 综合引擎 | `comprehensive_v2.py` | 829 | 整合所有模块统一入口 |
| **总计** | **35个.py文件** | **12,437行** | |

## 快速启动

### 开发环境

```bash
cd /root/bazi-platform
./run.sh
```

### 生产部署

```bash
docker build -t jinjian-bazi .
docker run -p 8000:8000 jinjian-bazi
```

### 访问

- 前端界面: http://localhost:8000/
- API文档: http://localhost:8000/docs
- 调试接口: POST /api/v1/engine/debug

## API用法

```bash
curl -X POST http://localhost:8000/api/v1/engine/debug \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","gender":"男","birth_year":1980,"birth_month":7,"birth_day":15,"birth_hour":4}'
```

返回21§完整JSON，包含：八字、身强弱、财星、格局、大运、事业、财富、婚姻、学历、健康、子女、灾祸、8维度评分等。

## 测试

```bash
cd engine
python3 tests/test_full_suite.py
# 320/320 全部通过
```

## 规则来源

所有规则基于九龙道长原始素材逐字精读翻译，来源包括：
- 素材11+17（财富规则）
- 素材12（学历规则）  
- 素材5行337（燥土规则）
- 公众号文章2026-06-25校准

**核心原则：零自创断事逻辑 — 每个断语必须有原始素材行号依据。**

## License

MIT
