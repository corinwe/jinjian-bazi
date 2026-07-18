#!/usr/bin/env python3
"""gen_report_images.py — 根据八字报告自动生成配图"""
import json, os, sys, subprocess

def main(ds_path, label, output_dir):
    ds = json.load(open(ds_path))
    r = ds['日主']
    w = ds['日主五行']
    eight = ds['八字']
    ti = int(ds['身强弱']['总分'])
    yong = max(100 - ti, 1)
    big_yun = ' '.join([y['干支'] for y in ds['大运'][:4]])
    
    # 五行→色调
    color_map = {'金':('白/金','金属/刀剑/珠宝'),'木':('绿/青','树木/竹林'),
                 '水':('蓝/黑','波浪/江海'),'火':('红/紫','火焰/太阳'),'土':('黄/棕','大地/山峦')}
    colors, elements = color_map.get(w, ('白','星'))
    
    # 生成prompt
    prompt = (
        f"中国传统八字命理象法图，{r}{w}日主{eight}，"
        f"体用比{ti}:{yong}，大运{big_yun}，"
        f"{colors}色调，{elements}元素，"
        f"水墨风格，天干地支符号装饰，阴阳鱼图案，留白意境，"
        f"竖版公众号配图，简约大气，高级灰背景"
    )
    
    # 保存prompt到文件
    prompt_path = os.path.join(output_dir, f'{label}_八字象法图_prompt.txt')
    with open(prompt_path, 'w') as f:
        f.write(prompt)
    print(f'  prompt已保存: {prompt_path}')
    
    # 调用image_generate（通过子进程触发agent tool）
    # 实际执行时由agent在pipeline中调用image_generate
    print(f'  配图prompt: {prompt[:80]}...')
    return prompt

if __name__ == '__main__':
    os.makedirs('/tmp/bazi_report_images', exist_ok=True)
    for dp, label in [('/tmp/weiqiling_ds.json','魏启令'),('/tmp/cheng_ds.json','主母成'),('/tmp/ziyuan_ds.json','子源')]:
        print(f'=== {label} ===')
        main(dp, label, '/tmp/bazi_report_images')
