"""
数据模型定义

设计原则：
1. 清晰的接口结构，方便后续对接真实 API
2. 使用 Pydantic 进行数据验证
3. 支持扩展字段
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DegreeLevel(str, Enum):
    """学历等级"""
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士"
    COLLEGE = "大专"
    OTHER = "其他"


class SchoolTier(str, Enum):
    """学校层级"""
    TIER_985 = "985"
    TIER_211 = "211"
    OVERSEAS = "海外名校"
    NORMAL = "普通本科"
    OTHER = "其他"


class TechStack(str, Enum):
    """技术栈分类"""
    JAVA = "Java"
    CPP = "C++"
    PYTHON = "Python"
    FRONTEND = "前端"
    BACKEND = "后端"
    FULLSTACK = "全栈"
    ARCHITECTURE = "架构"
    ALGORITHM = "算法"
    DATA = "数据"
    DEVOPS = "运维"
    AI_ML = "AI/ML"
    OTHER = "其他"


class TaskType(str, Enum):
    """任务类型"""
    INTERVIEW = "面试辅导"
    RESUME = "简历优化"
    CAREER = "职业规划"
    SKILL = "技能培训"
    MOCK = "模拟面试"
    OTHER = "其他"


class Expert(BaseModel):
    """专家基础信息"""
    talent_id: str = Field(..., description="专家唯一标识")
    name: Optional[str] = Field(None, description="专家姓名（可选）")
    
    # 教育背景
    degree: DegreeLevel = Field(DegreeLevel.OTHER, description="最高学历")
    school_tier: SchoolTier = Field(SchoolTier.OTHER, description="学校层级")
    school_name: Optional[str] = Field(None, description="学校名称")
    
    # 技术能力
    tech_stacks: List[str] = Field(default_factory=list, description="技术栈列表")
    skills: List[str] = Field(default_factory=list, description="技能标签")
    years_of_experience: Optional[int] = Field(None, description="工作年限")
    
    # 任务相关
    task_count: int = Field(0, description="完成任务数")
    task_types: List[str] = Field(default_factory=list, description="任务类型分布")
    domains: List[str] = Field(default_factory=list, description="领域分布")
    
    # 多样性评分 (0-100)
    type_score: int = Field(0, ge=0, le=100, description="任务类型多样性得分")
    domain_score: int = Field(0, ge=0, le=100, description="领域覆盖多样性得分")
    structure_score: int = Field(0, ge=0, le=100, description="结构差异度得分")
    diversity_score: int = Field(0, ge=0, le=100, description="综合多样性得分")
    
    # 模板化风险指标
    template_ratio: float = Field(0, ge=0, le=1, description="模板化程度 (0-1)")
    unique_patterns: int = Field(0, description="独立结构模式数")
    template_risk_level: str = Field("low", description="模板风险等级: low/medium/high")
    template_risk_description: str = Field("", description="模板风险描述")
    
    # 质量标签
    quality_label: str = Field("normal", description="质量标签: high_quality/normal/risk")
    quality_label_reason: str = Field("", description="质量标签判定依据")
    
    # 大厂背景
    has_big_company_exp: bool = Field(False, description="是否有大厂经历")
    companies: List[str] = Field(default_factory=list, description="工作过的公司")


class TemplateRiskStats(BaseModel):
    """模板化风险统计"""
    high_risk_count: int = Field(0, description="高风险专家数")
    high_risk_pct: float = Field(0, description="高风险占比")
    medium_risk_count: int = Field(0, description="中风险专家数")
    medium_risk_pct: float = Field(0, description="中风险占比")
    low_risk_count: int = Field(0, description="低风险专家数")
    low_risk_pct: float = Field(0, description="低风险占比")
    avg_template_ratio: float = Field(0, description="平均模板化程度")
    avg_unique_patterns: float = Field(0, description="平均独立模式数")


class QualityLabelStats(BaseModel):
    """质量标签统计"""
    high_quality_count: int = Field(0, description="高质量专家数")
    high_quality_pct: float = Field(0, description="高质量占比")
    normal_count: int = Field(0, description="正常专家数")
    normal_pct: float = Field(0, description="正常占比")
    risk_count: int = Field(0, description="风险专家数")
    risk_pct: float = Field(0, description="风险占比")


class DashboardStats(BaseModel):
    """Dashboard 统计数据"""
    
    # 概览
    total_experts: int = Field(..., description="专家总数")
    
    # 学历分布
    degree_distribution: Dict[str, int] = Field(..., description="学历分布")
    
    # 学校层级分布
    school_tier_distribution: Dict[str, int] = Field(..., description="学校层级分布")
    
    # 技术栈分布
    tech_stack_distribution: Dict[str, int] = Field(..., description="技术栈分布")
    
    # 任务统计
    task_stats: Dict[str, float] = Field(..., description="任务统计数据")
    
    # 任务类型分布
    task_type_distribution: Dict[str, int] = Field(..., description="任务类型分布")
    
    # KPI 指标
    kpi: Dict[str, float] = Field(..., description="关键指标")
    
    # 模板化风险统计
    template_risk_stats: Optional[TemplateRiskStats] = Field(None, description="模板化风险统计")
    
    # 质量标签统计
    quality_label_stats: Optional[QualityLabelStats] = Field(None, description="质量标签统计")
    
    # 多样性评分分布
    diversity_score_distribution: Optional[Dict[str, int]] = Field(None, description="多样性评分分布")
    
    # 平均分数
    avg_scores: Optional[Dict[str, float]] = Field(None, description="平均分数")


class UploadResponse(BaseModel):
    """上传响应"""
    success: bool
    message: str
    talent_count: int = 0
    session_id: Optional[str] = None


class DashboardResponse(BaseModel):
    """Dashboard 响应"""
    success: bool
    message: str
    stats: Optional[DashboardStats] = None
    experts: Optional[List[Expert]] = None
