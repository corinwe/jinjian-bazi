"""Prefect任务编排 — 定时任务+全链路调度"""
import sys, os, json, logging
from datetime import datetime

# Prefect imports
from prefect import flow, task, deploy
from prefect.task_runners import SequentialTaskRunner

# 添加architecture路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pre_retrieval_hook import PreRetrievalHook
from gatekeeper import GatekeeperValidator
from langfuse_client import LangFuseTracker

# ====== 确定性任务（每个任务都是代码层强制） ======

@task(name="前置检索", retries=1)
def task_retrieve(query: str, task_type: str) -> tuple:
    """Task 1: 强制检索知识库"""
    hook = PreRetrievalHook()
    return hook.retrieve(query, task_type)

@task(name="LLM推理")
def task_reason(knowledge: str, query: str) -> str:
    """Task 2: LLM基于已注入知识推理"""
    # 此处替换为实际LLM调用
    return '{"gegang": {"gegang_type": "食伤生财格", "success": true}}'

@task(name="校验门禁", retries=0)
def task_validate(raw_json: str) -> dict:
    """Task 3: 硬性校验"""
    validator = GatekeeperValidator()
    parsed, result = validator.validate_json(raw_json)
    return {
        'passed': result.passed,
        'errors': result.errors,
        'warnings': result.warnings,
        'parsed': parsed.model_dump() if parsed else None
    }

@task(name="观测追踪")
def task_observe(phase: str, data: dict):
    """Task 4: 观测追踪"""
    tracker = LangFuseTracker()
    return tracker.log(phase, data)

# ====== 工作流编排 ======

@flow(name="八字分析流水线", task_runner=SequentialTaskRunner())
def bazi_analysis_flow(user_query: str, task_type: str = "通用"):
    """完整八字分析工作流"""
    
    # 追踪开始
    task_observe("start", {"query": user_query, "type": task_type})
    
    # Step 1: 前置检索（代码层强制）
    knowledge, refs = task_retrieve(user_query, task_type)
    task_observe("retrieve_done", {"refs": refs})
    
    # Step 2: LLM推理（带重试机制）
    max_retries = 3
    for attempt in range(max_retries):
        raw_output = task_reason(knowledge, user_query)
        
        # Step 3: 校验门禁
        validation = task_validate(raw_output)
        
        if validation['passed']:
            task_observe("success", {"attempt": attempt + 1})
            return {
                'status': 'success',
                'output': validation['parsed'],
                'knowledge_refs': refs,
                'attempts': attempt + 1
            }
        
        # 不通过则追加错误信息重试
        error_msg = "; ".join(validation['errors'])
        knowledge += f"\n【前次校验报错】{error_msg}，请修正后重新输出"
        task_observe("retry", {"attempt": attempt + 1, "errors": validation['errors']})
    
    # 3次都不通过 → 转人工
    task_observe("failed", {"final_errors": validation.get('errors', [])})
    return {
        'status': 'need_human',
        'errors': validation.get('errors', []),
        'partial_output': validation.get('parsed')
    }

@flow(name="知识库更新流水线")
def knowledge_update_flow():
    """定时更新知识库（当SKILL.md变更时）"""
    # 重新向量化SKILL.md
    from chroma_builder import rebuild_knowledge_base
    result = rebuild_knowledge_base()
    return {'status': 'updated', 'chunks': result}

# ====== 定时任务部署 ======
if __name__ == "__main__":
    # 测试运行
    result = bazi_analysis_flow(
        user_query="乾造辛亥，分析2026年事业走势",
        task_type="事业"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
