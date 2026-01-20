"""
Mock 数据生成器

用于第一阶段开发测试，模拟真实专家数据。
后续可替换为真实 API 调用。
"""

import random
import hashlib
from typing import List, Dict
from collections import Counter
from app.models.schemas import Expert, DegreeLevel, SchoolTier


# 模拟数据池
MOCK_NAMES = [
    "张伟", "王芳", "李明", "刘洋", "陈静", "杨帆", "赵强", "黄磊",
    "周杰", "吴敏", "郑华", "孙燕", "马超", "朱峰", "胡鹏", "林涛",
    "何雨", "罗军", "梁静", "宋健", "唐文", "韩雪", "曹亮", "许晨"
]

MOCK_SCHOOLS = {
    SchoolTier.TIER_985: [
        "清华大学", "北京大学", "复旦大学", "上海交通大学", "浙江大学",
        "南京大学", "中国科学技术大学", "哈尔滨工业大学", "西安交通大学", "武汉大学"
    ],
    SchoolTier.TIER_211: [
        "北京邮电大学", "华东理工大学", "南京航空航天大学", "西安电子科技大学",
        "武汉理工大学", "中南财经政法大学", "苏州大学", "上海大学"
    ],
    SchoolTier.OVERSEAS: [
        "MIT", "Stanford University", "Carnegie Mellon", "UC Berkeley",
        "Cambridge University", "Oxford University", "ETH Zurich"
    ],
    SchoolTier.NORMAL: [
        "北京工商大学", "上海应用技术大学", "杭州电子科技大学", "成都理工大学",
        "广东工业大学", "武汉科技大学", "长沙理工大学"
    ],
    SchoolTier.OTHER: ["其他院校"]
}

TECH_STACKS = ["Java", "C++", "Python", "前端", "后端", "全栈", "架构", "算法", "数据", "运维", "AI/ML"]

SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++",
    "React", "Vue", "Node.js", "Spring Boot", "Django", "FastAPI",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "Docker", "Kubernetes", "AWS", "阿里云", "微服务", "分布式系统",
    "机器学习", "深度学习", "NLP", "计算机视觉", "推荐系统",
    "系统设计", "高并发", "性能优化", "安全", "测试"
]

TASK_TYPES = ["面试辅导", "简历优化", "职业规划", "技能培训", "模拟面试", "其他"]

# 任务类型关键词（用于模拟 prompt 分析）
TASK_TYPE_KEYWORDS = {
    "改写": ["改写", "重写", "润色"],
    "评测": ["评测", "评估", "评分", "打分"],
    "生成": ["生成", "创作", "撰写", "写一"],
    "推理": ["推理", "分析", "计算", "解题"],
    "翻译": ["翻译", "英译中", "中译英"],
    "问答": ["回答", "解答", "问答"],
    "代码": ["代码", "编程", "程序"],
    "总结": ["总结", "概括", "摘要"],
}

# 领域标签
DOMAIN_LABELS = [
    "K12教育", "高等教育/科研", "临床医学", "投资/证券", "财务/会计",
    "软件开发", "产品/运营", "市场/营销", "法律/合规", "设计/创意",
    "项目/管理", "人力/行政", "咨询/分析", "文化/传媒", "通用/日常"
]

BIG_COMPANIES = [
    "腾讯", "阿里巴巴", "字节跳动", "华为", "美团", "京东", "百度",
    "快手", "小米", "网易", "滴滴", "拼多多", "微软", "Google", "Amazon"
]

NORMAL_COMPANIES = [
    "某科技公司", "某互联网公司", "某创业公司", "某金融科技公司",
    "某软件公司", "某游戏公司", "某电商公司"
]

# Prompt 模板样本（用于模拟不同结构的任务）
PROMPT_TEMPLATES = [
    "请帮我{action}一下{object}",
    "我需要{action}{object}，要求{requirement}",
    "1. {step1}\n2. {step2}\n3. {step3}",
    "{object}是什么？请详细解释",
    "帮我分析一下{object}的{aspect}",
    "请根据以下要求{action}：{requirement}",
]


