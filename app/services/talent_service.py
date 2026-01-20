"""
专家数据服务

负责：
1. 解析上传的 talent_ids.txt
2. 获取专家数据（当前使用 Mock，后续可对接真实 API）
3. 计算统计指标
"""

from typing import List, Dict, Tuple
from collections import Counter
from app.models.schemas import (
    Expert, DashboardStats, TemplateRiskStats, QualityLabelStats
)
from app.services.mock_data import generate_mock_experts


class TalentService:
    """专家数据服务类"""
    
    def __init__(self):
        # 缓存专家数据（后续可改为 Redis 等）
        self._experts_cache: Dict[str, List[Expert]] = {}
    
    def parse_talent_ids(self, file_content: str) -> List[str]:
        """
        解析 talent_ids.txt 文件内容
        
        Args:
            file_content: 文件内容，每行一个 talent_id
            
        Returns:
            去重后的 talent_id 列表
        """
        lines = file_content.strip().split('\n')
        talent_ids = []
        
        for line in lines:
            tid = line.strip()
            # 跳过空行和注释
            if tid and not tid.startswith('#'):
                talent_ids.append(tid)
        
        # 去重但保持顺序
        seen = set()
        unique_ids = []
        for tid in talent_ids:
            if tid not in seen:
                seen.add(tid)
                unique_ids.append(tid)
        
        return unique_ids
    
    def fetch_experts(self, talent_ids: List[str], use_mock: bool = True) -> List[Expert]:
        """
        获取专家数据
        
        Args:
            talent_ids: 专家 ID 列表
            use_mock: 是否使用 Mock 数据（后续可对接真实 API）
            
        Returns:
            专家列表
        """
        if use_mock:
            return generate_mock_experts(talent_ids)
        else:
            # TODO: 对接真实 API
            raise NotImplementedError("真实 API 暂未实现")
    
    def calculate_stats(self, experts: List[Expert]) -> DashboardStats:
        """
        计算 Dashboard 统计数据
        
        Args:
            experts: 专家列表
            
        Returns:
            统计数据对象
        """
        if not experts:
            return DashboardStats(
                total_experts=0,
                degree_distribution={},
                school_tier_distribution={},
                tech_stack_distribution={},
                task_stats={},
                task_type_distribution={},
                kpi={}
            )
        
        total = len(experts)
        
        # 学历分布
        degree_dist = Counter(e.degree.value for e in experts)
        
        # 学校层级分布
        school_tier_dist = Counter(e.school_tier.value for e in experts)
        
        # 技术栈分布
        tech_stack_counter = Counter()
        for e in experts:
            for tech in e.tech_stacks:
                tech_stack_counter[tech] += 1
        tech_stack_dist = dict(tech_stack_counter.most_common(10))
        
        # 任务统计
        task_counts = [e.task_count for e in experts]
        total_tasks = sum(task_counts)
        avg_tasks = total_tasks / total if total > 0 else 0
        high_task_experts = sum(1 for tc in task_counts if tc >= 10)
        
        task_stats = {
            "total_tasks": total_tasks,
            "avg_tasks_per_expert": round(avg_tasks, 2),
            "high_task_expert_count": high_task_experts,
            "high_task_expert_pct": round(high_task_experts / total * 100, 1) if total > 0 else 0
        }
        
        # 任务类型分布
        task_type_counter = Counter()
        for e in experts:
            for tt in e.task_types:
                task_type_counter[tt] += 1
        task_type_dist = dict(task_type_counter)
        
        # KPI 指标
        masters_and_above = sum(1 for e in experts if e.degree.value in ["硕士", "博士"])
        elite_schools = sum(1 for e in experts if e.school_tier.value in ["985", "211", "海外名校"])
        big_company_exp = sum(1 for e in experts if e.has_big_company_exp)
        
        kpi = {
            "masters_and_above_count": masters_and_above,
            "masters_and_above_pct": round(masters_and_above / total * 100, 1) if total > 0 else 0,
            "elite_school_count": elite_schools,
            "elite_school_pct": round(elite_schools / total * 100, 1) if total > 0 else 0,
            "big_company_count": big_company_exp,
            "big_company_pct": round(big_company_exp / total * 100, 1) if total > 0 else 0,
        }
        
        # ===== 模板化风险统计 =====
        high_risk = sum(1 for e in experts if e.template_risk_level == "high")
        medium_risk = sum(1 for e in experts if e.template_risk_level == "medium")
        low_risk = sum(1 for e in experts if e.template_risk_level == "low")
        
        avg_template_ratio = sum(e.template_ratio for e in experts) / total if total > 0 else 0
        avg_unique_patterns = sum(e.unique_patterns for e in experts) / total if total > 0 else 0
        
        template_risk_stats = TemplateRiskStats(
            high_risk_count=high_risk,
            high_risk_pct=round(high_risk / total * 100, 1) if total > 0 else 0,
            medium_risk_count=medium_risk,
            medium_risk_pct=round(medium_risk / total * 100, 1) if total > 0 else 0,
            low_risk_count=low_risk,
            low_risk_pct=round(low_risk / total * 100, 1) if total > 0 else 0,
            avg_template_ratio=round(avg_template_ratio, 3),
            avg_unique_patterns=round(avg_unique_patterns, 1)
        )
        
        # ===== 质量标签统计 =====
        high_quality = sum(1 for e in experts if e.quality_label == "high_quality")
        normal_quality = sum(1 for e in experts if e.quality_label == "normal")
        risk_quality = sum(1 for e in experts if e.quality_label == "risk")
        
        quality_label_stats = QualityLabelStats(
            high_quality_count=high_quality,
            high_quality_pct=round(high_quality / total * 100, 1) if total > 0 else 0,
            normal_count=normal_quality,
            normal_pct=round(normal_quality / total * 100, 1) if total > 0 else 0,
            risk_count=risk_quality,
            risk_pct=round(risk_quality / total * 100, 1) if total > 0 else 0
        )
        
        # ===== 多样性评分分布 =====
        diversity_buckets = {"0-30": 0, "31-50": 0, "51-70": 0, "71-100": 0}
        for e in experts:
            score = e.diversity_score
            if score <= 30:
                diversity_buckets["0-30"] += 1
            elif score <= 50:
                diversity_buckets["31-50"] += 1
            elif score <= 70:
                diversity_buckets["51-70"] += 1
            else:
                diversity_buckets["71-100"] += 1
        
        # ===== 平均分数 =====
        avg_scores = {
            "type_score": round(sum(e.type_score for e in experts) / total, 1) if total > 0 else 0,
            "domain_score": round(sum(e.domain_score for e in experts) / total, 1) if total > 0 else 0,
            "structure_score": round(sum(e.structure_score for e in experts) / total, 1) if total > 0 else 0,
            "diversity_score": round(sum(e.diversity_score for e in experts) / total, 1) if total > 0 else 0,
        }
        
        return DashboardStats(
            total_experts=total,
            degree_distribution=dict(degree_dist),
            school_tier_distribution=dict(school_tier_dist),
            tech_stack_distribution=tech_stack_dist,
            task_stats=task_stats,
            task_type_distribution=task_type_dist,
            kpi=kpi,
            template_risk_stats=template_risk_stats,
            quality_label_stats=quality_label_stats,
            diversity_score_distribution=diversity_buckets,
            avg_scores=avg_scores
        )
    
    def process_upload(self, file_content: str, session_id: str) -> Tuple[List[Expert], DashboardStats]:
        """
        处理上传文件的完整流程
        
        Args:
            file_content: 文件内容
            session_id: 会话 ID（用于缓存）
            
        Returns:
            (专家列表, 统计数据)
        """
        talent_ids = self.parse_talent_ids(file_content)
        experts = self.fetch_experts(talent_ids)
        stats = self.calculate_stats(experts)
        
        # 缓存结果
        self._experts_cache[session_id] = experts
        
        return experts, stats
    
    def get_cached_experts(self, session_id: str) -> List[Expert]:
        """获取缓存的专家数据"""
        return self._experts_cache.get(session_id, [])


# 单例服务
talent_service = TalentService()
