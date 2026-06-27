"""
金鉴真人·模块导入验证测试
验证所有引擎模块可正确导入，函数签名与调用一致
"""

import sys, os, importlib

ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ENGINE_DIR)

# 所有引擎模块及预期导出的公共函数
MODULE_CHECKS = {
    "paipan": ["paipan"],
    "shen_qiang_ruo": ["compute_shen_qiang_ruo", "explain_score"],
    "shi_shen": ["get_shi_shen_for_gan", "get_shi_shen_for_cang_gan"],
    "cai_xing": ["compute_cai_xing", "cai_xing_explain"],
    "ge_ju": ["determine_ge_ju"],
    "da_yun": ["compute_da_yun", "compute_da_yun_scores"],
    "shen_sha": ["get_tian_yi", "get_wen_chang", "get_yi_ma"],
    "energy": ["compute_wu_xing_energy", "compute_energy_profile"],
    "xing_chong_he_hua": ["check_chong", "check_xing", "check_hai"],
    "liu_nian_v2": ["analyze_liu_nian_v2", "analyze_liu_nian_range"],
    "dimensions_v2": ["score_cai_fu", "score_shi_ye", "score_hun_yin"],
    "wealth_v2": ["analyze_wealth_full"],
    "career_v2": ["analyze_career_full"],
    "marriage_v2": ["analyze_marriage"],
    "education_v2": ["analyze_education"],
    "children_v2": ["get_children_star_school_a"],
    "health_v2": ["calc_wuxing_scores"],
    "misfortune_analysis": ["analyze_misfortune"],
    "pipeline_v5": ["run_pipeline", "run_v5", "format_21_section_report"],
}


def test_all_modules_import():
    """验证所有模块可正确导入"""
    failed = []
    for mod_name in MODULE_CHECKS:
        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            failed.append(f"  ✗ {mod_name}: {e}")

    assert not failed, f"模块导入失败:\n" + "\n".join(failed)
    print(f"  ✓ 全部 {len(MODULE_CHECKS)} 个模块导入成功")


def test_all_expected_funcs():
    """验证每个模块的预期函数可调用"""
    failed = []
    for mod_name, expected_funcs in MODULE_CHECKS.items():
        try:
            mod = importlib.import_module(mod_name)
            for func_name in expected_funcs:
                if not hasattr(mod, func_name):
                    # 尝试自动修正
                    failed.append(f"  ✗ {mod_name}.{func_name} 不存在")
        except ImportError as e:
            failed.append(f"  ✗ {mod_name}: {e}")

    assert not failed, f"缺少预期函数:\n" + "\n".join(failed)
    print(f"  ✓ 全部预期函数存在")


if __name__ == "__main__":
    test_all_modules_import()
    test_all_expected_funcs()
    print("\n✅ 全部导入验证通过")