def generate_task_queries(rng: random.Random, count: int, template_bias: float = 0.3) -> List[Dict]:
    """
    生成模拟的任务 Query 列表
    
    Args:
        rng: 随机数生成器
        count: 任务数量
        template_bias: 模板化程度偏向（0-1），越高越倾向于使用相同模板
        
    Returns:
        任务列表，包含 query, task_type, domain
    """
    tasks = []
    
    # 根据 template_bias 决定使用多少种模板
    if template_bias > 0.6:
        # 高模板化：主要使用 1-2 种模板
        template_pool = rng.sample(PROMPT_TEMPLATES, k=min(2, len(PROMPT_TEMPLATES)))
    elif template_bias > 0.3:
        # 中等：使用 3-4 种模板
        template_pool = rng.sample(PROMPT_TEMPLATES, k=min(4, len(PROMPT_TEMPLATES)))
    else:
        # 低模板化：使用全部模板
        template_pool = PROMPT_TEMPLATES.copy()
    
    # 领域分布：根据 template_bias 决定领域集中度
    if template_bias > 0.5:
        # 集中于 1-2 个领域
        domain_pool = rng.sample(DOMAIN_LABELS, k=min(2, len(DOMAIN_LABELS)))
    else:
        # 分布于多个领域
        domain_pool = rng.sample(DOMAIN_LABELS, k=min(6, len(DOMAIN_LABELS)))
    
    # 任务类型分布
    type_keys = list(TASK_TYPE_KEYWORDS.keys())
    if template_bias > 0.5:
        type_pool = rng.sample(type_keys, k=min(2, len(type_keys)))
    else:
        type_pool = rng.sample(type_keys, k=min(5, len(type_keys)))
    
    for _ in range(count):
        template = rng.choice(template_pool)
        domain = rng.choice(domain_pool)
        task_type = rng.choice(type_pool)
        
        # 简单的模板填充（实际不需要真实内容，只需要结构特征）
        query = f"[{domain}] {template} - {task_type}任务"
        
        tasks.append({
            "query": query,
            "task_type": task_type,
            "domain": domain,
            "template_id": PROMPT_TEMPLATES.index(template) if template in PROMPT_TEMPLATES else -1
        })
    
    return tasks


def analyze_prompt_structure(tasks: List[Dict]) -> Dict:
    """
    分析 Prompt 结构差异度（基于 analyze_expert_diversity.py 的逻辑）
    
    Returns:
        dict: {
            "unique_patterns": int,
            "template_ratio": float,
            "pattern_diversity": float,
            "structure_score": int (0-100)
        }
    """
    if not tasks:
        return {
            "unique_patterns": 0,
            "template_ratio": 0,
            "pattern_diversity": 0,
            "structure_score": 0
        }
    
    # 提取结构特征
    patterns = []
    for t in tasks:
        query = t.get("query", "")
        if not query:
            continue
        
        # 结构特征
        length_bucket = len(query) // 50
        has_question = "?" in query or "？" in query
        has_instruction = any(kw in query for kw in ["请", "帮我", "需要", "希望"])
        has_list = any(c in query for c in ["1.", "2.", "①", "②", "-", "•"])
        first_chars = query[:5] if len(query) >= 5 else query
        
        pattern = (length_bucket, has_question, has_instruction, has_list, first_chars)
        patterns.append(pattern)
    
    if not patterns:
        return {
            "unique_patterns": 0,
            "template_ratio": 0,
            "pattern_diversity": 0,
            "structure_score": 0
        }
    
    unique_patterns = len(set(patterns))
    total = len(patterns)
    
    # 模板化程度
    pattern_counts = Counter(patterns)
    most_common_count = pattern_counts.most_common(1)[0][1] if pattern_counts else 0
    template_ratio = most_common_count / total if total > 0 else 0
    
    # 多样性得分
    pattern_diversity = unique_patterns / total if total > 0 else 0
    
    # StructureScore (0-100)
    base_score = pattern_diversity * 100
    template_penalty = template_ratio * 30
    structure_score = max(0, min(100, base_score - template_penalty))
    
    return {
        "unique_patterns": unique_patterns,
        "template_ratio": round(template_ratio, 3),
        "pattern_diversity": round(pattern_diversity, 3),
        "structure_score": round(structure_score)
    }


