import json
import requests
from bs4 import BeautifulSoup

# 学校名单
schools = [
    {"name": "北京顺义国际学校", "url": "https://www.isb.bj.edu.cn", "type": "国际学校", "location": "北京"},
    {"name": "上海中学国际部", "url": "https://www.shsid.org", "type": "公办国际部", "location": "上海"},
    # ... 更多学校
]

def collect_school_info(schools):
    results = []
    for school in schools:
        try:
            # 尝试访问官网
            response = requests.get(school['url'], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            # 检查是否包含升学相关关键词
            keywords = ['大学', '录取', 'offer', 'admission', 'college', 'university', '升学', '毕业生']
            found_keywords = [kw for kw in keywords if kw in text]
            
            school_data = {
                "school": school['name'],
                "type": school['type'],
                "location": school['location'],
                "website": school['url'],
                "status": "可访问",
                "found_keywords": found_keywords
            }
            results.append(school_data)
            
        except Exception as e:
            school_data = {
                "school": school['name'],
                "type": school['type'],
                "location": school['location'],
                "website": school['url'],
                "status": f"访问失败: {str(e)}",
                "found_keywords": []
            }
            results.append(school_data)
    
    return results

if __name__ == "__main__":
    # 从文件读取学校名单
    with open('schools_list.json', 'r', encoding='utf-8') as f:
        schools = json.load(f)
    
    results = collect_school_info(schools)
    
    # 保存结果
    with open('schools_scan_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"扫描完成，共处理 {len(results)} 所学校")
    print(f"结果已保存到 schools_scan_results.json")
