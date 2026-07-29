"""触发层 + 上下文隔离 + LangFuse集成 — 缺失组件补全"""
import sys, os, json, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from langfuse_client import LangFuseTracker

# ====== 上下文隔离（每任务新Session） ======
class TaskSession:
    """每任务隔离的会话上下文——杜绝Memory污染"""
    
    def __init__(self):
        self.session_id = uuid.uuid4().hex[:12]
        self.created_at = None
        self.context = {}
    
    def reset(self):
        """任务结束后彻底重置"""
        self.session_id = uuid.uuid4().hex[:12]
        self.context = {}
    
    def set(self, key, value):
        self.context[key] = value
    
    def get(self, key, default=None):
        return self.context.get(key, default)

# ====== 工具白名单（各场景专属工具列表） ======
SCENE_TOOLS = {
    '事业': {'allowed': ['engine_calc', 'knowledge_retrieve', 'llm_reason'], 'blocked': []},
    '婚姻': {'allowed': ['engine_calc', 'knowledge_retrieve', 'llm_reason'], 'blocked': []},
    '财富': {'allowed': ['engine_calc', 'knowledge_retrieve', 'llm_reason'], 'blocked': []},
    '健康': {'allowed': ['engine_calc', 'knowledge_retrieve', 'llm_reason'], 'blocked': []},
    '通用': {'allowed': ['engine_calc', 'knowledge_retrieve', 'llm_reason'], 'blocked': []},
}

# ====== Trigger层（API+定时任务） ======
class TaskDispatcher:
    """触发层——接收请求，路由到正确的场景工作流"""
    
    def __init__(self):
        self.tracker = LangFuseTracker()
        self.session = TaskSession()
    
    def dispatch(self, query: str, scene: str = '通用') -> dict:
        """路由请求到对应场景"""
        self.session.reset()  # 每任务重置上下文
        
        # 记录开始
        self.tracker.log('dispatch', {
            'session_id': self.session.session_id,
            'query': query[:50],
            'scene': scene
        })
        
        # 路由验证
        if scene not in SCENE_TOOLS:
            return {'status': 'error', 'message': f'未知场景: {scene}'}
        
        # 注入场景配置
        self.session.set('scene', scene)
        self.session.set('tools_whitelist', SCENE_TOOLS[scene]['allowed'])
        
        return {'status': 'routed', 'session_id': self.session.session_id, 'scene': scene}
    
    def get_session(self) -> TaskSession:
        return self.session

# ====== 快速测试 ======
if __name__ == '__main__':
    d = TaskDispatcher()
    result = d.dispatch('乾造辛亥事业分析', '事业')
    print(f'Dispatch: {json.dumps(result, ensure_ascii=False)}')
    print(f'Session隔离: {d.get_session().session_id}')
