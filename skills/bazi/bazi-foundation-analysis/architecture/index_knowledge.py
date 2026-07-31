"""
知识库向量化脚本 — 将技能库+五经典文档向量化存入Chroma
用法: python3 index_knowledge.py
"""
import os, re, hashlib
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "/root/.hermes/profiles/jinjian-zhenren/data/chroma_db"
COLLECTION = "jinjian-bazi-knowledge"

# 需要向量化的文件源
SOURCES = [
    # 主技能文件
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/SKILL.md",
        "type": "skill",
    },
    # 五经典文档
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/classic_qiongtongbaojian_20260729.md",
        "type": "classic",
    },
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/classic_ditiansui_20260729.md",
        "type": "classic",
    },
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/classic_zipingzhenquan_20260729.md",
        "type": "classic",
    },
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/classic_sanmingtonghui_20260729.md",
        "type": "classic",
    },
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/classic_yuanhaiziping_20260729.md",
        "type": "classic",
    },
    # 方法论参考
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/references/ziping-theory-schools_20260722.md",
        "type": "methodology",
    },
    {
        "path": "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-foundation-analysis/architecture/report_template_21s.md",
        "type": "sop",
    },
]

def chunk_by_sections(content: str, source_path: str, source_type: str):
    """按##或§标题切分知识块"""
    # 提取标题行
    lines = content.split('\n')
    chunks = []
    current_title = os.path.basename(source_path)
    current_buf = []
    
    def flush():
        nonlocal current_title, current_buf
        text = '\n'.join(current_buf).strip()
        if len(text) > 30:
            chunks.append({
                'text': text,
                'title': current_title[:60],
                'section': _extract_section(current_title),
            })
        current_buf = []
    
    for line in lines:
        # 检测标题: ## 或 §开头
        if re.match(r'^#{1,3}\s+', line) or re.match(r'^§\d+', line):
            flush()
            current_title = line.strip().lstrip('#').strip()
        else:
            current_buf.append(line)
    flush()
    return chunks

def _extract_section(title: str) -> str:
    """从标题提取§编号"""
    m = re.search(r'§(\d+)', title)
    if m:
        return f"§{m.group(1)}"
    # 经典文档用固定标识
    for key in ['穷通宝鉴', '滴天髓', '子平真诠', '三命通会', '渊海子平']:
        if key in title:
            return f"经典-{key}"
    return "§37"

def index_all():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # 使用默认embedding（否则需API）
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    # 先删除旧collection重建（避免重复）
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    
    collection = client.create_collection(
        name=COLLECTION,
        embedding_function=ef
    )
    
    total = 0
    for src in SOURCES:
        path = src['path']
        if not os.path.exists(path):
            print(f"⚠️ 跳过(不存在): {path}")
            continue
        
        with open(path, encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_by_sections(content, path, src['type'])
        
        ids, docs, metadatas = [], [], []
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{path}:{i}:{chunk['text'][:50]}".encode()).hexdigest()[:16]
            ids.append(chunk_id)
            docs.append(chunk['text'])
            metadatas.append({
                'source': os.path.basename(path),
                'title': chunk['title'],
                'section': chunk['section'],
                'type': src['type'],
            })
        
        if ids:
            collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
            total += len(ids)
            print(f"✅ {os.path.basename(path)}: {len(ids)}块 (累计{total})")
    
    print(f"\n🎯 总计: {total}个知识块入库")
    
    # 验证
    count = collection.count()
    print(f"Chroma实际count: {count}")
    return total

if __name__ == "__main__":
    index_all()
