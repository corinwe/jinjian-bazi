"""工作流引擎 v2.0 — LangGraph状态图 + Instructor强制结构化输出"""
import os, json, sys
from typing import TypedDict, Optional, List, Literal
from openai import OpenAI

# ── 引擎路径 ──
ENGINE_PATH = "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine"
if ENGINE_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PATH)

# ── LangGraph ──
from langgraph.graph import StateGraph, END

# ── Instructor（强制结构化输出） ──
import instructor
from pydantic import BaseModel, Field
from enum import Enum

# ── 金鉴引擎 ──
from paipan import get_full_paipan
from constants import BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from ge_ju import determine_ge_ju, determine_xi_yong_shen
from shi_shen import get_shi_shen_all_dry

# ── 自研模块 ──
from pre_retrieval_hook import PreRetrievalHook
from gatekeeper import GatekeeperValidator

# ====== LLM API ======
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')
client = instructor.from_openai(OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL))

# ====== 结构化输出模型（Instructor强制） ======
class LineJudgment(str, Enum):
    吉 = "吉"
    凶 = "凶"
    平 = "平"

class LineOutput(BaseModel):
    line_type: str = Field(description="线类型: 财线/官杀线/身线/夫妻线/比劫线")
    judgment: LineJudgment = Field(description="明确吉凶")
    reason: str = Field(description="判断依据", min_length=5)

class SanJue(BaseModel):
    item_1: str = Field(description="第一条决断", min_length=5)
    item_2: str = Field(description="第二条决断", min_length=5)
    item_3: str = Field(description="第三条决断", min_length=5)

class GegangOut(BaseModel):
    gegang_type: str = Field(min_length=2)
    success: bool
    condition: str = Field(min_length=5)

class AnalysisReport(BaseModel):
    """Instructor强制LLM必须完整输出此结构"""
    gegang: GegangOut
    xiyong: str = Field(min_length=5)
    san_jueduan: SanJue
    lines: List[LineOutput] = Field(min_length=5, max_length=5)
    knowledge_used: List[str] = Field(min_length=1)

# ====== 场景定义（路由隔离） ======
SCENE_CONFIGS = {
    '事业': {
        'system_prompt': '你是金鉴真人·事业专精分析师。专注事业趋势、压力来源、机遇判断。',
        'required_sections': ['§37', '§38', '§39'],
        'max_tokens': 1500,
    },
    '婚姻': {
        'system_prompt': '你是金鉴真人·婚姻专精分析师。专注感情质量、夫妻互动、配偶特征。',
        'required_sections': ['§37', '§39'],
        'max_tokens': 1500,
    },
    '财富': {
        'system_prompt': '你是金鉴真人·财富专精分析师。专注财源走势、置业时机、风险管理。',
        'required_sections': ['§37', '§39', '§40'],
        'max_tokens': 1500,
    },
    '健康': {
        'system_prompt': '你是金鉴真人·健康专精分析师。专注体质走势、薄弱系统、养生建议。',
        'required_sections': ['§37', '§34'],
        'max_tokens': 1500,
    },
    '通用': {
        'system_prompt': '你是金鉴真人·八字命理分析师。你必须按照21§标准格式输出完整报告。',
        'required_sections': ['§37', '§38', '§39', '§40', '§35'],
        'max_tokens': 4000,
    },
}

# ====== 状态定义 ======
class WorkflowState(TypedDict):
    user_query: str
    task_type: str              # 场景路由key
    # 出生数据（由run_analysis_pipeline传入）
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    gender: str
    # 引擎数据
    bazi_str: str
    shen_qiang_label: str
    shen_qiang_score: float
    gegang_main: str
    gegang_desc: str
    xiyong_str: str
    # 知识
    forced_knowledge: str
    knowledge_refs: List[str]
    # LLM输出
    analysis_report: Optional[AnalysisReport]
    # 校验
    retry_count: int
    validation_passed: bool
    validation_errors: List[str]
    final_output: str

# ====== Node 1: 路由校验（Pre-hook） ======
def node_validate_input(state: WorkflowState) -> dict:
    """输入合法性校验"""
    errors = []
    if not state.get('user_query') or len(state['user_query']) < 10:
        errors.append("用户请求过短")
    task_type = state.get('task_type', '通用')
    if task_type not in SCENE_CONFIGS:
        errors.append(f"未知场景: {task_type}")
    return {'validation_errors': errors}

