#!/usr/bin/env python3
"""workflow_v2.py — Harness Engine 工作流定义"""
import json, os, yaml

WORKFLOW = {
    "name": "九龙道长标准报告v2",
    "version": "2.0",
    "phases": [
        {
            "id": 0, "name": "系统预检查", "type": "computational",
            "steps": [
                {"name": "检查BAZI_DATASOURCE", "action": "check_env", "param": "BAZI_DATASOURCE", "fail": "BLOCK"},
                {"name": "检查数据源字段完整性", "action": "verify_ds_fields", "fail": "BLOCK"},
            ]
        },
        {
            "id": 4, "name": "模块生成", "type": "orchestrated",
            "sections": [
                {"id": "s1", "name": "一页总览", "rule": "rules/overview.yaml", "template": "templates/overview.md"},
                {"id": "s2", "name": "格局分析", "rule": "rules/geju.yaml", "template": "templates/geju.md"},
                {"id": "s3", "name": "身强弱", "rule": "rules/shen_qiang_ruo.yaml", "template": "templates/shen_qiang_ruo.md"},
                {"id": "s4", "name": "喜用神", "rule": "rules/xi_yong_shen.yaml", "template": "templates/xi_yong_shen.md"},
                {"id": "s5", "name": "灾祸疾病", "rule": "rules/zai_huo_ji_bing.yaml", "template": "templates/zai_huo_ji_bing.md"},
                {"id": "s6", "name": "性格", "rule": "rules/xing_ge.yaml", "template": "templates/xing_ge.md"},
                {"id": "s7", "name": "身材外貌", "rule": "rules/wai_mao.yaml", "template": "templates/wai_mao.md"},
                {"id": "s8", "name": "财富分析", "rule": "rules/cai_fu.yaml", "template": "templates/cai_fu.md"},
                {"id": "s9", "name": "置业", "rule": "rules/zhi_ye.yaml", "template": "templates/zhi_ye.md"},
                {"id": "s10", "name": "事业分析", "rule": "rules/shi_ye.yaml", "template": "templates/shi_ye.md"},
                {"id": "s11", "name": "学业", "rule": "rules/xue_ye.yaml", "template": "templates/xue_ye.md"},
                {"id": "s12", "name": "婚姻", "rule": "rules/hun_yin.yaml", "template": "templates/hun_yin.md"},
                {"id": "s13", "name": "子女", "rule": "rules/zi_nv.yaml", "template": "templates/zi_nv.md"},
                {"id": "s14", "name": "健康", "rule": "rules/jian_kang.yaml", "template": "templates/jian_kang.md"},
                {"id": "s15", "name": "六亲", "rule": "rules/liu_qin.yaml", "template": "templates/liu_qin.md"},
                {"id": "s16", "name": "事件总表", "rule": "rules/shi_jian.yaml", "template": "templates/shi_jian.md"},
                {"id": "s17", "name": "大运精析", "rule": "rules/da_yun.yaml", "template": "templates/da_yun.md"},
                {"id": "s18", "name": "三决断", "rule": "rules/san_jue_duan.yaml", "template": "templates/san_jue_duan.md"},
                {"id": "s19", "name": "运程总评", "rule": "rules/yun_cheng.yaml", "template": "templates/yun_cheng.md"},
                {"id": "s20", "name": "五行补充", "rule": "rules/wu_xing_bu_chong.yaml", "template": "templates/wu_xing_bu_chong.md"},
                {"id": "s21", "name": "人生建议", "rule": "rules/ren_sheng_jian_yi.yaml", "template": "templates/ren_sheng_jian_yi.md"},
                {"id": "s22", "name": "补文昌", "rule": "rules/bu_wen_chang.yaml", "template": "templates/bu_wen_chang.md"},
                {"id": "s23", "name": "开财库", "rule": "rules/kai_cai_ku.yaml", "template": "templates/kai_cai_ku.md"},
                {"id": "s24", "name": "一生定性", "rule": "rules/yi_sheng_ding_xing.yaml", "template": "templates/yi_sheng_ding_xing.md"},
            ]
        },
        {
            "id": 5, "name": "发布前校验", "type": "computational",
            "steps": [
                {"name": "数据源对齐", "action": "check_ds_alignment", "fail": "BLOCK"},
                {"name": "数字算术自检", "action": "check_arithmetic", "fail": "BLOCK"},
            ]
        },
    ]
}


def load_rule(path):
    with open(path) as f:
        return yaml.safe_load(f)