def calculate_type_score(task_types: List[str]) -> int:
    """计算任务类型多样性得分 (0-100)"""
    if not task_types:
        return 0
    
    type_counter = Counter(task_types)
    unique_types = len(type_counter)
    total = len(task_types)
    
    # 基础分：类型数量（每种15分，满分60分）
    base_score = min(unique_types * 15, 60)
    
    # 均衡性加分
    top_ratio = type_counter.most_common(1)[0][1] / total if total > 0 else 1
    balance_score = max(0, (1 - top_ratio) * 50)
    
    return min(100, round(base_score + balance_score))


def calculate_domain_score(domains: List[str]) -> int:
    """计算领域多样性得分 (0-100)"""
    if not domains:
        return 0
    
    domain_counter = Counter(domains)
    unique_domains = len(domain_counter)
    total = len(domains)
    
    # 基础分
    base_score = min(unique_domains * 12, 60)
    
    # 集中度惩罚
    top_ratio = domain_counter.most_common(1)[0][1] / total if total > 0 else 1
    if top_ratio >= 0.9:
        concentration_penalty = 40
    elif top_ratio >= 0.8:
        concentration_penalty = 30
    elif top_ratio >= 0.7:
        concentration_penalty = 20
    else:
        concentration_penalty = 0
    
    balance_score = max(0, (1 - top_ratio) * 50)
    final_score = base_score + balance_score - concentration_penalty
    
    return max(0, min(100, round(final_score)))


def determine_template_risk_level(template_ratio: float, pattern_diversity: float) -> Dict:
    """
    判断模板化风险等级
    
    Returns:
        dict: {"level": str, "description": str}
    """
    if template_ratio >= 0.3 or pattern_diversity <= 0.4:
        return {
            "level": "high",
            "level_cn": "高",
            "description": f"超过{template_ratio:.0%}的任务结构高度相似，存在模板复用嫌疑"
        }
    elif template_ratio >= 0.15 or pattern_diversity <= 0.7:
        return {
            "level": "medium",
            "level_cn": "中",
            "description": f"约{template_ratio:.0%}的任务结构相似，存在部分模板复用迹象"
        }
    else:
        return {
            "level": "low",
            "level_cn": "低",
            "description": f"任务结构差异度{pattern_diversity:.0%}，Prompt设计较多样化"
        }


def determine_quality_label(
    type_score: int,
    domain_score: int,
    structure_score: int,
    diversity_score: int,
    task_count: int,
    template_risk_level: str
) -> Dict:
    """
    确定专家质量标签
    
    基于多维度评估：
    - 高质量：多样性高 + 低模板风险 + 任务量充足
    - 风险：高模板风险 或 极端单一
    - 正常：介于两者之间
    
    Returns:
        dict: {"label": str, "label_cn": str, "reason": str}
    """
    # 高质量条件
    if (diversity_score >= 70 and 
        template_risk_level == "low" and 
        task_count >= 5 and
        type_score >= 60 and domain_score >= 60):
        return {
            "label": "high_quality",
            "label_cn": "高质量",
            "reason": f"多样性评分{diversity_score}分，任务类型和领域分布均衡，模板风险低"
        }
    
    # 风险条件
    if template_risk_level == "high":
        return {
            "label": "risk",
            "label_cn": "风险",
            "reason": f"模板化风险高，任务结构高度相似，存在批量生产嫌疑"
        }
    
    if domain_score < 30 and type_score < 30:
        return {
            "label": "risk",
            "label_cn": "风险",
            "reason": f"任务类型和领域过度集中，泛化能力存疑"
        }
    
    # 正常
    return {
        "label": "normal",
        "label_cn": "正常",
        "reason": f"多样性评分{diversity_score}分，各维度表现中等"
    }