# ====== Node 2: 引擎计算（确定性代码） ======
def node_engine(state: WorkflowState) -> dict:
    """确定性引擎计算"""
    try:
        # 从state获取出生数据（通过state传递的参数，实际需要从user_query解析或外部传入）
        p = get_full_paipan(
            state.get('birth_year', 1980),
            state.get('birth_month', 8),
            state.get('birth_day', 6),
            state.get('birth_hour', 6),
            state.get('gender', '男'), '未知'
        )
        bazi = BaZi(
            Pillar(gan=p['year_pillar']['gan'], zhi=p['year_pillar']['zhi']),
            Pillar(gan=p['month_pillar']['gan'], zhi=p['month_pillar']['zhi']),
            Pillar(gan=p['day_pillar']['gan'], zhi=p['day_pillar']['zhi']),
            Pillar(gan=p['hour_pillar']['gan'], zhi=p['hour_pillar']['zhi']),
            '男'
        )
        score, label, _ = compute_shen_qiang_ruo(bazi)
        geju_main, geju_desc = determine_ge_ju(bazi)
        xiyong_tup = determine_xi_yong_shen(bazi)
        
        return {
            'bazi_str': p['bazi'],
            'shen_qiang_label': label,
            'shen_qiang_score': score,
            'gegang_main': geju_main,
            'gegang_desc': geju_desc,
            'xiyong_str': f"喜用:{','.join(xiyong_tup[0])} 忌:{','.join(xiyong_tup[1])}" if isinstance(xiyong_tup, tuple) else str(xiyong_tup)
        }
    except Exception as e:
        return {'validation_errors': [f"引擎失败: {str(e)[:100]}"]}

# ====== Node 3: 前置检索（确定性代码） ======
def node_retrieve(state: WorkflowState) -> dict:
    hook = PreRetrievalHook()
    scene_config = SCENE_CONFIGS.get(state.get('task_type', '通用'), SCENE_CONFIGS['通用'])
    kb, refs = hook.retrieve(state['user_query'], state.get('task_type', '通用'))
    # 标记为【强制知识·不可跳过】
    kb_blocked = f"""
┌─────────────────────────────────────────────────────┐
│ 【强制知识 — 物理注入·不可跳过】                    │
│ 以下知识为官方知识库检索结果，LLM不得忽略或替换      │
└─────────────────────────────────────────────────────┘
{chr(10).join(['【知识块' + str(i+1) + '】' + r for i, r in enumerate(refs[:3])])}

详细内容:
{kb[:1500]}
"""
    return {'forced_knowledge': kb_blocked, 'knowledge_refs': refs}

