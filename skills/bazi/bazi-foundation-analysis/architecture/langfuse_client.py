"""LangFuse观测追踪 — 全量记录+自动评估"""
import json, os
from datetime import datetime

LANGFUSE_ENABLED = os.environ.get('LANGFUSE_ENABLED', 'false').lower() == 'true'

class LangFuseTracker:
    """观测追踪层——记录每步执行"""
    
    def __init__(self):
        self.logs = []
        
        if LANGFUSE_ENABLED:
            try:
                from langfuse import Langfuse
                self.langfuse = Langfuse(
                    secret_key=os.environ.get('LANGFUSE_SECRET'),
                    public_key=os.environ.get('LANGFUSE_PUBLIC'),
                    host=os.environ.get('LANGFUSE_HOST', 'https://cloud.langfuse.com')
                )
                self.available = True
            except:
                self.available = False
        else:
            self.available = False
    
    def log(self, phase: str, data: dict):
        """记录执行日志"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'data': data
        }
        self.logs.append(entry)
        
        if self.available:
            try:
                self.langfuse.trace(
                    name=f"bazi_{phase}",
                    input=data,
                    metadata={'phase': phase}
                )
            except:
                pass
        
        return entry
    
    def get_report(self) -> str:
        """生成执行报告"""
        total = len(self.logs)
        errors = [l for l in self.logs if 'error' in str(l.get('data', {})).lower()]
        retries = [l for l in self.logs if l.get('phase') == 'retry']
        
        return f"""
执行报告
═══════════════
总步骤: {total}
错误数: {len(errors)}
重试数: {len(retries)}
阶段: {', '.join(set(l['phase'] for l in self.logs))}
        """

class GoldenDataset:
    """Golden Dataset——自动评估准确率"""
    
    def __init__(self):
        self.test_cases = [
            {"query": "七杀透干如何判断", "expected_sections": ["§37.1"], "type": "格局"},
            {"query": "地支相冲的判断方法", "expected_sections": ["§37.2"], "type": "格局"},
            {"query": "从杀格的判定条件", "expected_sections": ["§37.10", "§38.4"], "type": "格局"},
            {"query": "未库对辛金日主是什么库", "expected_sections": ["§40.2"], "type": "墓库"},
            {"query": "分线断法有几条线", "expected_sections": ["§38.5"], "type": "通用"},
            {"query": "三决断的选取规则", "expected_sections": [""], "type": "通用"},  
        ]
    
    def evaluate(self, knowledge_refs: list) -> dict:
        """评估检索结果是否覆盖了预期章节"""
        results = []
        for case in self.test_cases:
            for expected in case['expected_sections']:
                found = any(expected in ref for ref in knowledge_refs)
                results.append({
                    'query': case['query'][:30],
                    'expected': expected,
                    'found': found
                })
        
        pass_count = sum(1 for r in results if r['found'])
        total = len(results)
        return {
            'pass_rate': f"{pass_count}/{total} ({pass_count/total*100:.0f}%)",
            'detail': results
        }
