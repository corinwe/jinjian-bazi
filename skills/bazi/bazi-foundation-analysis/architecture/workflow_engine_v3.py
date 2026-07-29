"""工作流引擎 v3.1 — 直接生成21§标准报告（无LangGraph，更稳定）"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine")
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
from paipan import get_full_paipan
from constants import BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from ge_ju import determine_ge_ju, determine_xi_yong_shen
from pre_retrieval_hook import PreRetrievalHook

STD_21 = [
    "§1 一页总览表","§2 格局分析","§3 身强弱详解","§4 喜用神详解",
    "§5 灾祸/疾病/搬迁专项","§6 性格分析","§7 身材外貌分析",
    "§8 财富分析","§9 置业/买房分析","§10 事业分析",
    "§11 学历分析","§12 婚姻/感情分析","§13 子女分析",
    "§14 健康分析","§15 六亲分析","§16 全生命周期重点事件总表",
    "§17 大运精析","§18 三决断","§19 人生运程总评",
    "§20 五行补充建议","§21 人生建议"
]

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')
client = instructor.from_openai(OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL))

class Report21(BaseModel):
    raw_markdown: str = Field(min_length=500)

def count_sections(text: str) -> tuple:
    """检查21§覆盖情况"""
    found = []
    for s in STD_21:
        if re.search(re.escape(s[:6]), text):
            found.append(s)
    missing = [s for s in STD_21 if s not in found]
    return found, missing

def run(user_query: str, task_type: str = '通用',
        birth_year=1980, birth_month=8, birth_day=6,
        birth_hour=6, gender='男') -> dict:
    """完整流水线：引擎→检索→LLM生成21§→校验→输出"""
    
    # Step 1: 引擎计算
    print(f'[引擎] 排盘+身强弱+格局...', end=' ')
    try:
        p = get_full_paipan(birth_year, birth_month, birth_day, birth_hour, gender, '未知')
        bazi = BaZi(
            Pillar(gan=p['year_pillar']['gan'], zhi=p['year_pillar']['zhi']),
            Pillar(gan=p['month_pillar']['gan'], zhi=p['month_pillar']['zhi']),
            Pillar(gan=p['day_pillar']['gan'], zhi=p['day_pillar']['zhi']),
            Pillar(gan=p['hour_pillar']['gan'], zhi=p['hour_pillar']['zhi']),
            gender
        )
        score, label, _ = compute_shen_qiang_ruo(bazi)
        gm, gd = determine_ge_ju(bazi)
        xt = determine_xi_yong_shen(bazi)
        xys = f"喜:{','.join(xt[0])} 忌:{','.join(xt[1])}" if isinstance(xt, tuple) else str(xt)
        bazi_str = p['bazi']
        print(f'{bazi_str} | {label}({score}分) | {gm}')
    except Exception as e:
        return {'status': 'error', 'message': f'引擎失败: {str(e)[:100]}'}
    
    # Step 2: 前置检索
    print(f'[检索] Chroma知识库...', end=' ')
    hook = PreRetrievalHook()
    kb, refs = hook.retrieve(user_query, task_type)
    print(f'{len(refs)}个引用')
    
    # Step 3: LLM生成21§（最多3次重试）
    sections_list = "\n".join([f"  {i+1}. {sec}" for i, sec in enumerate(STD_21)])
    
    attempts = 0
    last_raw = ''
    while attempts <= 3:
        attempts += 1
        print(f'[LLM] 生成21§报告 (尝试{attempts})...', end=' ')
        
        feedback = ""
        if attempts > 1 and last_raw:
            found, missing = count_sections(last_raw)
            feedback = f"前次仅覆盖{len(found)}/21§，缺失: {', '.join(missing[:5])}。请确保全部21§都有内容。"
        
        prompt = f"""八字: {bazi_str} | {label}({score}分) | {gm}
喜用: {xys}

【强制知识】
{kb[:800]}

{feedback}

{user_query}

输出21§标准八字分析报告。要求：
1. 必须包含全部21个§，一个不能少
2. 每§写2-3句话，简洁精炼
3. §之间用---分隔
4. §8财富分析的破财风险根据八字实际喜忌动态判定
5. 在§1一页总览表中，必须单独列出以下三项：

   【关键调和与关键做工路径】
   (用3句话描述此八字的能量运作逻辑：用神如何发挥作用、五行如何流通做功)
   
   【强项与弱项】
   (列出此八字最强的2-3个方面，和最弱的2-3个风险点)
   
   【关键链路不能断】
   (指出此八字最关键的能量链条，一旦断裂会引发什么问题)

6. §21人生建议中必须呼应以上三项
7. §17大运总表必须用Markdown表格格式，列字段：大运 | 起止年龄 | 起止年份 | 干支五行 | 对格局影响 | 定性描述，覆盖至80岁
8. §16流年重点事件表必须用表格格式，按流年分列，字段：流年干支 | 事件类型 | 事件描述 | 吉凶，覆盖近10-15年已发生+未来5-10年
   - 事件类型包括：升官发财(💰)、灾祸(⚠️)、结婚添丁(💍)、资产置业(🏠)
   - 事件必须具体（如"2023癸卯年升任总监"），不可笼统

完整§列表：
{sections_list}"""

        try:
            result = client.chat.completions.create(
                model=LLM_MODEL,
                response_model=Report21,
                messages=[
                    {"role": "system", "content": "输出21§八字分析报告。每§2-3句。必须包含全部21个§。用---分隔§。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=6000
            )
            last_raw = result.raw_markdown
            found, missing = count_sections(last_raw)
            print(f'{len(found)}/{len(STD_21)}§')
            
            if len(missing) == 0:
                print(f'[校验] ✅ 全部21§齐全')
                break
            else:
                print(f'[校验] ⚠️ 缺失{len(missing)}个: {missing[:3]}')
                if attempts > 3:
                    print(f'[校验] 已达最大重试次数')
        except Exception as e:
            print(f'❌ LLM失败: {str(e)[:80]}')
            if attempts > 3:
                return {'status': 'error', 'message': f'LLM失败: {str(e)[:100]}'}
    
    # Step 4: 输出
    if last_raw:
        return {
            'status': 'success',
            'bazi_str': bazi_str,
            'shen_qiang': f'{label}({score}分)',
            'gegang': gm,
            'sections_found': len(found),
            'sections_missing': missing,
            'output': last_raw
        }
    return {'status': 'error', 'message': '无输出'}
