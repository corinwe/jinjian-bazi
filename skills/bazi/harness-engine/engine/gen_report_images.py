#!/usr/bin/env python3
"""gen_report_images.py — 根据八字报告自动生成配图（火山引擎豆包）"""
import json, os, sys, requests

ARK_KEY = os.environ.get('ARK_API_KEY', '')
ARK_URL = 'https://ark.cn-beijing.volces.com/api/v3/images/generations'
MODEL = 'ep-20260718232041-dslrc'

COLOR_MAP = {'金':('白/金','金属/刀剑/珠宝'),'木':('绿/青','树木/竹林'),
             '水':('蓝/黑','波浪/江海'),'火':('红/紫','火焰/太阳'),'土':('黄/棕','大地/山峦')}

def gen_prompt(ds_path, label, out_dir):
    ds = json.load(open(ds_path))
    r, w = ds['日主'], ds['日主五行']
    eight = ds['八字']
    ti = int(ds['身强弱']['总分'])
    yong = max(100 - ti, 1)
    colors, elements = COLOR_MAP.get(w, ('白','星'))
    big_yun = ' '.join([y['干支'] for y in ds['大运'][:4]])
    
    prompt = (
        f"中国传统八字命理象法图，{r}{w}日主{eight}，"
        f"体用比{ti}:{yong}，大运{big_yun}，"
        f"{colors}色调，{elements}元素，"
        f"水墨风格，天干地支符号装饰，阴阳鱼图案，留白意境，"
        f"竖版公众号配图，简约大气，高级灰背景"
    )
    p_path = os.path.join(out_dir, f'{label}_八字象法图_prompt.txt')
    with open(p_path, 'w') as f:
        f.write(prompt + '\n')
    print(f'  prompt: {prompt[:80]}...')
    return prompt

def generate_image(prompt, out_dir, label):
    if not ARK_KEY:
        print('  ⚠ ARK_API_KEY 未设置，跳过出图')
        return None
    resp = requests.post(ARK_URL,
        headers={'Authorization': f'Bearer {ARK_KEY}', 'Content-Type': 'application/json'},
        json={'model': MODEL, 'prompt': prompt, 'n': 1, 'size': '1920x1920'},
        timeout=60)
    data = resp.json()
    if 'data' in data:
        url = data['data'][0]['url']
        img_resp = requests.get(url, timeout=30)
        img_path = os.path.join(out_dir, f'{label}_八字象法图.jpg')
        with open(img_path, 'wb') as f:
            f.write(img_resp.content)
        print(f'  ✅ 出图: {img_path} ({len(img_resp.content)} bytes)')
        return img_path
    else:
        print(f'  ❌ {data.get("error",{}).get("message","unknown")}')
        return None

if __name__ == '__main__':
    os.makedirs('/tmp/bazi_report_images', exist_ok=True)
    for dp, label in [('/tmp/weiqiling_ds.json','魏启令'),('/tmp/cheng_ds.json','主母成'),('/tmp/ziyuan_ds.json','子源')]:
        print(f'=== {label} ===')
        p = gen_prompt(dp, label, '/tmp/bazi_report_images')
        generate_image(p, '/tmp/bazi_report_images', label)
