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
DZ_SHAPE = {'申':'刀剑','酉':'宝珠','寅':'古松','卯':'藤蔓','亥':'深潭','子':'长河',
            '巳':'熔炉','午':'烈日','辰':'湿地','戌':'火山','丑':'冻土','未':'田园'}


def build_prompt(ds):
    """为每个人八字构建独一无二的有机整体意境"""
    b = ds['八字'].split()
    G = [p[0] for p in b]; Z = [p[1] for p in b]
    rizhu = ds['日主']; ti = int(ds['身强弱']['总分']); yong = max(100-ti,1)
    
    # 五行统计
    wxc = {}
    for g,z in zip(G,Z):
        for ch in [g,z]:
            wx = GAN_WX.get(ch,'') or ZHI_WX.get(ch,'')
            if wx: wxc[wx] = wxc.get(wx,0)+1
    wx_rank = sorted(wxc.items(), key=lambda x:-x[1])  # 主次排序
    
    # 画布主色调 = 最多五行
    main_wx = wx_rank[0][0] if wx_rank else '金'
    main_color = WX_COLOR.get(main_wx, '白')
    
    # 画面主要元素描述（有机整体）
    elements = []
    for wx, cnt in wx_rank:
        if cnt >= 2: elements.append(f'{WX_ELE[wx]}为主要元素')
        elif cnt >= 1: elements.append(f'点缀{WX_ELE[wx]}')
    
    # 五行的生克关系视觉化
    relations = []
    wx_set = set(w for w,_ in wx_rank)
    if '金' in wx_set and '水' in wx_set: relations.append('金属山石缝隙中涌出清泉(金生水)')
    if '水' in wx_set and '木' in wx_set: relations.append('溪流两岸草木繁茂(水生木)')
    if '木' in wx_set and '火' in wx_set: relations.append('枯木燃烧化作火焰(木生火)')
    if '火' in wx_set and '土' in wx_set: relations.append('火焰熄灭归于尘土(火生土)')
    if '土' in wx_set and '金' in wx_set: relations.append('大地深处蕴藏金属矿脉(土生金)')
    
    prompt = (
        f"一幅中国传统水墨山水画，八字命理象法全图："
        f"八字{ds['八字']}，日主{rizhu}居中，其他七字符散落画面各方位，"
        f"整体色调以{main_color}为主，融合{', '.join([WX_COLOR.get(w,w) for w,c in wx_rank])}，"
        f"画面核心关系：{'；'.join(relations)}，"
        f"画中元素：{', '.join([f'{WX_ELE[w]}' for w,c in wx_rank])}，"
        f"天干符号悬浮空中，地支符号坐落大地，体用比{ti}:{yong}通过山水比例暗示，"
        f"阴阳鱼图案为背景底纹，每柱的天地人三才关系通过上下位置展现，"
        f"整体是一幅有机相连的生命画卷，每个符号与其他符号有互动关系，"
        f"传统中国水墨风格，意境深远，细节丰富，竖版公众号配图，高级质感"
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
