# API层审计发现（2026-07-05）

## 背景

对 `api/` 和 `backend/` 两套API实现进行全量审计，发现3个功能性Bug。全部已修复。

## 发现的Bug

### M1（P1）: PDF路由未处理农历参数

**文件**: `api/routers/pdf_download.py`

**问题**: `download_pdf` 端点接收 `calendar_type: str` 字段支持阳历/农历，但调用 `call_engine()` 时未传递 `lunar_month`/`lunar_day` 参数，也未做农历→公历转换。若用户选择农历提交，引擎将获得错误公历日期。

```python
# 修复前 — 不传农历参数
engine_result = call_engine(
    request.name, request.gender,
    request.birth_year, request.birth_month, request.birth_day,
    request.birth_hour,
)

# 修复后 — 先转公历再传参
sy, sm, sd = request.birth_year, request.birth_month, request.birth_day
lunar_month, lunar_day = None, None
if request.calendar_type == "lunar":
    lunar_month, lunar_day = request.birth_month, request.birth_day
    from lunar import lunar_to_solar
    solar = lunar_to_solar(request.birth_year, request.birth_month, request.birth_day)
    sy, sm, sd = solar.year, solar.month, solar.day

engine_result = call_engine(
    request.name, request.gender,
    sy, sm, sd, request.birth_hour,
    lunar_month=lunar_month, lunar_day=lunar_day,
)
```

**教训**: 添加任何接受日期输入的新API端点时，必须检查是否需处理农历。所有日期端点应复制 `_ensure_solar_date()` 模式，保持一致性。

---

### M2（P2）: 历史详情未JOIN完整数据

**文件**: `api/routers/history.py` — `get_analysis_detail()`

**问题**: 获取单个分析详情时只SELECT了 `analyses` 主表（id, bazi, status, created_at），未 LEFT JOIN `basic_data` 和 `analysis_results` 表。前端无法获取该历史分析的完整引擎输出。

```python
# 修复前 — 只查主表
cursor = conn.execute(
    "SELECT id, bazi, status, created_at FROM analyses WHERE id = ? AND user_id = ?",
    (analysis_id, user["user_id"]),
)

# 修复后 — JOIN两个子表+JSON字段解析
cursor = conn.execute(
    """SELECT a.id, a.bazi, a.status, a.created_at,
              bd.year_data, bd.month_data, bd.day_data, bd.hour_data, bd.ri_zhu_gan, bd.ri_zhu_wx, bd.ri_zhu_yy,
              bd.tian_gan_notes, bd.di_zhi_notes, bd.cheng_gu_weight, bd.cheng_gu_comment,
              ar.shen_qiang_ruo, ar.cai_xing, ar.ge_ju, ar.xi_yong_shen, ar.energy, ar.da_yun, ar.dimensions
       FROM analyses a
       LEFT JOIN basic_data bd ON a.id = bd.analysis_id
       LEFT JOIN analysis_results ar ON a.id = ar.analysis_id
       WHERE a.id = ? AND a.user_id = ?""",
    (analysis_id, user["user_id"]),
)
```

**教训**: 数据库分表设计意味着 detail endpoint 必须 JOIN 或 N+1 查询。建表时就应该定义好 detail 查询模板，而不是"需要时现加"。

---

### M3（P3）: limit参数未从路由传递

**文件**: `api/routers/history.py` — `get_history()`

**问题**: `analysis_repo.get_user_analyses()` 已接受 `limit: int = 20` 参数，但 `get_history` 路由硬编码 `LIMIT 50` 且不接受客户端传入的限制。

```python
# 修复后
from fastapi import Query

@router.get("/analyses")
async def get_history(
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),  # 可配1~200，默认50
):
    cursor = conn.execute(
        "SELECT ... FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user["user_id"], limit),
    )
```

**教训**: 所有列表端点必须支持 `limit` 和 `offset`（或 `page`）参数。Repository层已有 `limit` 参数时，路由层必须传递下去。

## 审计结论

| 检查项 | 结果 |
|:-------|:-----|
| 引擎引用路径 | ✅ 全部指向 `pipeline_v5`，无旧版(archive/)引用 |
| `api/` 路由 | ✅ 通过 `engine_client.call_engine()` subprocess调用，正确 |
| `backend/` 路由 | ✅ 已修（原引用 `pipeline_v4`，已改为 `pipeline_v5.run_v5()`） |
| 脚本引用 | ✅ `bazi-must-run-engine.sh`等全部用 `pipeline_v5` |
| 数据库操作 | ✅ 参数化SQL，无注入风险 |
| 请求验证 | ✅ Pydantic严格校验 |
| PDF农历 | ✅ 已修 |
| 历史详情 | ✅ 已修 |
| limit参数 | ✅ 已修 |
| 密码安全 | 🟡 使用SHA256而非bcrypt（预存，低优先级） |
