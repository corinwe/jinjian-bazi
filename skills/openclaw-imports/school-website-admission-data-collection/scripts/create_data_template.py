import json

# 标准化数据模板
data_template = {
    "school": "学校名称",
    "type": "国际学校/公办国际部/民办国际高中",
    "location": "城市",
    "year": 2025,
    "total_graduates": "毕业生总数",
    "offer_data": [
        {
            "university": "大学名称",
            "country": "国家",
            "major": "专业",
            "count": "录取人数",
            "scholarship": "奖学金信息"
        }
    ]
}

# 创建示例数据
example_data = {
    "school": "北京顺义国际学校",
    "type": "国际学校",
    "location": "北京",
    "year": 2024,
    "total_graduates": 120,
    "offer_data": [
        {
            "university": "哈佛大学",
            "country": "美国",
            "major": "计算机科学",
            "count": 2,
            "scholarship": "全额奖学金"
        },
        {
            "university": "剑桥大学",
            "country": "英国",
            "major": "经济学",
            "count": 3,
            "scholarship": "部分奖学金"
        }
    ]
}

if __name__ == "__main__":
    # 保存模板
    with open('data_template.json', 'w', encoding='utf-8') as f:
        json.dump(data_template, f, ensure_ascii=False, indent=2)
    
    # 保存示例
    with open('example_school_data.json', 'w', encoding='utf-8') as f:
        json.dump(example_data, f, ensure_ascii=False, indent=2)
    
    print("数据模板已创建：data_template.json")
    print("示例数据已创建：example_school_data.json")
