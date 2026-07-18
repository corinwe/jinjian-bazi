#!/usr/bin/env python3
"""gen_report_images.py v3 — 八字象法全图：八字五行生克有机整体意境"""
import json, os, requests, shutil

ARK_KEY = os.environ.get('ARK_API_KEY', '')
ARK_URL = 'https://ark.cn-beijing.volces.com/api/v3/images/generations'
MODEL = 'ep-20260718232041-dslrc'

GAN_WX = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
ZHI_WX = {'申':'金','酉':'金','寅':'木','卯':'木','亥':'水','子':'水','巳':'火','午':'火','辰':'土','戌':'土','丑':'土','未':'土'}
WX_COLOR = {'金':'白/银/金','木':'绿/青/翠','水':'蓝/墨/黑','火':'红/橙/紫','土':'黄/棕/赭'}
WX_ELE = {'金':'金属/刀剑/珠宝','木':'树木/花草/竹','水':'溪流/江海/云','火':'火焰/阳光/灯','土':'山峦/大地/沙'}
DZ_SHAPE = {'申':'刀剑','酉':'宝珠','寅':'参天古松','卯':'低矮藤蔓花草灌木','亥':'深潭','子':'蜿蜒长河',
            '巳':'熔炉窑火','午':'烈日当空','辰':'水库湿地','戌':'砖窑燥土城墙','丑':'冻土寒冰','未':'田园沃土'}


def build_prompt(ds):
    """为每个人八字构建独一无二的有机整体意境"""
    b = ds['八字'].split()
    G = [p[0] for p in b]; Z = [p[1] for p in b]
    rizhu = ds['日主']; ti = int(ds['身强弱']['总分']); yong = max(100-ti,1)
    
    # 每个地支的正确形态
    dz_shape = {'寅':'参天古松(高树)','卯':'低矮藤蔓花草灌木(非高树)','辰':'水库湿地',
                '巳':'熔炉窑火','午':'烈日当空','未':'田园沃土',
                '申':'金属刀剑','酉':'宝珠','戌':'砖窑燥土城墙(非高山)','亥':'深潭',
                '子':'蜿蜒长河','丑':'冻土寒冰'}
    
    # 逐柱描述
    col_desc = []
    for i,(g,z) in enumerate(zip(G,Z)):
        pos = ['年柱','月柱','日柱','时柱'][i]
        gw = GAN_WX.get(g,'')
        zw = ZHI_WX.get(z,'')
        zd = dz_shape.get(z,'')
        col_desc.append(f'{pos}{g}{z}:{g}为{WX_ELE.get(gw,"")}({WX_COLOR.get(gw,"")})，{z}为{zd}')
    
    wxc = {}
    for g,z in zip(G,Z):
        for ch in [g,z]:
            wx = GAN_WX.get(ch,'') or ZHI_WX.get(ch,'')
            if wx: wxc[wx] = wxc.get(wx,0)+1
    wx_rank = sorted(wxc.items(), key=lambda x:-x[1])
    main_wx = wx_rank[0][0] if wx_rank else '金'
    main_color = WX_COLOR.get(main_wx, '白')
    
    relations = []
    wx_set = set(w for w,_ in wx_rank)
    if '金' in wx_set and '水' in wx_set: relations.append('金属缝隙涌清泉(金生水)')
    if '水' in wx_set and '木' in wx_set: relations.append('溪流旁藤蔓花草繁茂(水生木)')
    if '木' in wx_set and '火' in wx_set: relations.append('藤蔓枯枝燃烧化火焰(木生火)')
    if '火' in wx_set and '土' in wx_set: relations.append('火焰熄灭归砖窑燥土(火生土)')
    if '土' in wx_set and '金' in wx_set: relations.append('砖窑燥土中蕴藏金属(土生金)')
    if '水' in wx_set and '火' in wx_set: relations.append('溪流水汽蒸腾与火焰交融(水克火亦相济)')
    
    prompt = (
        f"中国传统水墨山水画八字象法全图，八字{ds['八字']}，日主{rizhu}居中。"
        f"四柱描述：{'；'.join(col_desc)}。"
        f"注意：卯木为低矮藤蔓花草灌木非高树，戌土为砖窑燥土城墙非高山。"
        f"生克关系：{'；'.join(relations)}。"
        f"体用比{ti}:{yong}通过山水比例暗示。"
        f"天干符号悬浮空中对应的自然元素中，地支符号坐落大地对应的地貌。"
        f"整体画面有机统一，八个字不是孤立标签而是自然融合在一幅山水里，竖版公众号配图。"
    )
    return prompt


def go(ds_path, label, out_dir, kb_dir):
    ds = json.load(open(ds_path))
    prompt = build_prompt(ds)
    
    p_path = os.path.join(out_dir, f'{label}_prompt.txt')
    with open(p_path, 'w') as f:
        f.write(prompt+'\n')
    print(f'  prompt: {prompt[:80]}...')
    
    if not ARK_KEY:
        print('  ⚠ 无ARK_KEY')
        return
    
    # 火山引擎出图
    resp = requests.post(ARK_URL,
        headers={'Authorization': f'Bearer {ARK_KEY}', 'Content-Type': 'application/json'},
        json={'model': MODEL, 'prompt': prompt, 'n': 1, 'size': '1920x1920'},
        timeout=120)
    data = resp.json()
    
    if 'data' in data:
        url = data['data'][0]['url']
        img_data = requests.get(url, timeout=60).content
        img_path = os.path.join(out_dir, f'{label}_八字象法全图.jpg')
        with open(img_path, 'wb') as f:
            f.write(img_data)
        shutil.copy2(img_path, os.path.join(kb_dir, f'{label}_八字象法全图.jpg'))
        print(f'  ✅ {len(img_data)//1024}KB')
    else:
        print(f'  ❌ {data.get("error",{}).get("message","")}')


if __name__ == '__main__':
    os.makedirs('/tmp/bazi_v3', exist_ok=True)
    KB = '/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案'
    for dp, lb, sd in [
        ('/tmp/weiqiling_ds.json','魏启令','01-家主-魏启令'),
        ('/tmp/cheng_ds.json','主母成','02-主母-成'),
        ('/tmp/ziyuan_ds.json','子源','03-少爷-子源'),
    ]:
        print(f'=== {lb} ===')
        go(dp, lb, '/tmp/bazi_v3', os.path.join(KB, sd))
