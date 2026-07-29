"""Prefect任务编排 + 完整流水线演示"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_engine import run_analysis_pipeline
from langfuse_client import LangFuseTracker, GoldenDataset

def test_full_pipeline():
    """测试完整端到端八字分析流水线"""
    print('╔═══════════════════════════════════════════════╗')
    print('║  金鉴真人 · 商业化八字分析流水线 v1.0       ║')
    print('╚═══════════════════════════════════════════════╝')
    
    # 测试用例：乾造辛亥
    test_query = "乾造 庚申 癸未 辛亥 辛卯，1980年8月6日6时生，男，分析2026年事业走势"
    
    print(f'\n📋 命盘: {test_query[:40]}...')
    print(f'📊 场景: 事业\n')
    
    # 运行完整流水线
    result = run_analysis_pipeline(test_query, "事业")
    
    print('\n══════════════════════════════════════')
    print('📋 流水线结果')
    print('══════════════════════════════════════')
    print(f'状态: {"✅ 通过" if result.get("parsed_output") else "❌ 未通过"}')
    print(f'重试次数: {result.get("retry_count", 0)}')
    print(f'知识引用: {result.get("knowledge_refs", [])[:3]}')
    
    if result.get('final_output'):
        print(f'\n📝 分析输出:\n{result["final_output"]}')
    
    # Golden Dataset 评估
    print('\n══════════════════════════════════════')
    print('📊 Golden Dataset 评估')
    print('══════════════════════════════════════')
    gd = GoldenDataset()
    eval_result = gd.evaluate(result.get('knowledge_refs', []))
    print(f'检索覆盖率: {eval_result["pass_rate"]}')
    
    # LangFuse记录
    tracker = LangFuseTracker()
    tracker.log('pipeline_complete', {
        'query': test_query,
        'passed': bool(result.get('parsed_output')),
        'refs': result.get('knowledge_refs', []),
        'retries': result.get('retry_count', 0)
    })
    print(f'\n📈 观测追踪: {tracker.get_report()}')
    
    return result

if __name__ == "__main__":
    test_full_pipeline()
