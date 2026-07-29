"""校验门禁 — Agent输出后全量硬性校验"""
import json
import re
from typing import Optional
from structured_output import FullAnalysisOutput, ValidationResult

class GatekeeperValidator:
    """每步LLM输出后的硬性校验"""
    
    REQUIRED_SECTIONS = ['gegang', 'xiyong', 'san_jueduan', 'lines', 'knowledge_used']
    REQUIRED_LINE_TYPES = ['财线', '官杀线', '身线', '夫妻线', '比劫线']
    MAX_RETRIES = 3
    
    def validate_full_analysis(self, output: FullAnalysisOutput) -> ValidationResult:
        """验证完整分析输出"""
        errors = []
        warnings = []
        
        # 1. 检查是否包含所有必需字段
        for field in self.REQUIRED_SECTIONS:
            if not getattr(output, field, None):
                errors.append(f"缺少必需字段: {field}")
        
        # 2. 检查分线断法是否完整
        present_lines = [l.line_type for l in output.lines]
        for required in self.REQUIRED_LINE_TYPES:
            if required not in present_lines:
                errors.append(f"缺少分线: {required}")
        
        for line in output.lines:
            if line.judgment not in ['吉', '凶', '平']:
                errors.append(f"{line.line_type}的吉凶判断不明确")
        
        # 3. 检查知识引用
        if output.knowledge_used:
            refs = ' '.join(output.knowledge_used)
            if not re.search(r'§\d+', refs):
                warnings.append("知识引用未包含章节号")
        else:
            warnings.append("未提供知识引用")
        
        # 4. 检查三决断是否具体
        for i, item in enumerate([output.san_jueduan.item_1, 
                                   output.san_jueduan.item_2, 
                                   output.san_jueduan.item_3], 1):
            if not item or len(item) < 5:
                errors.append(f"三决断第{i}条过于简略")
        
        # 5. 检查格局条件是否明确
        if not output.gegang.condition:
            warnings.append("格局条件不明确")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_json(self, raw_json: str) -> tuple[Optional[FullAnalysisOutput], ValidationResult]:
        """解析JSON并校验"""
        try:
            data = json.loads(raw_json)
            parsed = FullAnalysisOutput(**data)
            result = self.validate_full_analysis(parsed)
            return parsed, result
        except json.JSONDecodeError as e:
            return None, ValidationResult(
                passed=False,
                errors=[f"JSON解析失败: {str(e)}"]
            )
        except Exception as e:
            return None, ValidationResult(
                passed=False,
                errors=[f"数据校验失败: {str(e)}"]
            )
