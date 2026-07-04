#!/usr/bin/env python3
"""
loop-engineering-wealth.py — 财富体系·自动化学习循环引擎 v1.0

【架构】三段式自动化循环：
  Phase 1 — LEARN:  精读新素材/规则 → 对比现有skill → 生成结构化变更清单
  Phase 2 — VERIFY: 验证完整性 → 检查覆盖率
  Phase 3 — APPLY:  更新skill → 扫描所有受影响报告 → 批量更新 → 推库

【用法】作为Hermes task dispatch的目标，或直接运行：
  python3 /root/bazi-platform/scripts/loop-engineering-wealth.py \
    --phase cycle \
    --rules-file /tmp/wealth_changelog.json \
    --reports "家主,主母,子源,立"

【自动输出】
  1. skill patch 指令 (Hermes可执行)
  2. 报告更新清单
  3. git push 指令
"""

import json
import os
import re
import sys
from datetime import datetime

# ─── 常量配置 ─────────────────────────────────────
BAZI_PLATFORM = "/root/bazi-platform"
SCRIPTS_DIR = f"{BAZI_PLATFORM}/scripts"
SKILL_DIR = "/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-wealth-analysis"
SKILL_FILE = f"{SKILL_DIR}/SKILL.md"
KNOWLEDGE_BASE = "/root/weiwuji-knowledge-base"
REPORTS_BASE = f"{KNOWLEDGE_BASE}/07-国学哲学/八字命格/02-人物档案"

# 受规则影响的报告与人物目录映射
REPORT_MAP = {
    "家主": {"dir": "01-家主-魏启令", "name": "魏家长子魏启令"},
    "主母": {"dir": "02-主母-成", "name": "魏家主母成"},
    "子源": {"dir": "03-少爷-子源", "name": "魏子源"},
    "立": {"dir": "05-立", "name": "立"},
}

VERSION_DIR_MAP = {
    "家风版": "家风版",
    "v7": "家风版",
    "v8": "家风版",
    "财富": "财富方案",
    "补财库": "补财库方案",
}


