"""工作流引擎 — 确定性计算引擎 + LLM叙事合成"""
import os, json, sys
from typing import TypedDict, Optional, List

# ── 引擎路径 ──
ENGINE_PATH = "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine"
if ENGINE_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PATH)

from openai import OpenAI
from pre_retrieval_hook import PreRetrievalHook
from structured_output import (
    FullAnalysisOutput, GegangAnalysis, LineAnalysis,
    SanJueDuan, ValidationResult, LineJudgment
)
from gatekeeper import GatekeeperValidator

# ====== 引擎导入 ======
from paipan import get_full_paipan
from shen_qiang_ruo import compute_shen_qiang_ruo
from ge_ju import determine_ge_ju, determine_xi_yong_shen
from shi_shen import get_shi_shen_all_dry
from da_yun import compute_da_yun
from xing_chong_he_hua import check_all_relations
from constants import BaZi, Pillar

# ====== LLM API 配置 ======
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')

def get_llm_client():
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ====== ====== 状态定义 ======
class AnalysisState(TypedDict):
    user_query: str
    task_type: str
    # 引擎计算结果
    bazi_result: Optional[dict]        # paipan.py输出
    shen_qiang_score: Optional[float]  # 身强弱分数
    shen_qiang_label: Optional[str]    # 身强/身弱/从强/从弱
    gegang: Optional[dict]             # 格局判定
    xiyong: Optional[dict]             # 喜用神
    shishen: Optional[dict]            # 十神
    dayun: Optional[list]              # 大运
    # 知识检索
    forced_knowledge: str
    knowledge_refs: List[str]
    # LLM合成
    analysis_json: Optional[str]
    parsed_output: Optional[FullAnalysisOutput]
    validation: Optional[ValidationResult]
    retry_count: int
    errors: List[str]
    final_output: Optional[str]

# ====== 构建八字对象 ======
def build_bazi_object(year: int, month: int, day: int, hour: int, gender: str) -> BaZi:
    """从原始数据构建引擎BaZi对象"""
    paipan_data = get_full_paipan(year, month, day, hour, gender, name="未知")
    
    # paipan输出是dict, 需要转换成BaZi对象
    # 构造Pillar对象
    pillars = {}
    for p_name in ['年柱', '月柱', '日柱', '时柱']:
        p = paipan_data.get(p_name, {})
        pillars[p_name] = Pillar(
            gan=p.get('天干', ''),
            zhi=p.get('地支', ''),
            cang_gan=p.get('藏干', [])
        )
    
    return BaZi(
        year_pillar=pillars['年柱'],
        month_pillar=pillars['月柱'],
        day_pillar=pillars['日柱'],
        hour_pillar=pillars['时柱'],
        gender=gender
    )

