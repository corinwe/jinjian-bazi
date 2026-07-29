"""结构化输出模型 — Instructor强制LLM输出固定JSON结构"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class LineJudgment(str, Enum):
    """分线断法——每条线明确吉凶"""
    吉 = "吉"
    凶 = "凶"
    平 = "平"

class KnowledgeRef(BaseModel):
    """知识引用——强制LLM标注来源"""
    section: str = Field(description="引用章节号，如§37.1")
    title: str = Field(description="引用章节标题")
    key_point: str = Field(description="引用的具体知识点")

class AnalysisSection(BaseModel):
    """分析章节——每个分析段落的结构"""
    section_name: str = Field(description="分析章节名")
    sop_step: str = Field(description="遵循的SOP步骤编号")
    knowledge_refs: List[KnowledgeRef] = Field(description="引用的知识来源，至少1个")
    analysis_text: str = Field(description="分析内容")
    
class LineAnalysis(BaseModel):
    """分线断法——每条线的独立判断"""
    line_type: str = Field(description="线类型: 财线/官杀线/身线/夫妻线/比劫线")
    judgment: LineJudgment = Field(description="明确吉凶")
    reason: str = Field(description="判断依据，必须引用知识")

class GegangAnalysis(BaseModel):
    """格局分析输出"""
    gegang_type: str = Field(description="格局类型")
    success: bool = Field(description="格成/格败")
    condition: str = Field(description="成/败的条件")
    qingzhuo: str = Field(description="清浊评定")

class SanJueDuan(BaseModel):
    """三决断"""
    item_1: str = Field(description="第一条决断")
    item_2: str = Field(description="第二条决断")
    item_3: str = Field(description="第三条决断")

class FullAnalysisOutput(BaseModel):
    """完整八字分析输出"""
    gegang: GegangAnalysis = Field(description="格局分析")
    xiyong: str = Field(description="喜用忌判定")
    san_jueduan: SanJueDuan = Field(description="三决断")
    lines: List[LineAnalysis] = Field(description="分线断法，至少5条")
    knowledge_used: List[str] = Field(description="使用的知识来源列表")

class ValidationResult(BaseModel):
    """校验结果"""
    passed: bool
    errors: List[str] = []
    warnings: List[str] = []
