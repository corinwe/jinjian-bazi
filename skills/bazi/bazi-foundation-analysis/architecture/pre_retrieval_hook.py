"""前置强制检索钩子 — 代码层无条件检索知识库"""
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "/root/.hermes/profiles/jinjian-zhenren/data/chroma_db"
TOP_K = 8

class PreRetrievalHook:
    """在Agent收到任务前，强制检索相关知识注入上下文"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_collection("jinjian-bazi-knowledge")
    
    def get_required_sections(self, task_type: str) -> list:
        """根据任务类型返回需要加载的知识章节"""
        section_map = {
            '格局': ['§37', '§38', '§40', '经典-子平真诠', '经典-渊海子平', '经典-杨清娟盲派'],
            '喜忌': ['§37', '§38', '经典-穷通宝鉴', '经典-杨清娟盲派'],
            '事业': ['§37', '§39', '经典-子平真诠', '经典-杨清娟盲派'],
            '财富': ['§37', '§39', '§40', '经典-三命通会', '经典-盲派做功', '经典-杨清娟盲派'],
            '婚姻': ['§37', '§39', '经典-三命通会', '经典-盲派寻根基'],
            '健康': ['§37', '§34', '经典-滴天髓'],
            '流年': ['§37', '§38', '经典-三命通会', '经典-渊海子平', '经典-杨清娟盲派'],
            '合参': ['§38', '§39', '经典-子平真诠', '经典-滴天髓', '经典-杨清娟盲派'],
            '墓库': ['§40', '经典-三命通会', '经典-盲派做功'],
            '模式': ['§39', '经典-渊海子平', '经典-段建业盲派'],
            '通用': ['§37', '§38', '§35', '经典-穷通宝鉴', '经典-滴天髓', '经典-子平真诠', '经典-三命通会', '经典-渊海子平', '经典-杨清娟盲派', '经典-段建业盲派', '经典-盲派做功', '经典-盲派寻根基'],
        }
        return section_map.get(task_type, ['§37', '§38'])
    
    def retrieve(self, query: str, task_type: str = '通用') -> tuple[str, list]:
        """检索相关知识并格式化"""
        required = self.get_required_sections(task_type)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=TOP_K,
            where={"section": {"$in": required}}
        )
        
        knowledge_parts = []
        references = []
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            section = meta.get('section', '?')
            title = meta.get('title', '?')
            knowledge_parts.append(f"[知识块{i+1}] §{section} {title}\n{doc[:500]}")
            references.append(f"{section}/{title}")
        
        knowledge_block = f"""
【强制知识 — 你必须严格遵循以下内容】
任务类型: {task_type}
检索依据: {query}

{chr(10).join(knowledge_parts)}

【工作守则】
1. 以上已提供最新最准确的知识，你无需自行检索
2. 你的唯一依据是以上知识，不得使用未提供的信息
3. 严格按照SOP步骤推理
4. 输出中必须引用你使用的知识来源（引用章节号）
"""
        return knowledge_block, references

# 使用示例
if __name__ == "__main__":
    hook = PreRetrievalHook()
    kb, refs = hook.retrieve("七杀透干如何处理", "格局")
    print(kb[:300])
    print(f"引用: {refs}")
