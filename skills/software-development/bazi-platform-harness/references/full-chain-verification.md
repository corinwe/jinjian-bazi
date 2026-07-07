# 全链路引用链验证协议

## 目的
每次修Bug/归档旧版/新增模块后，模拟一个八字从用户输入到最终报告输出的完整流程，逐层检查每个模块是否正确链接、引用无断层。

## 验证步骤

### Step 1: 29模块批量导入验证
```python
cd projects/bazi-platform/engine && python3 -c "
modules = ['paipan','lunar','constants','shen_qiang_ruo','shi_shen','ge_ju',
    'cai_xing','energy','da_yun','character','education','shi_shang',
    'xing_chong_he_hua','shen_sha','family','misfortune_analysis',
    'comprehensive_v2','career_v2','children_v2','health_v2','wealth_v2',
    'marriage_v2','liu_nian_v2','narrative_integration','narratives',
    'report_generator','generate_deep_report','_gen_detail_analysis',
    'pipeline_v5']
for mod in modules:
    exec(f'from {mod} import *')
    print(f'  ✅ {mod}')
print(f'✅ 全部 {len(modules)} 个模块引用链正常!')
"
```

### Step 2: CLI入口 → pipeline_v5完整运行
```bash
cd projects/bazi-platform/engine && \
python3 pipeline_v5.py --name 验证 --gender 男 --year 1990 --month 5 --day 15 --hour 10 --json 2>/dev/null | \
python3 -c "
import sys,json
d=json.load(sys.stdin)
result=d.get('result',{})
# 21§完整性检查
expected=['sec_1_overview','sec_2_ge_ju','sec_3_shen_qiang_ruo','sec_4_xi_yong',
    'sec_5_zai_huo','sec_6_character','sec_7_appearance','sec_8_wealth',
    'sec_9_property','sec_10_career','sec_11_education','sec_12_marriage',
    'sec_13_children','sec_14_health','sec_15_family','sec_16_events',
    'sec_17_da_yun_detail','sec_18_verdicts','sec_19_overall',
    'sec_20_wu_xing_advice','sec_21_advice']
missing=[s for s in expected if s not in result]
print(f'✅ 21§全部存在' if not missing else f'❌ 缺失: {missing}')
print(f'身强弱: {result.get(\"sec_3_shen_qiang_ruo\",{}).get(\"score\")}分')
print(f'格局: {result.get(\"sec_2_ge_ju\",{}).get(\"main\")}')
"
```

### Step 3: 报告生成器验证
```bash
cd projects/bazi-platform/engine && python3 -c "
from pipeline_v5 import run_pipeline
from report_generator import generate_report
result = run_pipeline('验证','男','庚','申','辛','巳','甲','午','丙','寅',birth_year=1990)
report = generate_report(result, '验证', '男')
lines = report.split(chr(10))
print(f'报告: {len(lines)}行')
print(f'署名: {\"金鉴真人\" in report}')
"
```

### Step 4: 双后端API路径验证
```bash
# 路径A(api): engine_client → subprocess → pipeline_v5
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && python3 -c "
import sys, os
sys.path.insert(0, 'engine')
from api.services.engine_client import call_engine
print('✅ api路径: engine_client 导入正常')
"

# 路径B(backend): 直接import pipeline_v5
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && python3 -c "
import sys, os
sys.path.insert(0, 'engine')
sys.path.insert(0, 'backend')
from app.routers.analyze import run_full_analysis_v4
print('✅ backend路径: run_full_analysis_v4 导入正常')
"
```

### Step 5: pytest全量测试
```bash
cd projects/bazi-platform/engine && python3 -m pytest tests/ -v --tb=short
```
必须9/9全部通过。

## 验证通过标准
- [ ] 29/29模块导入正常
- [ ] 21§全部存在 + 核心数据非空
- [ ] 报告≥1000行 + 含金鉴真人署名
- [ ] api + backend 两套API路径均可导入
- [ ] pytest 9/9通过