# ====== Node 4: LLM推理（Instructor强制结构化） ======
def node_llm_reason(state: WorkflowState) -> dict:
    """LLM推理——Instructor强制输出AnalysisReport"""
    scene_config = SCENE_CONFIGS.get(state.get('task_type', '通用'), SCENE_CONFIGS['通用'])
    
    error_feedback = ""
    if state.get('validation_errors'):
        error_feedback = "\n".join([f"【前次错误】{e}" for e in state['validation_errors']])
    
    user_prompt = f"""
【流派声明】
本报告以子平法（格局法+旺衰法）为骨架，
融合九龙道长特色理论（一位为真、十神吉恶平比例），
以盲派做功理论为实证视角。
综合之：子平为主、九龙为佐、盲派为验。

【引擎数据·确定性】
八字: {state.get('bazi_str', '?')}
身强弱: {state.get('shen_qiang_label', '?')} ({state.get('shen_qiang_score', 0)}分)
格局: {state.get('gegang_main', '?')} — {state.get('gegang_desc', '?')}
喜用: {state.get('xiyong_str', '?')}

【强制知识】
{state.get('forced_knowledge', '')[:1000]}

{error_feedback}

【用户请求】
{state['user_query']}

【输出要求】
请基于以上引擎数据和强制知识，输出完整21§八字分析报告。
报告开头必须注明流派依据（子平为主、九龙为佐、盲派为验）。
§8财富分析的破财风险必须根据此八字的实际喜忌动态判定（不可写死为"比劫"）。
报告末尾注明基于传统命理框架，仅供文化娱乐参考。
"""
    
    try:
        report = client.chat.completions.create(
            model=LLM_MODEL,
            response_model=AnalysisReport,  # ← Instructor强制
            messages=[
                {"role": "system", "content": scene_config['system_prompt'] + "你必须输出严格的结构化JSON，不得遗漏任何字段。"},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=scene_config['max_tokens'],
        )
        return {'analysis_report': report, 'retry_count': state.get('retry_count', 0)}
    except Exception as e:
        err_msg = f"Instructor LLM调用失败: {str(e)[:100]}"
        return {'validation_errors': state.get('validation_errors', []) + [err_msg]}

# ====== Node 5: 校验门禁（代码层） ======
def node_gatekeeper(state: WorkflowState) -> dict:
    """后置校验门禁"""
    report = state.get('analysis_report')
    if not report:
        return {'validation_passed': False, 'validation_errors': ['无分析报告']}
    
    errors = []
    try:
        if not report.gegang or not report.gegang.gegang_type:
            errors.append("格局类型缺失")
        if not report.san_jueduan or not report.san_jueduan.item_1:
            errors.append("三决断缺失")
        required_lines = ['财线', '官杀线', '身线', '夫妻线', '比劫线']
        present = [l.line_type for l in report.lines]
        for rl in required_lines:
            if rl not in present:
                errors.append(f"缺少{rl}")
        if not report.knowledge_used:
            errors.append("无知识引用")
    except Exception as e:
        errors.append(f"校验异常: {str(e)[:80]}")
    
    passed = len(errors) == 0
    return {
        'validation_passed': passed,
        'validation_errors': errors if not passed else state.get('validation_errors', [])
    }

# ====== Node 6: 格式化输出 ======
def node_output(state: WorkflowState) -> dict:
    """格式化21§报告输出"""
    report = state.get('analysis_report')
    if report and state.get('validation_passed'):
        # 直接输出LLM生成的完整21§报告
        # (report object包含了21§的全部内容)
        r = f"""# 金鉴真人·八字命理分析报告
生成引擎：金鉴真人商业化分析流水线 v2.0
分析流派：子平法(格局+旺衰)为主 · 九龙特色理论为佐 · 盲派做功为验

---

## §1 一页总览表
**八字**: {state.get('bazi_str', '?')}
**日主**: {state.get('shen_qiang_label', '?')}({state.get('shen_qiang_score', 0)}分)
**格局**: {state.get('gegang_main', '?')} — {state.get('gegang_desc', '?')}
**喜用**: {report.xiyong}

## §2 格局分析
{report.gegang.gegang_type}({'格成' if report.gegang.success else '格败'})
{report.gegang.condition}

## §18 三决断
① {report.san_jueduan.item_1}
② {report.san_jueduan.item_2}
③ {report.san_jueduan.item_3}

---
基于传统子平命理框架，仅供文化娱乐参考。
"""
        return {'final_output': r}
    return {'final_output': '❌ 分析未通过校验门禁，已转人工处理'}

# ====== 条件边 ======
def decide_retry(state: WorkflowState) -> Literal['retry', 'output', 'human']:
    """判断下一节点"""
    if state.get('validation_passed'):
        return 'output'
    if state.get('retry_count', 0) < 3:
        return 'retry'
    return 'human'

# ====== 构建状态图（LangGraph） ======
def build_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)
    
    # 注册节点
    workflow.add_node("input_validate", node_validate_input)
    workflow.add_node("engine_calc", node_engine)
    workflow.add_node("knowledge_retrieve", node_retrieve)
    workflow.add_node("llm_reason", node_llm_reason)
    workflow.add_node("gatekeeper", node_gatekeeper)
    workflow.add_node("output", node_output)
    workflow.add_node("human_intervention", lambda s: s)  # 转人工(占位)
    
    # 定义边——硬性顺序
    workflow.set_entry_point("input_validate")
    workflow.add_edge("input_validate", "engine_calc")
    workflow.add_edge("engine_calc", "knowledge_retrieve")
    workflow.add_edge("knowledge_retrieve", "llm_reason")
    workflow.add_edge("llm_reason", "gatekeeper")
    
    # 条件边：校验不通过则重试或转人工
    workflow.add_conditional_edges(
        "gatekeeper",
        decide_retry,
        {
            "retry": "llm_reason",    # 回到LLM重新生成
            "output": "output",        # 通过→输出
            "human": "human_intervention"  # 3次不过→转人工
        }
    )
    
    workflow.add_edge("output", END)
    workflow.add_edge("human_intervention", END)
    
    return workflow.compile()

# ====== 主入口 ======
def run_analysis_pipeline(user_query: str, task_type: str = '通用',
                          birth_year=1980, birth_month=8, birth_day=6,
                          birth_hour=6, gender='男') -> dict:
    """运行完整分析流水线"""
    app = build_workflow()
    
    initial = WorkflowState(
        user_query=user_query,
        task_type=task_type,
        birth_year=birth_year, birth_month=birth_month,
        birth_day=birth_day, birth_hour=birth_hour, gender=gender,
        bazi_str='', shen_qiang_label='', shen_qiang_score=0.0,
        gegang_main='', gegang_desc='', xiyong_str='',
        forced_knowledge='', knowledge_refs=[],
        analysis_report=None,
        retry_count=0, validation_passed=False,
        validation_errors=[], final_output=''
    )
    
    result = app.invoke(initial, {"recursion_limit": 15})
    
    print(f'[流水线] 场景: {task_type}')
    print(f'[流水线] 引擎: {result.get("bazi_str","?")} | 身{result.get("shen_qiang_label","?")} {result.get("gegang_main","?")}')
    print(f'[流水线] 重试: {result.get("retry_count",0)}次')
    print(f'[流水线] 校验: {"✅通过" if result.get("validation_passed") else "❌未通过"}')
    print(f'[流水线] 知识: {len(result.get("knowledge_refs",[]))}个引用')
    
    return result
