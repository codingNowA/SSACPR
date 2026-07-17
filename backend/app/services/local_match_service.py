"""
本地岗位匹配服务 - 不依赖LLM的规则匹配算法

基于多维度评分：
1. 技能匹配（必需+加分）
2. 经验匹配（年限+行业）
3. 学历匹配
4. 地点偏好
5. 薪资匹配

支持动态权重调整（根据岗位数据分布）
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

from app.config.match_weights import (
    MATCH_WEIGHTS,
    DYNAMIC_FACTORS,
    EDUCATION_LEVELS,
    EXPERIENCE_RANGES,
    MATCH_THRESHOLDS,
)
from app.schemas.job import (
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    MatchCategory,
    ResumeProfile,
)
from app.services.job_service import JobService

logger = logging.getLogger(__name__)


class LocalMatchService:
    """本地匹配服务"""

    def __init__(self, job_service: JobService):
        self.job_service = job_service
        self.skill_frequency_cache: Optional[Dict[str, float]] = None
        self.salary_stats_cache: Optional[Dict[str, float]] = None

    async def match(self, request: JobMatchRequest) -> JobMatchResponse:
        """
        执行本地匹配

        流程：
        1. 加载简历画像
        2. 获取候选岗位
        3. 计算岗位数据统计（用于动态权重）
        4. 对每个岗位计算匹配分数
        5. 分层返回结果
        """
        # 1. 加载简历画像
        profile = await self._load_resume_profile(request.resume_id)

        # 2. 获取候选岗位（从OpenSearch或PostgreSQL）
        candidates = await self._get_candidate_jobs(profile, request)

        if not candidates:
            return JobMatchResponse(
                resume_id=request.resume_id,
                total=0,
                highly_matched=[],
                fairly_matched=[],
                development_direction=[],
            )

        # 3. 计算岗位数据统计
        self._calculate_job_statistics(candidates)

        # 4. 计算每个岗位的匹配分数
        results: List[JobMatchResult] = []
        for candidate in candidates:
            score_detail = self._calculate_match_score(profile, candidate, request.preferences)

            result = JobMatchResult(
                job_id=candidate.get("id", 0),
                job_title=candidate.get("title", ""),
                company=candidate.get("company"),
                location=candidate.get("location"),
                salary_range=candidate.get("salary_range"),
                match_score=round(score_detail["final_score"], 1),
                matched_skills=score_detail["matched_skills"],
                missing_skills=score_detail["missing_skills"],
                match_reason=self._generate_local_reason(score_detail),
                category=self._categorize(score_detail["final_score"]),
            )
            results.append(result)

        # 5. 按分数排序并分层
        results.sort(key=lambda x: x.match_score, reverse=True)

        highly = [r for r in results if r.category == MatchCategory.highly_matched][:10]
        fairly = [r for r in results if r.category == MatchCategory.fairly_matched][:10]
        development = [r for r in results if r.category == MatchCategory.development_direction][:5]

        return JobMatchResponse(
            resume_id=request.resume_id,
            total=len(results),
            highly_matched=highly,
            fairly_matched=fairly,
            development_direction=development,
        )

    def _calculate_match_score(
        self,
        profile: ResumeProfile,
        job: Dict[str, Any],
        preferences: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        计算匹配分数

        返回：
        {
            "final_score": 85.5,
            "skill_required_score": 90.0,
            "skill_bonus_score": 80.0,
            "experience_years_score": 85.0,
            "experience_industry_score": 70.0,
            "education_score": 100.0,
            "location_score": 100.0,
            "salary_score": 80.0,
            "matched_skills": [...],
            "missing_skills": [...],
        }
        """
        scores = {}

        # 1. 必需技能匹配
        skill_result = self._score_skills(profile, job)
        scores["skill_required_score"] = skill_result["required_score"]
        scores["skill_bonus_score"] = skill_result["bonus_score"]
        scores["matched_skills"] = skill_result["matched"]
        scores["missing_skills"] = skill_result["missing"]

        # 2. 工作年限匹配
        scores["experience_years_score"] = self._score_experience_years(profile, job)

        # 3. 行业经验匹配
        scores["experience_industry_score"] = self._score_industry(profile, job)

        # 4. 学历匹配
        scores["education_score"] = self._score_education(profile, job)

        # 5. 地点偏好
        scores["location_score"] = self._score_location(profile, job, preferences)

        # 6. 薪资匹配
        scores["salary_score"] = self._score_salary(profile, job, preferences)

        # 计算加权总分
        final_score = (
            MATCH_WEIGHTS["skill_required"] * scores["skill_required_score"] +
            MATCH_WEIGHTS["skill_bonus"] * scores["skill_bonus_score"] +
            MATCH_WEIGHTS["experience_years"] * scores["experience_years_score"] +
            MATCH_WEIGHTS["experience_industry"] * scores["experience_industry_score"] +
            MATCH_WEIGHTS["education"] * scores["education_score"] +
            MATCH_WEIGHTS["location"] * scores["location_score"] +
            MATCH_WEIGHTS["salary"] * scores["salary_score"]
        )

        scores["final_score"] = final_score
        return scores

    def _score_skills(self, profile: ResumeProfile, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        技能匹配评分

        返回：
        {
            "required_score": 90.0,  # 必需技能覆盖率
            "bonus_score": 70.0,     # 加分技能覆盖率
            "matched": ["Python", "SQL"],
            "missing": ["Docker", "K8s"],
        }
        """
        resume_skills = set(s.lower().strip() for s in profile.skills if s)
        job_skills_raw = job.get("skills", []) or []

        # 如果岗位没有技能列表，从要求中提取
        if not job_skills_raw:
            from app.services.match_service import extract_skills_from_text
            job_skills_raw = extract_skills_from_text(job.get("requirements", "") or "")

        job_skills = set(s.lower().strip() for s in job_skills_raw if s)

        matched = list(resume_skills & job_skills)
        missing = list(job_skills - resume_skills)

        # 应用动态权重（稀缺技能加成，常见技能衰减）
        weighted_matched = 0.0
        for skill in matched:
            weight = self._get_skill_weight(skill)
            weighted_matched += weight

        # 必需技能评分（假设前70%是必需技能）
        required_count = max(1, int(len(job_skills) * 0.7))
        required_score = min(100, (len(matched) / required_count) * 100) if required_count > 0 else 50

        # 加分技能评分（剩余30%）
        bonus_count = len(job_skills) - required_count
        bonus_score = min(100, ((len(matched) - required_count) / max(1, bonus_count)) * 100) if bonus_count > 0 else 100

        return {
            "required_score": max(0, required_score),
            "bonus_score": max(0, bonus_score),
            "matched": sorted(matched),
            "missing": sorted(missing),
        }

    def _score_experience_years(self, profile: ResumeProfile, job: Dict[str, Any]) -> float:
        """工作年限匹配评分"""
        # 从简历中提取工作年限
        resume_years = self._extract_years_from_profile(profile)

        # 从岗位中提取要求的年限范围
        job_exp_text = job.get("experience", "") or job.get("requirements", "")
        job_years_range = self._extract_experience_range(job_exp_text)

        if job_years_range == (0, 0):  # 不限经验
            return 100.0

        min_years, max_years = job_years_range

        if resume_years < min_years:
            # 经验不足，按比例扣分
            return max(0, (resume_years / min_years) * 100)
        elif min_years <= resume_years <= max_years:
            # 完全符合
            return 100.0
        else:
            # 经验过高，轻微扣分（可能overqualified）
            return max(70, 100 - (resume_years - max_years) * 5)

    def _score_industry(self, profile: ResumeProfile, job: Dict[str, Any]) -> float:
        """行业经验匹配评分"""
        # 简单的关键词匹配
        resume_text = " ".join([profile.target_position or "", profile.summary or ""])
        job_industry = job.get("industry", "")

        if not job_industry:
            return 50.0  # 无行业要求，给中间分

        if job_industry.lower() in resume_text.lower():
            return 100.0

        return 30.0  # 无相关行业经验

    def _score_education(self, profile: ResumeProfile, job: Dict[str, Any]) -> float:
        """学历匹配评分"""
        # 从教育经历列表中提取最高学历
        resume_edu = "本科"  # 默认值
        if profile.education and len(profile.education) > 0:
            # 取第一个教育经历的学历
            resume_edu = profile.education[0].degree or "本科"

        job_edu_text = job.get("education", "") or job.get("requirements", "")
        job_edu = self._extract_education_requirement(job_edu_text)

        resume_level = EDUCATION_LEVELS.get(resume_edu, 5)
        job_level = EDUCATION_LEVELS.get(job_edu, 1)

        if resume_level >= job_level:
            return 100.0
        else:
            # 学历不足，按比例扣分
            return max(0, (resume_level / job_level) * 100)

    def _score_location(
        self,
        profile: ResumeProfile,
        job: Dict[str, Any],
        preferences: Optional[Any] = None
    ) -> float:
        """地点偏好匹配"""
        job_location = job.get("location", "")

        # 优先使用偏好设置
        if preferences and hasattr(preferences, 'cities') and preferences.cities:
            if job_location in preferences.cities:
                return 100.0
            return 30.0

        # 如果没有偏好设置，默认返回中等分数
        return 70.0

        return 50.0  # 无偏好，给中间分

    def _score_salary(
        self,
        profile: ResumeProfile,
        job: Dict[str, Any],
        preferences: Optional[Any] = None
    ) -> float:
        """薪资匹配评分"""
        job_salary_text = job.get("salary_range", "")
        job_salary_avg = self._parse_salary_average(job_salary_text)

        if job_salary_avg == 0:
            return 50.0  # 无薪资信息，给中间分

        # 检查是否有薪资异常（偏离市场均值）
        if self.salary_stats_cache:
            mean = self.salary_stats_cache.get("mean", 0)
            std = self.salary_stats_cache.get("std", 0)
            if mean > 0 and std > 0:
                if abs(job_salary_avg - mean) > 2 * std:
                    # 薪资异常，降权
                    penalty_factor = DYNAMIC_FACTORS["salary_outlier_penalty"]
                    return 50.0 * penalty_factor

        # 与期望薪资对比
        if preferences and hasattr(preferences, 'min_salary') and preferences.min_salary:
            expected_min = preferences.min_salary
            expected_max = getattr(preferences, 'max_salary', expected_min * 1.5)

            if expected_min <= job_salary_avg <= expected_max:
                return 100.0
            elif job_salary_avg < expected_min:
                return max(20, (job_salary_avg / expected_min) * 100)
            else:
                return max(70, 100 - ((job_salary_avg - expected_max) / expected_max) * 30)

        return 80.0  # 无期望薪资，给较高分

    def _get_skill_weight(self, skill: str) -> float:
        """
        获取技能权重（根据出现频率）

        稀缺技能加权，常见技能降权
        """
        if not self.skill_frequency_cache:
            return 1.0

        frequency = self.skill_frequency_cache.get(skill.lower(), 0.5)

        if frequency < 0.1:  # 出现频率 < 10%，稀缺
            return DYNAMIC_FACTORS["rare_skill_boost"]
        elif frequency > 0.5:  # 出现频率 > 50%，常见
            return DYNAMIC_FACTORS["common_skill_decay"]
        else:
            return 1.0

    def _calculate_job_statistics(self, jobs: List[Dict[str, Any]]) -> None:
        """计算岗位数据统计（用于动态权重）"""
        # 统计技能出现频率
        all_skills = []
        salaries = []

        for job in jobs:
            skills = job.get("skills", []) or []
            all_skills.extend([s.lower() for s in skills])

            salary_avg = self._parse_salary_average(job.get("salary_range", ""))
            if salary_avg > 0:
                salaries.append(salary_avg)

        # 技能频率
        total_jobs = len(jobs)
        skill_counts = Counter(all_skills)
        self.skill_frequency_cache = {
            skill: count / total_jobs
            for skill, count in skill_counts.items()
        }

        # 薪资统计
        if salaries:
            import numpy as np
            self.salary_stats_cache = {
                "mean": np.mean(salaries),
                "std": np.std(salaries),
            }

    def _categorize(self, score: float) -> MatchCategory:
        """根据分数分类"""
        if score >= MATCH_THRESHOLDS["highly_matched"]:
            return MatchCategory.highly_matched
        elif score >= MATCH_THRESHOLDS["fairly_matched"]:
            return MatchCategory.fairly_matched
        else:
            return MatchCategory.development_direction

    def _generate_local_reason(self, score_detail: Dict[str, Any]) -> str:
        """生成本地匹配理由"""
        reasons = []

        # 技能匹配
        if score_detail["skill_required_score"] >= 80:
            reasons.append(f"技能匹配度高({len(score_detail['matched_skills'])}项匹配)")
        elif score_detail["skill_required_score"] >= 60:
            reasons.append(f"技能基本匹配({len(score_detail['matched_skills'])}项匹配)")
        else:
            reasons.append(f"技能匹配度较低，缺少{len(score_detail['missing_skills'])}项关键技能")

        # 经验匹配
        if score_detail["experience_years_score"] >= 80:
            reasons.append("工作经验符合要求")
        elif score_detail["experience_years_score"] < 60:
            reasons.append("工作经验不足")

        # 学历匹配
        if score_detail["education_score"] < 100:
            reasons.append("学历未达到最优要求")

        # 地点和薪资
        if score_detail["location_score"] == 100:
            reasons.append("工作地点符合期望")
        if score_detail["salary_score"] >= 80:
            reasons.append("薪资水平合理")

        return "；".join(reasons) if reasons else "综合评估匹配"

    # 辅助方法
    def _extract_years_from_profile(self, profile: ResumeProfile) -> int:
        """从简历中提取工作年限"""
        # 简单实现：从工作经历文本中提取年份数量
        summary = profile.summary or ""
        years_match = re.findall(r'(\d+)\s*年', summary)
        if years_match:
            return int(years_match[0])
        return 0

    def _extract_experience_range(self, text: str) -> Tuple[int, int]:
        """从文本中提取经验年限范围"""
        for key, (min_y, max_y) in EXPERIENCE_RANGES.items():
            if key in text:
                return (min_y, max_y)
        return (0, 0)

    def _extract_education_requirement(self, text: str) -> str:
        """从文本中提取学历要求"""
        for edu in ["博士", "硕士", "本科", "大专"]:
            if edu in text:
                return edu
        return "不限"

    def _parse_salary_average(self, salary_text: str) -> float:
        """解析薪资范围，返回平均值（单位：千元）"""
        if not salary_text:
            return 0.0

        # 提取数字
        numbers = re.findall(r'(\d+)', salary_text)
        if len(numbers) >= 2:
            min_salary = int(numbers[0])
            max_salary = int(numbers[1])
            return (min_salary + max_salary) / 2
        elif len(numbers) == 1:
            return int(numbers[0])

        return 0.0

    async def _load_resume_profile(self, resume_id: int) -> ResumeProfile:
        """加载简历画像"""
        from app.services.job_service import get_db_pool
        import json

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT parsed_data FROM resumes WHERE id = $1",
                resume_id,
            )

        if row is None or row["parsed_data"] is None:
            raise ValueError(f"简历 ID {resume_id} 不存在或未解析")

        parsed = row["parsed_data"]
        if isinstance(parsed, str):
            parsed = json.loads(parsed)

        return self._build_profile_from_parsed(parsed)

    def _build_profile_from_parsed(self, parsed: Dict[str, Any]) -> ResumeProfile:
        """将 parsed_data JSON 转换为 ResumeProfile"""
        from app.schemas.job import EducationItem, ExperienceItem, ProjectItem

        # 提取技能
        skills = []
        skills_data = parsed.get("skills", [])

        if isinstance(skills_data, list):
            for skill in skills_data:
                if isinstance(skill, dict) and skill.get("name"):
                    # SkillTag 格式: {"name": "Python", "level": "熟练"}
                    skills.append(skill["name"])
                elif isinstance(skill, str):
                    # 字符串格式: "Python"
                    skills.append(skill)

        # 提取基本信息
        basic_info = parsed.get("basic_info", {})
        name = basic_info.get("name", "")
        target_position = basic_info.get("job_intention", "")

        # 提取教育经历
        education_items = []
        education_data = parsed.get("education", [])
        for edu in education_data:
            education_items.append(EducationItem(
                school=edu.get("school"),
                degree=edu.get("degree"),
                major=edu.get("major"),
                graduation_year=edu.get("end_date"),
            ))

        # 提取工作经历
        experience_items = []
        work_data = parsed.get("work_experience", [])
        for work in work_data:
            experience_items.append(ExperienceItem(
                company=work.get("company"),
                position=work.get("position"),
                duration=f"{work.get('start_date', '')} - {work.get('end_date', '至今')}",
                description=work.get("description"),
            ))

        # 提取项目经历
        project_items = []
        project_data = parsed.get("project_experience", [])
        for proj in project_data:
            project_items.append(ProjectItem(
                name=proj.get("name"),
                role=proj.get("role"),
                description=proj.get("description"),
                technologies=proj.get("tech_stack", []),
            ))

        # 构建摘要
        summary = parsed.get("self_evaluation", "")
        if not summary:
            summary_parts = []
            if name:
                summary_parts.append(f"姓名: {name}")
            if target_position:
                summary_parts.append(f"求职意向: {target_position}")
            if skills:
                summary_parts.append(f"技能: {', '.join(skills[:5])}")
            if work_data:
                summary_parts.append(f"工作经历: {len(work_data)}段")
            summary = "; ".join(summary_parts)

        return ResumeProfile(
            name=name,
            skills=skills,
            education=education_items,
            experience=experience_items,
            projects=project_items,
            target_position=target_position,
            summary=summary,
        )

    async def _get_candidate_jobs(
        self,
        profile: ResumeProfile,
        request: JobMatchRequest
    ) -> List[Dict[str, Any]]:
        """获取候选岗位列表"""
        # 构建搜索关键词
        search_keywords = profile.skills[:15] if profile.skills else []
        if profile.target_position:
            search_keywords = [profile.target_position] + search_keywords

        # 从 JobService 召回岗位
        candidates = await self.job_service.recall_jobs(
            keywords=search_keywords if search_keywords else None,
            preferences=request.preferences,
            size=100,
        )

        return candidates


# 单例
local_match_service = None


def get_local_match_service(job_service: JobService) -> LocalMatchService:
    """获取本地匹配服务实例"""
    global local_match_service
    if local_match_service is None:
        local_match_service = LocalMatchService(job_service)
    return local_match_service
