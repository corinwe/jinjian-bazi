import json

# 基于已知信息的学校名单
schools_list = [
    # 北京地区
    {"name": "北京顺义国际学校", "url": "https://www.isb.bj.edu.cn", "type": "国际学校", "location": "北京"},
    {"name": "北京京西学校", "url": "https://www.wab.edu", "type": "国际学校", "location": "北京"},
    {"name": "北京德威英国国际学校", "url": "https://beijing.dulwich.org", "type": "国际学校", "location": "北京"},
    {"name": "北京四中国际部", "url": "https://www.bhsfic.com", "type": "公办国际部", "location": "北京"},
    {"name": "北京十一学校国际部", "url": "https://www.bnds.cn", "type": "公办国际部", "location": "北京"},
    {"name": "北京师范大学附属实验中学国际部", "url": "https://www.sdsz.com.cn", "type": "公办国际部", "location": "北京"},
    {"name": "北京人大附中国际部", "url": "https://www.rdfz.cn", "type": "公办国际部", "location": "北京"},
    
    # 上海地区
    {"name": "上海美国学校", "url": "https://www.saschina.org", "type": "国际学校", "location": "上海"},
    {"name": "上海协和国际外籍人员子女学校", "url": "https://www.concordiashanghai.org", "type": "国际学校", "location": "上海"},
    {"name": "上海德威外籍人员子女学校", "url": "https://shanghai.dulwich.org", "type": "国际学校", "location": "上海"},
    {"name": "上海中学国际部", "url": "https://www.shsid.org", "type": "公办国际部", "location": "上海"},
    {"name": "上海外国语大学附属外国语学校国际部", "url": "https://www.sfls.cn", "type": "公办国际部", "location": "上海"},
    {"name": "上海市世界外国语中学国际部", "url": "https://www.wflms.cn", "type": "民办国际高中", "location": "上海"},
    {"name": "上海平和双语学校国际部", "url": "https://www.shphschool.com", "type": "民办国际高中", "location": "上海"},
    
    # 广州/深圳地区
    {"name": "广州美国人国际学校", "url": "https://www.aisgz.org", "type": "国际学校", "location": "广州"},
    {"name": "深圳国际交流学院", "url": "https://www.scie.com.cn", "type": "民办国际高中", "location": "深圳"},
    {"name": "深圳外国语学校国际部", "url": "https://www.swis.cn", "type": "公办国际部", "location": "深圳"},
    {"name": "华南师范大学附属中学国际部", "url": "https://www.hsfz.net.cn", "type": "公办国际部", "location": "广州"},
    
    # 其他地区
    {"name": "成都树德中学国际部", "url": "https://www.sdzx.net", "type": "公办国际部", "location": "成都"},
    {"name": "杭州外国语学校剑桥高中", "url": "https://www.chinahw.net", "type": "公办国际部", "location": "杭州"},
    {"name": "南京外国语学校国际部", "url": "https://www.nfls.com.cn", "type": "公办国际部", "location": "南京"},
    {"name": "武汉外国语学校国际部", "url": "https://www.wfls.com.cn", "type": "公办国际部", "location": "武汉"}
]

if __name__ == "__main__":
    # 保存学校名单
    with open('schools_list.json', 'w', encoding='utf-8') as f:
        json.dump(schools_list, f, ensure_ascii=False, indent=2)
    
    # 按地区分组统计
    location_stats = {}
    type_stats = {}
    
    for school in schools_list:
        location = school['location']
        school_type = school['type']
        
        location_stats[location] = location_stats.get(location, 0) + 1
        type_stats[school_type] = type_stats.get(school_type, 0) + 1
    
    print(f"学校名单已生成，共 {len(schools_list)} 所学校")
    print(f"地区分布：{location_stats}")
    print(f"类型分布：{type_stats}")
    print(f"名单已保存到 schools_list.json")
