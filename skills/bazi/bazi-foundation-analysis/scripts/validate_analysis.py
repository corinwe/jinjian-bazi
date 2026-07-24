#!/usr/bin/env python3
"""validate_analysis.py — 命理分析质量验证工具
从MingLi-Bench题库中抽取与命主相关的题目，
验证分析质量（选择题+标准答案对比）。
"""
import json, sys, os, random

TOTAL_POOL_PATH = '/root/weiwuji-knowledge-base/07-国学哲学/八字命格/00-原始素材/命理评测题库_MingLiBench_160题.json'

def load_pool():
    with open(TOTAL_POOL_PATH) as f:
        return json.load(f)

def filter_by_bazi(pool, bazi_str):
    """根据八字大致匹配相关题目（按年柱筛选）"""
    year_gan = bazi_str.split()[0][0] if bazi_str else ''
    matched = []
    for q in pool:
        bi = q.get('birth_info', {})
        # 简单匹配：同一年出生
        if bi.get('year'):
            # 年干相同或相近
            pass
        matched.append(q)
    return matched  # 实际应用中需要更精确的匹配

def validate_response(question, model_answer, correct_answer):
    """验证单题"""
    return model_answer.strip().upper() == correct_answer.strip().upper()

def run_validation(model_responses, questions):
    """运行批量验证"""
    total = len(questions)
    correct = 0
    results = []
    for q, resp in zip(questions, model_responses):
        is_correct = validate_response(q, resp, q['answer'])
        if is_correct:
            correct += 1
        results.append({
            'id': q['id'],
            'question': q['question'][:40],
            'expected': q['answer'],
            'got': resp,
            'pass': is_correct,
            'category': q.get('category', '')
        })
    return {
        'total': total,
        'correct': correct,
        'accuracy': round(correct/total*100, 1) if total > 0 else 0,
        'pass_80': (correct/total >= 0.8) if total > 0 else False,
        'results': results
    }

if __name__ == '__main__':
    pool = load_pool()
    print(f'题库: {len(pool)}题')
    
    # 示例：按类别抽样
    category = sys.argv[1] if len(sys.argv) > 1 else '婚姻'
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    sampled = [q for q in pool if q.get('category') == category][:sample_size]
    print(f'分类[{category}]: {len(sampled)}题')
    for q in sampled:
        print(f'  {q["id"]}: {q["question"][:50]}... → 答案({q["answer"]})')
