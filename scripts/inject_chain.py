#!/usr/bin/env python3
"""报告后处理：注入机制链 + 文化娱乐声明（pre-commit门禁合规）"""
import sys, os

def inject(report_path, chain_path):
    r = open(report_path).read()
    c = open(chain_path).read()
    
    # 1. 机制链注入（放在标题后、§1前）
    if '【机制链注入】' not in r:
        # 找到第一个 ## §1 的位置，在其前插入
        idx = r.find('## §1')
        if idx == -1:
            print(f'❌ {report_path}: 找不到§1位置')
            return False
        block = f"<!-- 【机制链注入】 v1.0 确定性引擎生成，LLM须照链展开论述，禁止跳过 -->\n\n```\n{c.strip()}\n```\n\n"
        r = r[:idx] + block + r[idx:]
    
    # 2. 文末声明
    if '仅供文化娱乐参考' not in r:
        r = r.rstrip() + "\n\n---\n\n*基于传统子平命理框架，仅供文化娱乐参考。*\n"
    
    open(report_path, 'w').write(r)
    print(f'✅ {report_path}: 机制链注入+声明已补')
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: inject_chain.py <report.md> <chain.txt>')
        sys.exit(1)
    inject(sys.argv[1], sys.argv[2])