def generate_mock_expert(talent_id: str) -> Expert:
    """
    根据 talent_id 生成一个模拟专家
    
    使用 talent_id 的 hash 作为随机种子，保证相同 ID 生成相同数据
    """
    # 用 talent_id 生成固定的随机种子
    seed = int(hashlib.md5(talent_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    
    # 学历分布
    degree_weights = [
        (DegreeLevel.MASTER, 40),
        (DegreeLevel.BACHELOR, 35),
        (DegreeLevel.PHD, 10),
        (DegreeLevel.COLLEGE, 10),
        (DegreeLevel.OTHER, 5)
    ]
    degree = rng.choices(
        [d[0] for d in degree_weights],
        weights=[d[1] for d in degree_weights]
    )[0]
    
    # 学校层级分布
    tier_weights = [
        (SchoolTier.TIER_985, 25),
        (SchoolTier.TIER_211, 20),
        (SchoolTier.OVERSEAS, 10),
        (SchoolTier.NORMAL, 35),
        (SchoolTier.OTHER, 10)
    ]
    school_tier = rng.choices(
        [t[0] for t in tier_weights],
        weights=[t[1] for t in tier_weights]
    )[0]
    
    school_name = rng.choice(MOCK_SCHOOLS[school_tier])
    
    # 技术栈
    tech_stacks = rng.sample(TECH_STACKS, k=rng.randint(1, 3))
    
    # 技能
    skills = rng.sample(SKILLS, k=rng.randint(3, 8))
    
    # 工作年限
    years_of_exp = rng.randint(1, 15)
    
    # 任务数
    task_count = int(rng.expovariate(0.08))
    task_count = max(3, min(task_count, 60))
    
    # 模板化偏向（用于生成任务）
    template_bias = rng.uniform(0.1, 0.8)
    
    # 生成任务列表
    tasks = generate_task_queries(rng, task_count, template_bias)
    
    # 分析 Prompt 结构
    structure_analysis = analyze_prompt_structure(tasks)
    
    # 计算各维度分数
    task_types = [t["task_type"] for t in tasks]
    domains = [t["domain"] for t in tasks]
    
    type_score = calculate_type_score(task_types)
    domain_score = calculate_domain_score(domains)
    structure_score = structure_analysis["structure_score"]
    
    # 总分
    diversity_score = round(type_score * 0.4 + domain_score * 0.4 + structure_score * 0.2)
    
    # 模板风险等级
    template_risk = determine_template_risk_level(
        structure_analysis["template_ratio"],
        structure_analysis["pattern_diversity"]
    )
    
    # 质量标签
    quality_info = determine_quality_label(
        type_score, domain_score, structure_score,
        diversity_score, task_count, template_risk["level"]
    )
    
    # 大厂经历
    has_big_company = rng.random() < 0.30
    if has_big_company:
        companies = rng.sample(BIG_COMPANIES, k=rng.randint(1, 2))
    else:
        companies = rng.sample(NORMAL_COMPANIES, k=rng.randint(1, 2))
    
    # 任务类型列表
    task_type_list = list(set(task_types))
    
    return Expert(
        talent_id=talent_id,
        name=rng.choice(MOCK_NAMES),
        degree=degree,
        school_tier=school_tier,
        school_name=school_name,
        tech_stacks=tech_stacks,
        skills=skills,
        years_of_experience=years_of_exp,
        task_count=task_count,
        task_types=task_type_list,
        # 新增字段
        type_score=type_score,
        domain_score=domain_score,
        structure_score=structure_score,
        diversity_score=diversity_score,
        template_ratio=structure_analysis["template_ratio"],
        unique_patterns=structure_analysis["unique_patterns"],
        template_risk_level=template_risk["level"],
        template_risk_description=template_risk["description"],
        quality_label=quality_info["label"],
        quality_label_reason=quality_info["reason"],
        domains=list(set(domains)),
        has_big_company_exp=has_big_company,
        companies=companies
    )


def generate_mock_experts(talent_ids: List[str]) -> List[Expert]:
    """批量生成模拟专家数据"""
    return [generate_mock_expert(tid) for tid in talent_ids]
