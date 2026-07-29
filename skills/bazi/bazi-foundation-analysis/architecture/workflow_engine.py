"""工作流引擎 — 确定性状态图，集成真实LLM API"""
import os, json
from typing import TypedDict, Optional, List
from openai import OpenAI

from pre_retrieval_hook import PreRetrievalHook
from structured_output import (
    FullAnalysisOutput, GegangAnalysis, LineAnalysis,
    SanJueDuan, ValidationResult, LineJudgment
)
from gatekeeper import GatekeeperValidator

# ====== LLM API 配置 ======
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')

def get_llm_client():
    """获取LLM客户端"""
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ====== 状态定义 ======
class AnalysisState(TypedDict):
    user_query: str
    task_type: str
    forced_knowledge: str
    knowledge_refs: List[str]
    analysis_json: Optional[str]
    parsed_output: Optional[FullAnalysisOutput]
    validation: Optional[ValidationResult]
    retry_count: int
    errors: List[str]
    final_output: Optional[str]

# ====== 提示词模板 ======
SYSTEM_PROMPT = """你是金鉴真人——顶级八字命理分析专家。
你的所有判断必须以下方案件【强制知识】为唯一依据，不得使用未提供的信息。
你必须严格按照指定的JSON结构输出。"""

def build_analysis_prompt(user_query: str, forced_knowledge: str, feedback: str = "") -> list:
    """构建推理提示词"""
    user_content = f"""
【强制知识】
{forced_knowledge[:2000]}

【用户请求】
{user_query}

{feedback}

【输出要求】
请严格按照以下JSON结构输出，不要包含任何其他文字：
{{
    "gegang": {{"gegang_type": "格局类型", "success": true/false, "condition": "成/败条件", "qingzhuo": "清浊评定"}},
    "xiyong": "喜用忌一句话",
    "san_jueduan": {{"item_1": "第一条决断", "item_2": "第二条决断", "item_3": "第三条决断"}},
    "lines": [
        {{"line_type": "财线", "judgment": "吉/凶/平", "reason": "判断依据"}},
        {{"line_type": "官杀线", "judgment": "吉/凶/平", "reason": "判断依据"}},
        {{"line_type": "身线", "judgment": "吉/凶/平", "reason": "判断依据"}},
        {{"line_type": "夫妻线", "judgment": "吉/凶/平", "reason": "判断依据"}},
        {{"line_type": "比劫线", "judgment": "吉/凶/平", "reason": "判断依据"}}
    ],
    "knowledge_used": ["§37.1 规则", "§38.2 规则"]
}}
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

# ====== 工作流节点 ======
class WorkflowNodes:
    def __init__(self):
        self.retriever = PreRetrievalHook()
        self.validator = GatekeeperValidator()
        self.llm = get_llm_client()
    
    def node_retrieve(self, state: AnalysisState) -> dict:
        """Node 1: 前置强制检索（代码层）"""
        kb, refs = self.retriever.retrieve(
            query=state['user_query'],
            task_type=state.get('task_type', '通用')
        )
        return {'forced_knowledge': kb, 'knowledge_refs': refs}
    
    def node_reasoning(self, state: AnalysisState) -> dict:
        """Node 2: LLM推理（真实API调用）"""
        # 构建错误反馈（如有前次失败）
        feedback = ""
        if state.get('errors'):
            feedback = "【前次校验未通过】\n" + "\n".join(state['errors'])
            feedback += "\n请根据以上报错修正你的输出，确保符合要求。"
        
        messages = build_analysis_prompt(
            state['user_query'],
            state.get('forced_knowledge', ''),
            feedback
        )
        
        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            raw = response.choices[0].message.content.strip()
            # 提取JSON（处理模型可能输出markdown代码块的情况）
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()
            
            return {'analysis_json': raw}
            
        except Exception as e:
            return {'analysis_json': '{}', 'errors': state.get('errors', []) + [f"LLM API调用失败: {str(e)[:100]}"]}
    
    def node_validate(self, state: AnalysisState) -> dict:
        """Node 3: 校验门禁（代码层）"""
        parsed, result = self.validator.validate_json(
            state.get('analysis_json', '{}')
        )
        return {
            'parsed_output': parsed,
            'validation': result,
            'retry_count': state.get('retry_count', 0) + (0 if result.passed else 1),
            'errors': state.get('errors', []) + result.errors
        }
    
    def node_output(self, state: AnalysisState) -> dict:
        """Node 4: 格式化输出"""
        if state.get('parsed_output'):
            o = state['parsed_output']
            result = f"【格局】{o.gegang.gegang_type}（{'格成' if o.gegang.success else '格败'}）\n"
            result += f"【条件】{o.gegang.condition}\n"
            result += f"【喜用】{o.xiyong}\n"
            result += f"【三决断】\n  ① {o.san_jueduan.item_1}\n  ② {o.san_jueduan.item_2}\n  ③ {o.san_jueduan.item_3}\n"
            for line in o.lines:
                result += f"【{line.line_type}】{line.judgment} — {line.reason}\n"
            result += f"【引用】{', '.join(o.knowledge_used)}"
            return {'final_output': result}
        return {'final_output': '⚠️ 分析失败，未通过校验门禁，请检查输入或转人工处理'}
    
    def node_should_retry(self, state: AnalysisState) -> str:
        if state.get('validation') and state['validation'].passed:
            return 'output'
        if state.get('retry_count', 0) < self.validator.MAX_RETRIES:
            return 'retry'
        return 'human'

# ====== ====== 主流程 ======
def run_analysis_pipeline(user_query: str, task_type: str = '通用') -> dict:
    """运行完整分析流水线——检索→LLM推理→校验→输出"""
    nodes = WorkflowNodes()
    state = AnalysisState(
        user_query=user_query,
        task_type=task_type,
        forced_knowledge='',
        knowledge_refs=[],
        analysis_json=None,
        parsed_output=None,
        validation=None,
        retry_count=0,
        errors=[],
        final_output=None
    )
    
    # Step 1: 强制检索（代码层，无条件执行）
    print(f'[流水线] Step1: 前置检索...', end=' ')
    state.update(nodes.node_retrieve(state))
    print(f'{len(state["knowledge_refs"])}个引用')
    
    # Step 2-3: LLM推理→校验（最多3次重试）
    for attempt in range(nodes.validator.MAX_RETRIES + 1):
        print(f'[流水线] Step2: LLM推理 (尝试{attempt+1}/{nodes.validator.MAX_RETRIES+1})...', end=' ')
        state.update(nodes.node_reasoning(state))
        print('完成')
        
        print(f'[流水线] Step3: 校验门禁...', end=' ')
        state.update(nodes.node_validate(state))
        v = state.get('validation')
        if v and v.passed:
            print('✅通过')
            break
        else:
            errs = v.errors[:3] if v else ['未知错误']
            print(f'❌未通过 ({len(errs)}个错误)')
            for e in errs:
                print(f'     ❌ {e}')
            if attempt < nodes.validator.MAX_RETRIES:
                print(f'[流水线] 重试中...')
    
    # Step 4: 输出
    print(f'[流水线] Step4: 格式化输出...')
    state.update(nodes.node_output(state))
    
    return state
