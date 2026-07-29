"""工作流引擎 — 确定性状态图，Agent仅作为推理节点"""
import os, json
from typing import TypedDict, Optional, List
from enum import Enum

# 如果用LangGraph（可选，也可用纯函数代替）
# from langgraph.graph import StateGraph, END

from pre_retrieval_hook import PreRetrievalHook
from structured_output import (
    FullAnalysisOutput, GegangAnalysis, LineAnalysis,
    SanJueDuan, ValidationResult, LineJudgment
)
from gatekeeper import GatekeeperValidator

# ====== 状态定义 ======
class AnalysisState(TypedDict):
    """工作流携带的上下文"""
    user_query: str                  # 用户原始提问
    task_type: str                   # 任务类型：格局/喜忌/事业/…
    forced_knowledge: str            # 前置检索注入的知识
    knowledge_refs: List[str]        # 引用列表
    analysis_json: Optional[str]     # LLM输出的JSON
    parsed_output: Optional[FullAnalysisOutput]  # 校验后的输出
    validation: Optional[ValidationResult]       # 校验结果
    retry_count: int                 # 重试次数
    errors: List[str]                # 错误日志

# ====== 确定性节点（代码层） ======
class WorkflowNodes:
    """所有工作流节点——严格区分代码节点和LLM节点"""
    
    def __init__(self):
        self.retriever = PreRetrievalHook()
        self.validator = GatekeeperValidator()
    
    # --- 节点1：前置检索（确定性代码） ---
    def node_retrieve(self, state: AnalysisState) -> dict:
        """强制检索——代码层无条件执行"""
        kb, refs = self.retriever.retrieve(
            query=state['user_query'],
            task_type=state.get('task_type', '通用')
        )
        return {
            'forced_knowledge': kb,
            'knowledge_refs': refs
        }
    
    # --- 节点2：LLM推理（需外部调用） ---
    def node_reasoning(self, state: AnalysisState) -> dict:
        """LLM推理节点——基于已注入知识进行推理
        此节点需要实际的LLM API调用，当前为占位"""
        prompt = f"""
        作为金鉴真人，基于以下强制知识分析八字：
        
        {state['forced_knowledge'][:1000]}
        
        用户请求：{state['user_query']}
        
        请严格按照以下JSON结构输出：
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
            "knowledge_used": ["§37.1", "§38.2"]
        }}
        """
        # 实际LLM调用在此替换
        return {'analysis_json': '{"gegang":...}'}  # 占位
    
    # --- 节点3：校验门禁（确定性代码） ---
    def node_validate(self, state: AnalysisState) -> dict:
        """校验门禁——代码层拦截不合规输出"""
        parsed, result = self.validator.validate_json(
            state.get('analysis_json', '{}')
        )
        return {
            'parsed_output': parsed,
            'validation': result,
            'retry_count': state.get('retry_count', 0) + (0 if result.passed else 1),
            'errors': state.get('errors', []) + result.errors
        }
    
    # --- 节点4：输出处理 ---
    def node_output(self, state: AnalysisState) -> dict:
        """格式化输出"""
        if state.get('parsed_output'):
            output = state['parsed_output']
            result = f"【格局】{output.gegang.gegang_type} {'格成' if output.gegang.success else '格败'}"
            result += f"\n【条件】{output.gegang.condition}"
            result += f"\n【三决断】\n1.{output.san_jueduan.item_1}\n2.{output.san_jueduan.item_2}\n3.{output.san_jueduan.item_3}"
            for line in output.lines:
                result += f"\n【{line.line_type}】{line.judgment} — {line.reason}"
            return {'final_output': result}
        return {'final_output': '分析失败，请重试'}
    
    # --- 节点5：重试/转人工判断 ---
    def node_should_retry(self, state: AnalysisState) -> str:
        """判断是否需要重试"""
        if state.get('validation') and state['validation'].passed:
            return 'output'
        if state.get('retry_count', 0) < self.validator.MAX_RETRIES:
            return 'retry'
        return 'human'

# 主流程
def run_analysis_pipeline(user_query: str, task_type: str = '通用') -> dict:
    """运行完整分析流水线"""
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
        errors=[]
    )
    
    # 硬性流程：检索→推理→校验（最多3次重试）→输出
    state.update(nodes.node_retrieve(state))
    
    for attempt in range(nodes.validator.MAX_RETRIES + 1):
        state.update(nodes.node_reasoning(state))
        state.update(nodes.node_validate(state))
        
        if state.get('validation') and state['validation'].passed:
            break
        
        if attempt < nodes.validator.MAX_RETRIES:
            state['retry_count'] = state.get('retry_count', 0) + 1
    
    state.update(nodes.node_output(state))
    return state
