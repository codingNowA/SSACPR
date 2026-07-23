"""
面试准备服务
为用户提供针对性的面试准备建议和问题
"""
from typing import Dict, List, Any, Optional
import asyncpg
import json
import logging

logger = logging.getLogger(__name__)


class InterviewPrepService:
    """面试准备服务"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def prepare_interview(
        self, job_id: int, resume_id: int
    ) -> Dict[str, Any]:
        """
        生成面试准备方案

        Args:
            job_id: 岗位ID
            resume_id: 简历ID

        Returns:
            面试准备方案
        """
        async with self.db_pool.acquire() as conn:
            # 获取岗位信息
            job = await conn.fetchrow(
                "SELECT id, title, company, job_profile FROM jobs WHERE id = $1",
                job_id
            )
            if not job:
                raise ValueError(f"岗位不存在: {job_id}")

            # 获取简历信息
            resume = await conn.fetchrow(
                "SELECT id, parsed_data FROM resumes WHERE id = $1",
                resume_id
            )
            if not resume:
                raise ValueError(f"简历不存在: {resume_id}")

        # 解析简历数据
        parsed_data_raw = resume["parsed_data"]
        if isinstance(parsed_data_raw, str):
            try:
                profile = json.loads(parsed_data_raw)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse parsed_data for resume {resume_id}")
                profile = {}
        else:
            profile = parsed_data_raw or {}

        basic_info = profile.get("basic_info", {})
        work_experience = profile.get("work_experience", [])
        skills = profile.get("skills", [])

        # 提取技能名称列表
        if isinstance(skills, list) and len(skills) > 0:
            if isinstance(skills[0], dict):
                skill_names = [s.get("name", "") for s in skills if s.get("name")]
            else:
                skill_names = skills
        else:
            skill_names = []

        # 解析岗位数据
        job_profile_raw = job["job_profile"]
        if isinstance(job_profile_raw, str):
            try:
                job_data = json.loads(job_profile_raw)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse job_profile for job {job_id}")
                job_data = {}
        else:
            job_data = job_profile_raw or {}

        required_skills = job_data.get("required_skills", [])
        bonus_skills = job_data.get("bonus_skills", [])
        responsibilities = job_data.get("responsibilities", [])

        # 生成面试准备方案
        result = {
            "job_id": job_id,
            "job_title": job["title"],
            "company": job["company"],
            "resume_id": resume_id,
            "candidate_name": basic_info.get("name", ""),

            # 技术准备
            "technical_prep": self._generate_technical_prep(
                required_skills, bonus_skills, skill_names
            ),

            # 项目准备
            "project_prep": self._generate_project_prep(
                work_experience, responsibilities
            ),

            # 常见问题
            "common_questions": await self._get_common_questions(job["title"]),

            # 技术问题
            "technical_questions": await self._get_technical_questions(required_skills),

            # 行为问题
            "behavioral_questions": await self._get_behavioral_questions(),

            # 优势与劣势分析
            "swot_analysis": self._analyze_swot(
                skill_names, required_skills, bonus_skills, work_experience
            ),

            # 建议
            "recommendations": self._generate_recommendations(
                skill_names, required_skills, work_experience, responsibilities
            ),
        }

        return result

    def _generate_technical_prep(
        self, required_skills: List[str], bonus_skills: List[str], user_skills: List[str]
    ) -> Dict[str, Any]:
        """生成技术准备建议"""
        user_skill_set = {s.lower() for s in user_skills if s}
        required_skill_set = {s.lower() for s in required_skills if s}
        bonus_skill_set = {s.lower() for s in bonus_skills if s}

        # 已掌握的必需技能
        mastered_required = [
            s for s in required_skills
            if s.lower() in user_skill_set
        ]

        # 缺失的必需技能
        missing_required = [
            s for s in required_skills
            if s.lower() not in user_skill_set
        ]

        # 已掌握的加分技能
        mastered_bonus = [
            s for s in bonus_skills
            if s.lower() in user_skill_set
        ]

        # 重点准备领域
        focus_areas = missing_required[:5] if missing_required else mastered_required[:5]

        # 准备建议
        tips = []
        if missing_required:
            tips.append(f"优先学习缺失的核心技能: {', '.join(missing_required[:3])}")
        if mastered_required:
            tips.append(f"深入准备已掌握技能的面试题: {', '.join(mastered_required[:3])}")
        if mastered_bonus:
            tips.append(f"突出展示加分技能: {', '.join(mastered_bonus)}")

        return {
            "mastered_required": mastered_required,
            "missing_required": missing_required,
            "mastered_bonus": mastered_bonus,
            "focus_areas": focus_areas,
            "preparation_tips": tips,
        }

    def _generate_project_prep(
        self, work_experience: List[Dict], responsibilities: List[str]
    ) -> Dict[str, Any]:
        """生成项目准备建议"""
        key_projects = []

        for exp in work_experience[:3]:  # 取最近3段经历
            highlights = []
            desc = exp.get("description", "")
            achievements = exp.get("achievements", [])

            if desc:
                highlights.append(desc)
            if achievements:
                highlights.extend(achievements[:2])

            key_projects.append({
                "company": exp.get("company", ""),
                "position": exp.get("position", ""),
                "duration": f"{exp.get('start_date', '')} - {exp.get('end_date', '')}",
                "highlights": highlights,
            })

        tips = [
            "使用STAR法则准备项目经历（Situation情境、Task任务、Action行动、Result结果）",
            "准备2-3个最能体现技术能力的项目案例",
            "量化项目成果（如性能提升百分比、用户增长数据等）",
        ]

        if responsibilities:
            tips.append(f"重点准备与岗位职责相关的项目经验")

        return {
            "key_projects": key_projects,
            "preparation_tips": tips,
        }

    async def _get_common_questions(self, job_title: str) -> List[Dict[str, str]]:
        """获取常见问题"""
        common = [
            {
                "question": "请做一下自我介绍",
                "tips": "控制在2-3分钟，突出与岗位相关的经验和技能",
            },
            {
                "question": "为什么选择我们公司？",
                "tips": "事先研究公司业务、文化和产品，展示你的了解和兴趣",
            },
            {
                "question": "你的职业规划是什么？",
                "tips": "结合岗位发展路径，说明短期和长期目标",
            },
            {
                "question": "你有什么想问我的吗？",
                "tips": "准备2-3个有深度的问题，显示你对工作内容和团队的关注",
            },
        ]

        return common

    async def _get_technical_questions(self, required_skills: List[str]) -> List[Dict[str, Any]]:
        """获取技术问题"""
        if not required_skills:
            return []

        async with self.db_pool.acquire() as conn:
            # 从数据库查询相关技术问题
            questions = await conn.fetch(
                """
                SELECT id, question, difficulty, answer_points, related_skills
                FROM interview_questions
                WHERE category = 'technical'
                AND related_skills ?| $1
                LIMIT 10
                """,
                required_skills
            )

            result = []
            for q in questions:
                result.append({
                    "question_id": q["id"],
                    "question": q["question"],
                    "difficulty": q["difficulty"] or "medium",
                    "tags": q["related_skills"] or [],
                    "answer_hint": q["answer_points"] or "",
                })

            # 如果数据库没有数据，返回通用问题
            if not result:
                result = [
                    {
                        "question_id": 0,
                        "question": f"请介绍一下你在{required_skills[0]}方面的项目经验",
                        "difficulty": "medium",
                        "tags": [required_skills[0]],
                        "answer_hint": "结合具体项目，说明技术选型、遇到的挑战和解决方案",
                    }
                ] if required_skills else []

            return result

    async def _get_behavioral_questions(self) -> List[Dict[str, str]]:
        """获取行为问题"""
        async with self.db_pool.acquire() as conn:
            questions = await conn.fetch(
                """
                SELECT question, answer_points
                FROM interview_questions
                WHERE category = 'behavioral'
                LIMIT 5
                """
            )

            result = []
            for q in questions:
                result.append({
                    "question": q["question"],
                    "tips": q["answer_points"] or "",
                })

            # 如果数据库没有数据，返回通用问题
            if not result:
                result = [
                    {
                        "question": "描述一次项目中的团队合作经历",
                        "tips": "使用STAR法则，突出你的角色和贡献",
                    },
                    {
                        "question": "遇到过最大的技术挑战是什么？如何解决的？",
                        "tips": "说明问题背景、分析过程、解决方案和最终效果",
                    },
                ]

            return result

    def _analyze_swot(
        self, skills: List[str], required_skills: List[str],
        bonus_skills: List[str], work_experience: List[Dict]
    ) -> Dict[str, List[str]]:
        """SWOT分析"""
        user_skill_set = {s.lower() for s in skills if s}
        required_skill_set = {s.lower() for s in required_skills if s}

        # 优势
        strengths = []
        matched_skills = [s for s in required_skills if s.lower() in user_skill_set]
        if matched_skills:
            strengths.append(f"具备核心技能: {', '.join(matched_skills[:3])}")
        if work_experience:
            years = len(work_experience)
            strengths.append(f"拥有{years}段工作经验，项目经历丰富")

        # 劣势
        weaknesses = []
        missing_skills = [s for s in required_skills if s.lower() not in user_skill_set]
        if missing_skills:
            weaknesses.append(f"缺少部分要求技能: {', '.join(missing_skills[:3])}")

        # 机会
        opportunities = [
            "岗位提供的技术成长空间",
            "团队协作和项目经验积累",
        ]

        # 威胁
        threats = []
        if missing_skills:
            threats.append("其他候选人可能具备更全面的技能")
        threats.append("需要快速适应新的技术栈和工作环境")

        return {
            "strengths": strengths or ["待评估"],
            "weaknesses": weaknesses or ["无明显劣势"],
            "opportunities": opportunities,
            "threats": threats,
        }

    def _generate_recommendations(
        self, skills: List[str], required_skills: List[str],
        work_experience: List[Dict], responsibilities: List[str]
    ) -> List[str]:
        """生成面试建议"""
        recommendations = []

        user_skill_set = {s.lower() for s in skills if s}
        missing = [s for s in required_skills if s.lower() not in user_skill_set]

        if missing:
            recommendations.append(f"面试前快速了解: {', '.join(missing[:2])}")

        if work_experience:
            recommendations.append("准备2-3个最能体现技术能力的项目案例")

        recommendations.extend([
            "提前研究公司产品和业务，展示你的兴趣",
            "准备几个有深度的问题向面试官提问",
            "注意表达清晰、逻辑性强，展现良好的沟通能力",
        ])

        return recommendations
