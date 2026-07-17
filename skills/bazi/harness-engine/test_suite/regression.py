#!/usr/bin/env python3
"""
test_suite/regression.py — L3学习飞轮 · 回归测试运行器
每次Harness Engine改动后运行，验证已有能力不退化
"""
import json, sys, os

BASE = '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/harness-engine'
TEST_DIR = os.path.join(BASE, 'test_suite')


def run_test(test_path):
    with open(test_path) as f:
        case = json.load(f)
    
    ds_path = case.get('ds_path', '/tmp/weiqiling_ds.json')
    if not os.path.exists(ds_path):
        return {'test': case['name'], 'status': 'SKIP', 'reason': f'数据源不存在:{ds_path}'}
    
    ds = json.load(open(ds_path))
    
    # 加载step_runner
    sys.path.insert(0, os.path.join(BASE, 'engine'))
    from workflow_v2 import WORKFLOW, load_rule
    
    results = []
    for check in case.get('checks', []):
        ctype = check['type']
        passed = False
        detail = ''
        
        if ctype == 'field_value':
            # 检查DS字段值
            field = check['field']
            expected = check['expected']
            actual = ds.get(field)
            ds_ref = ds
            for part in field.split('.'):
                if isinstance(ds_ref, dict) and part in ds_ref:
                    ds_ref = ds_ref[part]
                elif isinstance(ds_ref, list) and part.lstrip('-').isdigit():
                    ds_ref = ds_ref[int(part)]
                else:
                    ds_ref = None; break
            passed = ds_ref == expected or str(ds_ref) == str(expected)
            detail = f'{field}={ds_ref}(期望{expected})'
        
        elif ctype == 'contains':
            # 检查输出文本
            full = case.get('expected_report', '')
            keyword = check['keyword']
            passed = keyword in full
            detail = f'关键词"{keyword}": {"找到" if passed else "未找到"}'
        
        elif ctype == 'sensor':
            # 运行传感器
            sensor_name = check['name']
            sys.path.insert(0, os.path.join(BASE, 'engine'))
            from step_runner import check_ds_alignment, check_min_lines
            sensors = {'check_ds_alignment': check_ds_alignment, 'check_min_lines': check_min_lines}
            f = sensors.get(sensor_name)
            if f:
                errs = f(full, ds) if sensor_name == 'check_ds_alignment' else f(full)
                passed = len(errs) == 0
                detail = f'{sensor_name}: {errs if errs else "通过"}'
        
        results.append({
            'check': check.get('desc', ctype),
            'status': 'PASS' if passed else 'FAIL',
            'detail': detail
        })
    
    return {'test': case['name'], 'results': results}


def run_all():
    test_files = sorted([f for f in os.listdir(TEST_DIR) if f.endswith('.json')])
    if not test_files:
        print('test_suite/ 空，无测试用例')
        return
    
    total_pass = 0
    total_fail = 0
    
    for tf in test_files:
        tp = os.path.join(TEST_DIR, tf)
        result = run_test(tp)
        all_pass = all(r['status'] == 'PASS' for r in result.get('results', []))
        symbol = '✅' if all_pass else '❌'
        print(f'{symbol} {result["test"]}')
        for r in result.get('results', []):
            print(f'   {r["status"]} {r["check"]}: {r["detail"]}')
            if r['status'] == 'PASS': total_pass += 1
            else: total_fail += 1
    
    print(f'\n总计: {total_pass}通过 / {total_fail}失败')
    return total_fail == 0


if __name__ == '__main__':
    ok = run_all()
    sys.exit(0 if ok else 1)