# ====== 工作流节点 ======
class WorkflowNodes:
    def __init__(self):
        self.retriever = PreRetrievalHook()
        self.validator = GatekeeperValidator()
        self.llm = get_llm_client()
    
    # --- 节点1：引擎计算（确定性代码） ---
    def node_engine_calc(self, state: AnalysisState) -> dict:
        """调用确定性引擎进行排盘+身强弱+格局+喜用计算"""
        result = {}
        
        try:
            p = get_full_paipan(
                state.get('birth_year', 1980),
                state.get('birth_month', 8),
                state.get('birth_day', 6),
                state.get('birth_hour', 6),
                state.get('gender', '男'), "未知"
            )
            bazi = BaZi(
                Pillar(gan=p['year_pillar']['gan'], zhi=p['year_pillar']['zhi']),
                Pillar(gan=p['month_pillar']['gan'], zhi=p['month_pillar']['zhi']),
                Pillar(gan=p['day_pillar']['gan'], zhi=p['day_pillar']['zhi']),
                Pillar(gan=p['hour_pillar']['gan'], zhi=p['hour_pillar']['zhi']),
                state.get('gender', '男')
            )
            
            score, label, _ = compute_shen_qiang_ruo(bazi)
            geju_main, geju_desc = determine_ge_ju(bazi)
            xiyong = determine_xi_yong_shen(bazi)
            shishen = get_shi_shen_all_dry(bazi)
            
            result['bazi_result'] = {
                'bazi_str': p['bazi'],
                'year_pillar': p['year_pillar'],
                'month_pillar': p['month_pillar'],
                'day_pillar': p['day_pillar'],
                'hour_pillar': p['hour_pillar']
            }
            result['shen_qiang_score'] = score
            result['shen_qiang_label'] = label
            result['gegang'] = {'main': geju_main, 'desc': geju_desc}
            result['xiyong'] = xiyong
            result['shishen'] = shishen
            
        except Exception as e:
            result['errors'] = [f"引擎计算失败: {str(e)[:100]}"]
        
        return result
    
    # --- 节点2：前置检索（确定性代码） ---
    def node_retrieve(self, state: AnalysisState) -> dict:
        kb, refs = self.retriever.retrieve(
            query=state['user_query'],
            task_type=state.get('task_type', '通用')
        )
        return {'forced_knowledge': kb, 'knowledge_refs': refs}
    
    # --- 节点3：LLM叙事合成（基于引擎数据） ---
    def node_reasoning(self, state: AnalysisState) -> dict:
        """LLM仅做叙事合成——引擎已算完所有确定性数据"""
        
        # 构建引擎数据摘要
        bazi = state.get('bazi_result', {})
        gegang = state.get('gegang', {})
        xiyong = state.get('xiyong', ([''], ['']))
        engine_summary = f"""
【引擎计算数据】
八字: {bazi.get('bazi_str', '?')}
身强弱: {state.get('shen_qiang_label', '?')}({state.get('shen_qiang_score', 0)}分)
格局: {gegang.get('main', '?')} — {gegang.get('desc', '?')}
喜用神: {', '.join(xiyong[0]) if isinstance(xiyong, tuple) and xiyong[0] else str(xiyong)}
忌神: {', '.join(xiyong[1]) if isinstance(xiyong, tuple) and len(xiyong) > 1 else ''}
"""
        
        feedback = ""
        if state.get('errors'):
            feedback = "【前次校验未通过】\n" + "\n".join(state['errors']) + "\n请根据报错修正。"
        
        messages = [
            {"role": "system", "content": "你是金鉴真人——顶级八字命理分析专家。以下【引擎计算数据】是确定性的，你无需质疑和重新计算。基于这些数据+【强制知识】合成分析报告。"},
            {"role": "user", "content": f"""
【引擎计算数据】
{engine_summary}

{feedback}

【强制知识】
{state.get('forced_knowledge', '')[:1500]}

【用户请求】
{state['user_query']}

【输出要求】
严格按照以下JSON结构输出，不得包含其他文字：
{{
    "gegang": {{"gegang_type": "...", "success": true/false, "condition": "...", "qingzhuo": "..."}},
    "xiyong": "...",
    "san_jueduan": {{"item_1": "...", "item_2": "...", "item_3": "..."}},
    "lines": [
        {{"line_type": "财线", "judgment": "吉/凶/平", "reason": "..."}},
        {{"line_type": "官杀线", "judgment": "吉/凶/平", "reason": "..."}},
        {{"line_type": "身线", "judgment": "吉/凶/平", "reason": "..."}},
        {{"line_type": "夫妻线", "judgment": "吉/凶/平", "reason": "..."}},
        {{"line_type": "比劫线", "judgment": "吉/凶/平", "reason": "..."}}
    ],
    "knowledge_used": ["§37.1 规则", "§38.2 规则"]
}}
"""}
        ]
        
        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL, messages=messages,
                temperature=0.1, max_tokens=2000
            )
            raw = response.choices[0].message.content.strip()
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()
            return {'analysis_json': raw}
        except Exception as e:
            return {'analysis_json': '{}', 'errors': state.get('errors', []) + [f"LLM失败: {str(e)[:100]}"]}
    
    # --- 节点4：校验门禁（确定性代码） ---
    def node_validate(self, state: AnalysisState) -> dict:
        parsed, result = self.validator.validate_json(state.get('analysis_json', '{}'))
        return {
            'parsed_output': parsed, 'validation': result,
            'retry_count': state.get('retry_count', 0) + (0 if result.passed else 1),
            'errors': state.get('errors', []) + result.errors
        }
    
    # --- 节点5：格式化输出 ---
    def node_output(self, state: AnalysisState) -> dict:
        if state.get('parsed_output'):
            o = state['parsed_output']
            r = f"【身强弱】{state.get('shen_qiang_label', '?')}（{state.get('shen_qiang_score', 0)}分）"
            r += f"\n【格局】{o.gegang.gegang_type}（{'格成' if o.gegang.success else '格败'}）"
            r += f"\n【条件】{o.gegang.condition}\n【喜用】{o.xiyong}"
            r += f"\n【三决断】\n  ① {o.san_jueduan.item_1}\n  ② {o.san_jueduan.item_2}\n  ③ {o.san_jueduan.item_3}"
            for line in o.lines:
                r += f"\n【{line.line_type}】{line.judgment} — {line.reason}"
            r += f"\n【引用】{', '.join(o.knowledge_used)}"
            return {'final_output': r}
        return {'final_output': '⚠️ 分析未通过校验门禁，请检查输入或转人工'}
    
    def node_should_retry(self, state: AnalysisState) -> str:
        if state.get('validation') and state['validation'].passed:
            return 'output'
        if state.get('retry_count', 0) < self.validator.MAX_RETRIES:
            return 'retry'
        return 'human'

