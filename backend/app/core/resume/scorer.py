"""
简历评分器
对简历进行多维度评分分析
"""
import re
from typing import List, Optional, Dict, Any

from app.schemas.resume_structured import ResumeStructuredData
from app.schemas.resume_score import (
    ResumeScore,
    CompletenessScore,
    ProfessionalismScore,
    QuantificationScore,
    ProjectDepthScore,
    JobMatchScore,
    ScoreDimension,
)
from app.ai.llm.client import default_llm_client, LLMClientError


class ResumeScorerError(Exception):
    """简历评分异常"""
    pass


class ResumeScorer:
    """简历评分器"""

    # 权重配置
    WEIGHTS = {
        'completeness': 0.25,      # 完整性 25%
        'professionalism': 0.20,   # 专业性 20%
        'quantification': 0.20,    # 量化程度 20%
        'project_depth': 0.20,     # 项目深度 20%
        'job_match': 0.15,         # 岗位匹配 15%
    }

    def __init__(self):
        self.llm_client = default_llm_client

    async def score_resume(
        self,
        structured_data: ResumeStructuredData,
        resume_text: str,
        job_title: Optional[str] = None,
        job_description: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
    ) -> ResumeScore:
        """
        对简历进行综合评分

        Args:
            structured_data: 结构化简历数据
            resume_text: 原始简历文本
            job_title: 目标岗位
            job_description: 岗位描述
            required_skills: 岗位要求技能

        Returns:
            评分结果
        """
        try:
            # 1. 完整性评分
            completeness = self._score_completeness(structured_data)

            # 2. 专业性评分（需要 LLM 辅助）
            professionalism = await self._score_professionalism(structured_data, resume_text)

            # 3. 量化程度评分
            quantification = self._score_quantification(structured_data)

            # 4. 项目深度评分
            project_depth = self._score_project_depth(structured_data)

            # 5. 岗位匹配评分（可选）
            job_match = None
            if job_title or job_description or required_skills:
                job_match = await self._score_job_match(
                    structured_data,
                    job_title,
                    job_description,
                    required_skills
                )

            # 6. 计算总分
            dimensions = self._build_dimensions(
                completeness,
                professionalism,
                quantification,
                project_depth,
                job_match
            )

            total_score = self._calculate_total_score(dimensions)

            # 7. 生成总体反馈
            overall_feedback, strengths, weaknesses, suggestions = await self._generate_overall_feedback(
                structured_data,
                completeness,
                professionalism,
                quantification,
                project_depth,
                job_match
            )

            return ResumeScore(
                total_score=total_score,
                completeness=completeness,
                professionalism=professionalism,
                quantification=quantification,
                project_depth=project_depth,
                job_match=job_match,
                dimensions=dimensions,
                overall_feedback=overall_feedback,
                strengths=strengths,
                weaknesses=weaknesses,
                suggestions=suggestions
            )

        except Exception as e:
            raise ResumeScorerError(f"评分失败: {str(e)}")

    def _score_completeness(self, data: ResumeStructuredData) -> CompletenessScore:
        """评估简历完整性"""
        has_basic_info = data.basic_info is not None
        has_education = len(data.education) > 0
        has_work_experience = len(data.work_experience) > 0
        has_project_experience = len(data.project_experience) > 0
        has_skills = len(data.skills) > 0

        # 计算得分
        score = 0
        missing_fields = []

        if has_basic_info:
            score += 20
            # 检查基本信息字段完整性
            if data.basic_info.name:
                score += 5
            else:
                missing_fields.append("姓名")

            if data.basic_info.phone:
                score += 5
            else:
                missing_fields.append("电话")

            if data.basic_info.email:
                score += 5
            else:
                missing_fields.append("邮箱")
        else:
            missing_fields.append("基本信息")

        if has_education:
            score += 20
        else:
            missing_fields.append("教育经历")

        if has_work_experience:
            score += 20
        else:
            missing_fields.append("工作经历")

        if has_project_experience:
            score += 15
        else:
            missing_fields.append("项目经验")

        if has_skills:
            score += 10
        else:
            missing_fields.append("技能标签")

        # 生成反馈
        if score >= 90:
            feedback = "简历信息非常完整，各板块齐全。"
        elif score >= 70:
            feedback = f"简历信息较完整，建议补充：{', '.join(missing_fields[:2])}。"
        else:
            feedback = f"简历信息不够完整，缺少：{', '.join(missing_fields)}。"

        return CompletenessScore(
            total_score=score,
            has_basic_info=has_basic_info,
            has_education=has_education,
            has_work_experience=has_work_experience,
            has_project_experience=has_project_experience,
            has_skills=has_skills,
            missing_fields=missing_fields,
            feedback=feedback
        )

    async def _score_professionalism(
        self,
        data: ResumeStructuredData,
        resume_text: str
    ) -> ProfessionalismScore:
        """评估简历专业性（使用 LLM 辅助）"""
        # 基础评分
        language_quality = 70.0
        format_consistency = 70.0
        detail_richness = 50.0

        # 1. 语言质量评估
        if len(resume_text) > 500:
            language_quality += 10
        if len(resume_text) > 1000:
            language_quality += 10

        # 2. 格式一致性评估（无日期时不应给予"格式统一"加分）
        date_formats = self._extract_date_formats(data)
        if date_formats:
            unique_formats = len(set(date_formats))
            if unique_formats <= 2:  # 日期格式基本统一
                format_consistency += 15
            if unique_formats == 1:  # 日期格式完全统一
                format_consistency += 15

        # 3. 细节丰富度评估
        total_descriptions = 0
        for exp in data.work_experience:
            if exp.description and len(exp.description) > 50:
                total_descriptions += 1
        for proj in data.project_experience:
            if proj.description and len(proj.description) > 50:
                total_descriptions += 1

        if total_descriptions > 0:
            detail_richness += 20
        if total_descriptions > 2:
            detail_richness += 20
        if total_descriptions > 4:
            detail_richness += 10

        # 限制最大分数
        language_quality = min(language_quality, 100)
        format_consistency = min(format_consistency, 100)
        detail_richness = min(detail_richness, 100)

        total_score = (language_quality + format_consistency + detail_richness) / 3

        # 生成反馈
        if total_score >= 85:
            feedback = "简历专业性强，语言规范，格式统一，描述详细。"
        elif total_score >= 70:
            feedback = "简历专业性良好，建议进一步统一格式，增加细节描述。"
        else:
            feedback = "简历专业性有待提升，建议规范语言表达，统一时间格式，丰富经历描述。"

        return ProfessionalismScore(
            total_score=round(total_score, 1),
            language_quality=round(language_quality, 1),
            format_consistency=round(format_consistency, 1),
            detail_richness=round(detail_richness, 1),
            feedback=feedback
        )

    def _score_quantification(self, data: ResumeStructuredData) -> QuantificationScore:
        """评估量化程度"""
        quantified_achievements = 0
        total_achievements = 0
        examples = []

        # 检查工作经历中的量化成果
        for exp in data.work_experience:
            for achievement in exp.achievements or []:
                total_achievements += 1
                if self._is_quantified(achievement):
                    quantified_achievements += 1
                    if len(examples) < 3:
                        examples.append(achievement)

        # 检查项目经验中的量化成果
        for proj in data.project_experience:
            for achievement in proj.achievements or []:
                total_achievements += 1
                if self._is_quantified(achievement):
                    quantified_achievements += 1
                    if len(examples) < 3:
                        examples.append(achievement)

        # 计算量化率
        if total_achievements > 0:
            quantification_rate = quantified_achievements / total_achievements
            score = quantification_rate * 100
        else:
            quantification_rate = 0.0
            score = 0.0

        # 生成反馈
        if score >= 70:
            feedback = f"量化程度优秀（{quantification_rate:.0%}），成果描述具体可衡量。"
        elif score >= 40:
            feedback = f"量化程度中等（{quantification_rate:.0%}），建议增加更多数据支撑的成果。"
        else:
            feedback = f"量化程度较低（{quantification_rate:.0%}），建议用具体数字、百分比等量化成果。"

        return QuantificationScore(
            total_score=round(score, 1),
            quantified_achievements=quantified_achievements,
            total_achievements=total_achievements,
            quantification_rate=round(quantification_rate, 2),
            examples=examples,
            feedback=feedback
        )

    def _score_project_depth(self, data: ResumeStructuredData) -> ProjectDepthScore:
        """评估项目深度"""
        project_count = len(data.project_experience)

        if project_count == 0:
            return ProjectDepthScore(
                total_score=0.0,
                project_count=0,
                avg_tech_stack_count=0.0,
                avg_achievement_count=0.0,
                has_detailed_description=False,
                feedback="缺少项目经验，建议补充相关项目。"
            )

        # 计算平均技术栈数量
        total_tech_stack = sum(len(proj.tech_stack or []) for proj in data.project_experience)
        avg_tech_stack_count = total_tech_stack / project_count

        # 计算平均成果数量
        total_achievements = sum(len(proj.achievements or []) for proj in data.project_experience)
        avg_achievement_count = total_achievements / project_count

        # 检查是否有详细描述
        detailed_projects = sum(
            1 for proj in data.project_experience
            if proj.description and len(proj.description) > 100
        )
        has_detailed_description = detailed_projects >= project_count * 0.5

        # 计算得分
        score = 0.0

        # 项目数量得分 (30分)
        if project_count >= 3:
            score += 30
        elif project_count >= 2:
            score += 20
        else:
            score += 10

        # 技术栈得分 (30分)
        if avg_tech_stack_count >= 5:
            score += 30
        elif avg_tech_stack_count >= 3:
            score += 20
        elif avg_tech_stack_count >= 1:
            score += 10

        # 成果描述得分 (20分)
        if avg_achievement_count >= 3:
            score += 20
        elif avg_achievement_count >= 2:
            score += 15
        elif avg_achievement_count >= 1:
            score += 10

        # 详细描述得分 (20分)
        if has_detailed_description:
            score += 20

        # 生成反馈
        if score >= 80:
            feedback = f"项目深度优秀，共 {project_count} 个项目，技术栈丰富，成果清晰。"
        elif score >= 60:
            feedback = f"项目深度良好，共 {project_count} 个项目，建议增加技术栈和成果描述。"
        else:
            feedback = f"项目深度不足，共 {project_count} 个项目，建议丰富项目内容和技术细节。"

        return ProjectDepthScore(
            total_score=round(score, 1),
            project_count=project_count,
            avg_tech_stack_count=round(avg_tech_stack_count, 1),
            avg_achievement_count=round(avg_achievement_count, 1),
            has_detailed_description=has_detailed_description,
            feedback=feedback
        )

    async def _score_job_match(
        self,
        data: ResumeStructuredData,
        job_title: Optional[str],
        job_description: Optional[str],
        required_skills: Optional[List[str]]
    ) -> JobMatchScore:
        """评估岗位匹配度（使用 LLM 辅助）"""
        # 提取简历技能
        resume_skills = [skill.name.lower() for skill in data.skills]

        matched_skills = []
        missing_skills = []

        # 技能匹配
        if required_skills:
            for skill in required_skills:
                skill_lower = skill.lower()
                if any(skill_lower in rs or rs in skill_lower for rs in resume_skills):
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

        # 技能匹配得分
        if required_skills and len(required_skills) > 0:
            skill_score = (len(matched_skills) / len(required_skills)) * 100
        else:
            skill_score = 70.0  # 默认分数

        # 经验匹配得分
        experience_match = 70.0
        if len(data.work_experience) > 0:
            experience_match = 80.0
        if len(data.work_experience) >= 2:
            experience_match = 90.0

        # 学历匹配得分
        education_match = 70.0
        if len(data.education) > 0:
            education_match = 80.0
            # 检查是否有本科及以上学历
            for edu in data.education:
                if edu.degree and ('本科' in edu.degree or '硕士' in edu.degree or '博士' in edu.degree):
                    education_match = 90.0
                    break

        # 总分
        total_score = (skill_score * 0.5 + experience_match * 0.3 + education_match * 0.2)

        # 生成反馈
        if total_score >= 80:
            feedback = f"岗位匹配度高，技能匹配 {len(matched_skills)}/{len(required_skills) if required_skills else 0} 项。"
        elif total_score >= 60:
            feedback = f"岗位匹配度中等，建议补充技能：{', '.join(missing_skills[:3])}。"
        else:
            feedback = f"岗位匹配度较低，缺少关键技能：{', '.join(missing_skills[:5])}。"

        return JobMatchScore(
            total_score=round(total_score, 1),
            job_title=job_title,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_match=round(experience_match, 1),
            education_match=round(education_match, 1),
            feedback=feedback
        )

    def _build_dimensions(
        self,
        completeness: CompletenessScore,
        professionalism: ProfessionalismScore,
        quantification: QuantificationScore,
        project_depth: ProjectDepthScore,
        job_match: Optional[JobMatchScore]
    ) -> List[ScoreDimension]:
        """构建维度评分列表"""
        dimensions = [
            ScoreDimension(
                name="完整性",
                score=completeness.total_score,
                weight=self.WEIGHTS['completeness'],
                feedback=completeness.feedback
            ),
            ScoreDimension(
                name="专业性",
                score=professionalism.total_score,
                weight=self.WEIGHTS['professionalism'],
                feedback=professionalism.feedback
            ),
            ScoreDimension(
                name="量化程度",
                score=quantification.total_score,
                weight=self.WEIGHTS['quantification'],
                feedback=quantification.feedback
            ),
            ScoreDimension(
                name="项目深度",
                score=project_depth.total_score,
                weight=self.WEIGHTS['project_depth'],
                feedback=project_depth.feedback
            ),
        ]

        if job_match:
            dimensions.append(ScoreDimension(
                name="岗位匹配",
                score=job_match.total_score,
                weight=self.WEIGHTS['job_match'],
                feedback=job_match.feedback
            ))

        return dimensions

    def _calculate_total_score(self, dimensions: List[ScoreDimension]) -> float:
        """计算总分"""
        total_weight = sum(dim.weight for dim in dimensions)
        weighted_score = sum(dim.score * dim.weight for dim in dimensions)
        return round(weighted_score / total_weight, 1)

    async def _generate_overall_feedback(
        self,
        data: ResumeStructuredData,
        completeness: CompletenessScore,
        professionalism: ProfessionalismScore,
        quantification: QuantificationScore,
        project_depth: ProjectDepthScore,
        job_match: Optional[JobMatchScore]
    ) -> tuple[str, List[str], List[str], List[str]]:
        """生成总体反馈"""
        strengths = []
        weaknesses = []
        suggestions = []

        # 分析优势
        if completeness.total_score >= 85:
            strengths.append("简历信息完整全面")
        if professionalism.total_score >= 80:
            strengths.append("简历专业性强，格式规范")
        if quantification.total_score >= 70:
            strengths.append("成果量化清晰")
        if project_depth.total_score >= 80:
            strengths.append("项目经验丰富且深入")
        if job_match and job_match.total_score >= 80:
            strengths.append("与目标岗位匹配度高")

        # 分析不足
        if completeness.total_score < 70:
            weaknesses.append("简历信息不够完整")
            suggestions.append(f"补充缺失模块：{', '.join(completeness.missing_fields)}")
        if professionalism.total_score < 70:
            weaknesses.append("专业性有待提升")
            suggestions.append("统一时间格式，规范语言表达，增加描述细节")
        if quantification.total_score < 40:
            weaknesses.append("量化程度不足")
            suggestions.append("用具体数字、百分比、对比等方式量化工作成果")
        if project_depth.total_score < 60:
            weaknesses.append("项目深度不够")
            suggestions.append("丰富项目描述，补充技术栈和具体成果")
        if job_match and job_match.total_score < 60:
            weaknesses.append("与目标岗位匹配度较低")
            suggestions.append(f"补充关键技能：{', '.join(job_match.missing_skills[:3])}")

        # 生成总体反馈
        if len(strengths) >= 3:
            overall_feedback = f"简历整体质量优秀。主要优势：{', '.join(strengths[:3])}。"
        elif len(strengths) >= 1:
            overall_feedback = f"简历有一定亮点。优势：{', '.join(strengths)}。"
        else:
            overall_feedback = "简历有较大提升空间。"

        if weaknesses:
            overall_feedback += f" 主要不足：{', '.join(weaknesses[:2])}。"

        return overall_feedback, strengths, weaknesses, suggestions

    def _extract_date_formats(self, data: ResumeStructuredData) -> List[str]:
        """提取日期格式"""
        dates = []

        for edu in data.education:
            if edu.start_date:
                dates.append(self._detect_date_format(edu.start_date))
            if edu.end_date:
                dates.append(self._detect_date_format(edu.end_date))

        for exp in data.work_experience:
            if exp.start_date:
                dates.append(self._detect_date_format(exp.start_date))
            if exp.end_date:
                dates.append(self._detect_date_format(exp.end_date))

        return [d for d in dates if d]

    def _detect_date_format(self, date_str: str) -> Optional[str]:
        """检测日期格式"""
        if re.match(r'^\d{4}-\d{2}$', date_str):
            return 'YYYY-MM'
        elif re.match(r'^\d{4}\.\d{2}$', date_str):
            return 'YYYY.MM'
        elif re.match(r'^\d{4}/\d{2}$', date_str):
            return 'YYYY/MM'
        elif re.match(r'^\d{4}年\d{1,2}月$', date_str):
            return 'YYYY年MM月'
        return None

    def _is_quantified(self, text: str) -> bool:
        """判断文本是否包含量化信息"""
        # 检查是否包含数字、百分比等
        patterns = [
            r'\d+',  # 数字
            r'\d+%',  # 百分比
            r'\d+人',  # 人数
            r'\d+万',  # 金额
            r'\d+个',  # 数量
            r'\d+倍',  # 倍数
            r'提升\d+',  # 提升
            r'降低\d+',  # 降低
            r'增长\d+',  # 增长
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True

        return False


# 全局实例
resume_scorer = ResumeScorer()