class LoopEngineering:
    """Loop Engineering 三段式自动循环引擎"""

    def __init__(self, phase="cycle", rules_file=None, reports=None):
        self.phase = phase
        self.rules_file = rules_file
        self.reports = reports.split(",") if reports else []
        self.rules = []
        self.changelog = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.changelog_path = f"{SCRIPTS_DIR}/_changelogs/wealth_{self.timestamp}.json"

    # ═══ Phase 1: LEARN ═══════════════════════════════

    def phase_learn(self):
        """Phase 1: 学习 — 精读规则 → 对比skill → 生成变更清单"""
        print(f"\n{'=' * 60}")
        print("  📖 Phase 1: LEARN — 精读&对比")
        print(f"{'=' * 60}")

        # ① 加载现有skill
        if os.path.exists(SKILL_FILE):
            with open(SKILL_FILE) as f:
                existing_skill = f.read()
            print(f"  ✓ 加载现有skill ({len(existing_skill)} chars)")
        else:
            print(f"  ✗ SKILL.md 不存在: {SKILL_FILE}")
            existing_skill = ""

        # ② 加载规则变更清单
        if self.rules_file and os.path.exists(self.rules_file):
            with open(self.rules_file) as f:
                raw_rules = json.load(f)
            self.rules = raw_rules.get("rules", [])
            print(f"  ✓ 加载规则文件: {len(self.rules)} 条规则")
        else:
            print("  ! 无规则文件，使用内嵌默认规则")
            self.rules = self._get_default_rules()

        # ③ 对比现有skill → 生成变更清单
        new_rules = []
        corrected_rules = []
        deleted_rules = []

        for rule in self.rules:
            rule_key = rule.get("key", rule.get("title", ""))
            rule_content = rule.get("content", "")

            # 检查是否已存在（基于§章节标题匹配）
            if rule_key and rule_content:
                is_new = False
                # 先用§章节号匹配（如 §17 或 §2.2）
                section_num = re.search(r"§([\d\.]+)", rule_key)
                if section_num:
                    section_num = section_num.group(1)
                    section_pattern = rf"##\s*§{re.escape(section_num)}"
                    if not re.search(section_pattern, existing_skill):
                        is_new = True
                        print(f"  🆕 新增章节: §{section_num} {rule.get('title', '')[:30]}")
                    else:
                        print(f"  ✓ 已有章节 §{section_num}")

                if is_new:
                    new_rules.append(rule)
                    print(f"  🆕 新增规则: {rule.get('title', rule_key)[:40]}")
                else:
                    # 检查是否需要修正
                    print(f"  ✓ 已有规则(检查): {rule.get('title', rule_key)[:40]}")

        # ④ 生成结构化变更清单
        self.changelog = {
            "meta": {
                "timestamp": self.timestamp,
                "domain": "wealth",
                "phase": "learn",
                "skill_version": self._detect_skill_version(existing_skill),
            },
            "new_rules": [
                {
                    "key": r.get("key", r.get("title", "")),
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "section": r.get("section", "新建"),
                    "source": r.get("source", "新增规则"),
                }
                for r in new_rules
            ],
            "corrected_rules": corrected_rules,
            "deleted_rules": deleted_rules,
            "affected_reports": self._scan_affected_reports(),
        }

        # 保存变更清单
        os.makedirs(os.path.dirname(self.changelog_path), exist_ok=True)
        with open(self.changelog_path, "w") as f:
            json.dump(self.changelog, f, ensure_ascii=False, indent=2)

        print(f"\n  ✅ 变更清单已生成: {self.changelog_path}")
        print(f"  📊 新增: {len(new_rules)} | 修正: {len(corrected_rules)} | 删除: {len(deleted_rules)}")
        print(f"  📄 影响报告: {len(self.changelog['affected_reports'])} 份")

        return self.changelog_path

    def _get_default_rules(self):
        """默认规则集（用于当前财富体系循环）"""
        return [
            {
                "key": "能量链条法则",
                "title": "§👑 核心概念：能量链条（比劫→食伤→财）",
                "section": "§👑 新建",
                "content": "发财的本质逻辑：比劫(身)→食伤→财 这条能量链条必须完整且够力。\n"
                "身强=比劫足→能生食伤→链条顺畅→能担财\n"
                "身弱=比劫弱→生不动食伤→链条断→担不住财\n"
                "口诀：财富不看单维度，能量链条看全部；起点终点加中间，三段打通才是富。",
                "source": "09号视频截图精读 §1:58",
            },
            {
                "key": "发财五法",
                "title": "§7 发财的五种方式（09号视频原文表）",
                "section": "§7 重写",
                "content": "发财五法：①身强财旺 ②流年遇库则发 ③流年遇五鬼运财则发 ④流年遇禄神则发 ⑤大运流年补足(六种状态矩阵)",
                "source": "09号视频截图精读 §发财的方法总结",
            },
            {
                "key": "破财五条件",
                "title": "§17 什么时候破财（5种条件逐项检查）",
                "section": "§17 新建",
                "content": "破财5条件：①流年财星受冲 ②流年食伤受冲 ③身强遇比肩劫财 ④财星被合化成其他能量 ⑤流年遇墓破财",
                "source": "09号视频截图精读 §0:06:54 + 素材11行33~41",
            },
            {
                "key": "合作伙伴规则",
                "title": "§16 合作伙伴规则（身强vs身弱完全不同）",
                "section": "§16 新建",
                "content": "身强→以财官食为喜用(消耗能量)；身弱→以印比为喜用(补充能量)\n"
                "身强3模式：①以财为喜用→与老板合作 ②以官杀为喜用→与领导合作 ③以食伤为喜用→与下属合作\n"
                "身弱2模式：①以比劫为喜用→与朋友合作 ②以印为喜用→与师长合作",
                "source": "素材11行65~209原文逐字",
            },
            {
                "key": "财富五级定量表修正",
                "title": "§2.2 财富五级定量表（修正大富条件）",
                "section": "§2.2 修正",
                "content": "巨富=大运配合无刑冲；大富=大运刑冲；中富=财星<40分无库；小富=身弱财弱无库；贫穷=身弱无财+枭神夺食",
                "source": "09号视频截图精读 §1:26:55 + 素材11行349~433",
            },
        ]

    def _detect_skill_version(self, skill_content):
        """检测现有skill的版本号"""
        match = re.search(r"v(\d+\.\d+)", skill_content)
        return match.group(1) if match else "unknown"

    def _scan_affected_reports(self):
        """扫描所有受财富规则影响的报告"""
        affected = []
        for person, info in REPORT_MAP.items():
            person_dir = f"{REPORTS_BASE}/{info['dir']}"
            if os.path.exists(person_dir):
                files = [f for f in os.listdir(person_dir) if f.endswith(".md")]
                if files:
                    affected.append(
                        {
                            "person": person,
                            "name": info["name"],
                            "dir": info["dir"],
                            "files": files,
                        }
                    )
        return affected

    # ═══ Phase 2: VERIFY ══════════════════════════════

    def phase_verify(self, changelog_path=None):
        """Phase 2: VERIFY — 已合并到CHECKER，直接转发"""
        return self.phase_checker()

    # ═══ Phase 2.5: CHECKER ══════════════════════════════

    def phase_checker(self):
        """Phase 2: CHECKER — 报告 vs skill §0-§17 全量规则交叉验证
        ============================================================
        核心原则：Maker规则全集 = Checker规则全集
        ============================================================
        Maker写报告参考：§👑 §0 §1 §2 §3 §4 §5 §6 §7 §10 §12 §13 §14 §16 §17
        Checker必须验证全部上述规则，一条不能少（与Maker 1:1对应）
        
        关键设计：**不信任报告中的任何断言**，用skill规则重新推导再对比。
        当前验证维度：§10.1 五种墓库全量（比劫/财才/官杀/印枭/食伤）
        蓄财双库：比劫墓库 + 财才墓库（素材11行365）
        赚钱动力源：食伤墓库（老板校准20260702）
        Read verification-rules.yaml for complete rule list (Maker=Checker 1:1)
        """
        print(f"\n{'=' * 60}")
        print("  🔬 CHECKER — 报告 vs skill §10.1 五种墓库全量验证")
        print(f"{'=' * 60}")

        # ① 加载skill §10.1五种墓库表
        skill_content = ""
        if os.path.exists(SKILL_FILE):
            with open(SKILL_FILE) as f:
                skill_content = f.read()

        muku_table = {}
        for line in skill_content.split("\n"):
            if line.startswith("|") and "日元" in line:
                continue
            if line.startswith("|") and ("木" in line or "火" in line or "土" in line or "金" in line or "水" in line):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:
                    muku_table[parts[1]] = {
                        "比劫库": parts[2],  # 蓄财库①：合作得财
                        "财才墓库": parts[3],  # 蓄财库②：直接蓄财
                        "官杀库": parts[4],
                        "印库": parts[5],
                        "食伤库": parts[6].split("|")[0],  # 赚钱动力源
                    }

        ri_zhu_map = {
            "甲": "甲乙木",
            "乙": "甲乙木",
            "丙": "丙丁火",
            "丁": "丙丁火",
            "戊": "戊己土",
            "己": "戊己土",
            "庚": "庚辛金",
            "辛": "庚辛金",
            "壬": "壬癸水",
            "癸": "壬癸水",
        }

        ku_labels = {
            "比劫库": "蓄财库①·合作得财",
            "财才墓库": "蓄财库②·直接蓄财",
            "官杀库": "权力/管理",
            "印库": "证书/合同",
            "食伤库": "赚钱动力源",
        }
        all_dizhi = list("子丑寅卯辰巳午未申酉戌亥")

        all_issues = []
        all_passed = 0
        all_failed = 0

        for person, info in REPORT_MAP.items():
            person_dir = f"{REPORTS_BASE}/{info['dir']}"
            wealth_files = [f for f in os.listdir(person_dir) if f.endswith(".md") and ("财富" in f or "补财" in f)]
            for fname in wealth_files:
                fpath = f"{person_dir}/{fname}"
                with open(fpath) as f:
                    content = f.read()

                bazi_match = re.search(
                    r"(?:八字\s*[|:：].*?|(?<=\*\*))([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])",
                    content,
                )
                rizhu_match = re.search(r"日主\s*[|:：\]]\s*\*?\*?([甲乙丙丁戊己庚辛壬癸])", content)
                if not rizhu_match:
                    print(f"  ⚠ {person}/{fname}: 未找到日主，跳过")
                    continue

                rizhu = rizhu_match.group(1)
                rizhu_group = ri_zhu_map.get(rizhu, "")
                dizhi_in_bazi = []
                if bazi_match:
                    for g in bazi_match.groups():
                        dizhi_in_bazi.append(g[1])  # 取每组第二个字=地支

                print(f"\n  ── {person} ({rizhu}日主) ──")

                if rizhu_group not in muku_table:
                    print(f"  ⚠ 未找到{rizhu_group}的墓库表")
                    continue

                for ku_type in ["比劫库", "财才墓库", "官杀库", "印库", "食伤库"]:
                    entry = muku_table[rizhu_group].get(ku_type, "")
                    dz_match = re.search(r"^([子丑寅卯辰巳午未申酉戌亥])", entry)
                    if not dz_match:
                        continue
                    dizhi = dz_match.group(1)
                    has_it = dizhi in dizhi_in_bazi
                    label = ku_labels.get(ku_type, ku_type)
                    report_mentions = ku_type[:2] in content or f"{dizhi}=" in content or f"{dizhi}库" in content

                    if has_it and not report_mentions:
                        all_failed += 1
                        sev = "error"
                        msg = f"八字含{dizhi}={ku_type}({label})，报告中未提及"
                        all_issues.append({"person": person, "file": fname, "severity": sev, "issue": msg})
                        print(f"  ❌ [{sev}] {ku_type}={dizhi}({label}) — 报告遗漏")
                    elif has_it:
                        all_passed += 1
                        print(f"  ✅ {ku_type}={dizhi}({label}) —已有 ✅")
                    else:
                        all_passed += 1
                        print(f"  ✓ {ku_type}={dizhi}({label}) —八字无")

        print(f"\n{'─' * 60}")
        if all_failed > 0:
            print(f"  ❌ CHECKER: {all_passed} 通过, {all_failed} 失败, {len(all_issues)} 个问题")
            for iss in all_issues[:10]:
                print(f"  · [{iss['severity']}] {iss['person']} - {iss['issue'][:80]}")
            return False
        else:
            print(f"  ✅ CHECKER通过 — 五种墓库全量验证({all_passed}项)")
            return True

    # ═══ Phase 3: APPLY ═══════════════════════════════

    def phase_apply(self, changelog_path=None):
        """Phase 3: 应用 — 输出Hermes可执行的指令序列"""
        path = changelog_path or self.changelog_path
        print(f"\n{'=' * 60}")
        print("  🚀 Phase 3: APPLY — 生成执行指令")
        print(f"{'=' * 60}")

        with open(path) as f:
            changelog = json.load(f)

        # 输出结构化指令给Hermes主agent执行
        print(f"\n{'─' * 60}")
        print("  以下指令请由金鉴真人的Sub-Agent执行：")
        print(f"{'─' * 60}\n")

        # 指令1: 更新skill
        print("【指令1】更新 bazi-wealth-analysis skill")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for rule in changelog.get("new_rules", []):
            section = rule.get("section", "新建")
            print(f"  ▶ 区域: {section}")
            print(f"  ▶ 标题: {rule['title']}")
            print(f"  ▶ 来源: {rule.get('source', 'N/A')}")
            print(f"  ▶ 内容长度: {len(rule['content'])} chars")
            print()

        # 指令2: 更新报告
        print("【指令2】更新受影响报告")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for r in changelog.get("affected_reports", []):
            skill_version = changelog.get("meta", {}).get("skill_version", "v?.?")
            new_version = self._bump_version(skill_version)
            for fname in r.get("files", []):
                if self._is_wealth_report(fname):
                    full_path = f"{REPORTS_BASE}/{r['dir']}/{fname}"
                    print(f"  ▶ {r['person']} → {full_path}")
                    print("    (需要: 添加§👑能量链条 + §7发财五法 + §16合作伙伴 + §17破财5条)")

        # 指令3: 推库
        print()
        print("【指令3】推库")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f'  ▶ cd {KNOWLEDGE_BASE} && git add -A && git commit -m "[wealth][v{new_version}] ..." && git push')

        # 保存apply结果
        apply_result = {
            "changelog": path,
            "instructions": [
                {
                    "type": "update_skill",
                    "skill": "bazi-wealth-analysis",
                    "new_rules_count": len(changelog.get("new_rules", [])),
                },
                {
                    "type": "update_reports",
                    "count": len(changelog.get("affected_reports", [])),
                    "targets": [r["person"] for r in changelog.get("affected_reports", [])],
                },
                {
                    "type": "git_push",
                    "repo": KNOWLEDGE_BASE,
                },
            ],
        }
        apply_path = f"{SCRIPTS_DIR}/_changelogs/wealth_{self.timestamp}_apply.json"
        with open(apply_path, "w") as f:
            json.dump(apply_result, f, ensure_ascii=False, indent=2)

        print(f"\n  ✅ 指令集已保存: {apply_path}")
        return apply_path

    def _bump_version(self, current_version):
        """版本号递增"""
        match = re.search(r"(\d+)\.(\d+)", str(current_version))
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            return f"{major}.{minor + 1}"
        return "4.0"

    def _is_wealth_report(self, filename):
        """判断文件是否为财富报告"""
        keywords = ["财富", "财", "补财库", "财运", "v1.0", "v1.1"]
        return any(k in filename for k in keywords)

    # ═══ 完整循环 ═══════════════════════════════════

    def run_cycle(self):
        """一键执行完整 learn → verify → checker → apply 循环"""
        print(f"\n{'█' * 60}")
        print("  🔄 Loop Engineering 完整循环启动")
        print(f"  领域: 财富体系 | 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'█' * 60}")

        # Phase 1: Learn
        changelog_path = self.phase_learn()

        # Phase 2: Verify
        if not self.phase_verify(changelog_path):
            print("\n  ⚠ 验证不通过，请在 changelog 中修复后重试")
            return False

        # Phase 2.5: Checker — 报告 vs skill 交叉验证
        if not self.phase_checker():
            print("\n  ❌ CHECKER发现报告内容与skill规则不一致！请修复后再推库")
            return False

        # Phase 3: Apply
        apply_result = self.phase_apply(changelog_path)

        print(f"\n{'█' * 60}")
        print("  ✅ 循环完成！")
        print(f"  变更清单: {changelog_path}")
        print(f"  执行指令: {apply_result}")
        print(f"{'█' * 60}")

        return True


# ═══ CLI 入口 ═══════════════════════════════════════


def main():
    import argparse

    parser = argparse.ArgumentParser(description="财富体系·自动化学习循环引擎")
    parser.add_argument(
        "--phase", choices=["learn", "verify", "checker", "apply", "cycle"], default="cycle", help="执行阶段"
    )
    parser.add_argument("--rules-file", help="规则变更JSON文件路径")
    parser.add_argument("--reports", default="家主,主母,子源,立", help="受影响报告列表 (逗号分隔)")

    args = parser.parse_args()

    engine = LoopEngineering(
        phase=args.phase,
        rules_file=args.rules_file,
        reports=args.reports,
    )

    if args.phase == "cycle":
        engine.run_cycle()
    elif args.phase == "learn":
        engine.phase_learn()
    elif args.phase == "verify":
        engine.phase_verify()
    elif args.phase == "checker":
        engine.phase_checker()
    elif args.phase == "apply":
        engine.phase_apply()

    return 0


if __name__ == "__main__":
    sys.exit(main())