# ====== 主流程 ======
def run_analysis_pipeline(user_query: str, task_type: str = '通用',
                          birth_year=1980, birth_month=8, birth_day=6,
                          birth_hour=6, gender='男') -> dict:
    """完整分析流水线：引擎计算→检索→LLM合成→校验→输出"""
    nodes = WorkflowNodes()
    state = AnalysisState(
        user_query=user_query, task_type=task_type,
        birth_year=birth_year, birth_month=birth_month,
        birth_day=birth_day, birth_hour=birth_hour, gender=gender,
        bazi_result=None, shen_qiang_score=None, shen_qiang_label=None,
        gegang=None, xiyong=None, shishen=None, dayun=None,
        forced_knowledge='', knowledge_refs=[],
        analysis_json=None, parsed_output=None, validation=None,
        retry_count=0, errors=[], final_output=None
    )
    
    # Step 1: 引擎计算（确定性代码）
    print('[流水线] Step1: 引擎排盘+身强弱计算...', end=' ')
    state.update(nodes.node_engine_calc(state))
    print(f'身强弱={state.get("shen_qiang_label", "?")} {state.get("shen_qiang_score", 0)}分')
    
    # Step 2: 前置检索
    print('[流水线] Step2: 知识检索...', end=' ')
    state.update(nodes.node_retrieve(state))
    print(f'{len(state["knowledge_refs"])}个引用')
    
    # Step 3-4: LLM合成→校验（最多3次重试）
    for attempt in range(nodes.validator.MAX_RETRIES + 1):
        print(f'[流水线] Step3: LLM叙事合成 (尝试{attempt+1})...', end=' ')
        state.update(nodes.node_reasoning(state))
        print('完成')
        
        print(f'[流水线] Step4: 校验门禁...', end=' ')
        state.update(nodes.node_validate(state))
        v = state.get('validation')
        if v and v.passed:
            print('✅通过')
            break
        errs = v.errors[:3] if v else ['未知错误']
        print(f'❌未通过 ({len(errs)}个错误)')
        for e in errs: print(f'     ❌ {e}')
    
    # Step 5: 输出
    print('[流水线] Step5: 格式化输出...')
    state.update(nodes.node_output(state))
    return state
