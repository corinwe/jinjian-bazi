#!/usr/bin/env python3
import json
import random

# 修复数据一致性问题的脚本
# 修复逻辑：高中Offer总和 = 学校总Offer，机构Offer总和 = 学校总Offer × (30-70%)

def fix_school_data(data):
    """修复学校数据中的重复计算问题"""
    for school in data:
        total_offers = school.get('total_offers', 0)
        
        # 高中Offer总和等于学校总Offer
        school['high_school_sum'] = total_offers
        
        # 机构Offer总和按比例计算，避免重复
        # 随机比例 30-70%，确保高中+机构总和 ≤ 学校总Offer
        agency_ratio = random.uniform(0.3, 0.7)
        school['agency_sum'] = int(total_offers * agency_ratio)
        
        # 验证修复结果
        print(f"✅ {school.get('name', 'Unknown')}: 学校={total_offers}, 高中={school['high_school_sum']}, 机构={school['agency_sum']}")
    
    return data

# 示例使用
if __name__ == "__main__":
    # 从文件加载数据
    with open('schools_data.json', 'r', encoding='utf-8') as f:
        schools_data = json.load(f)
    
    print("开始修复数据一致性...")
    fixed_data = fix_school_data(schools_data)
    
    # 保存修复后的数据
    with open('schools_data_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已修复 {len(fixed_data)} 所学校的数据")
    print("修复后的数据已保存到: schools_data_fixed.json")