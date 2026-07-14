"""
岗位难度分析服务
实现岗位难度的基础判断逻辑
"""
import re
from typing import List, Dict, Optional
from app.schemas.job_difficulty import (
    JobDifficultyRequest,
    JobDifficultyResponse,
    DifficultyLevel,
    DifficultyFactor
)


class JobDifficultyAnalyzer:
    """岗位难度分析器"""

    # 难度等级阈值
    DIFFICULTY_THRESHOLDS = {
        DifficultyLevel.VERY_EASY: (0, 20),
        DifficultyLevel.EASY: (20, 40),
        DifficultyLevel.MEDIUM: (40, 60),
        DifficultyLevel.HARD: (60, 80),
        DifficultyLevel.VERY_HARD: (80, 100),
    }

    # 学历权重映射
    EDUCATION_WEIGHTS = {
        "博士": 10,
        "硕士": 8,
        "研究生": 8,
        "本科": 5,
        "大专": 3,
        "专科": 3,
        "不限": 2,
    }

    # 经验年限权重
    EXPERIENCE_WEIGHTS = {
        "10年以上": 10,
        "8-10年": 9,
        "5-8年": 8,
        "3-5年": 6,
        "1-3年": 4,
        "1年": 3,
        "应届": 2,
        "不限": 1,
    }

    def __init__(self):
        """初始化分析器"""
        pass

    def analyze(self, request: JobDifficultyRequest) -> JobDifficultyResponse:
        """
        分析岗位难度

        Args:
            request: 岗位难度判断请求

        Returns:
            岗位难度判断响应
        """
        # 1. 分析各个难度因素
        factors = self._analyze_factors(request)

        # 2. 计算总体难度得分
        total_score = self._calculate_total_score(factors)

        # 3. 确定难度等级
        difficulty_level = self._determine_difficulty_level(total_score)

        # 4. 生成难度总结
        summary = self._generate_summary(request, difficulty_level, total_score)

        # 5. 生成备考建议
        suggestions = self._generate_suggestions(request, difficulty_level, factors)

        # 6. 生成竞争分析
        competitive_analysis = self._generate_competitive_analysis(request, difficulty_level)

        # 7. 预估准备时间
        estimated_preparation_time = self._estimate_preparation_time(difficulty_level, factors)

        # 8. 确定适合人群
        target_audience = self._determine_target_audience(request, difficulty_level)

        # 9. 识别主要挑战
        key_challenges = self._identify_key_challenges(request, factors)

        # 10. 估算成功率
        success_rate_estimate = self._estimate_success_rate(difficulty_level, total_score)

        # 11. 分析市场需求
        market_demand = self._analyze_market_demand(request)

        # 12. 职业发展前景
        career_development = self._analyze_career_development(request)

        return JobDifficultyResponse(
            job_title=request.job_title,
            difficulty_level=difficulty_level,
            difficulty_score=round(total_score, 2),
            difficulty_factors=factors,
            summary=summary,
            suggestions=suggestions,
            competitive_analysis=competitive_analysis,
            estimated_preparation_time=estimated_preparation_time,
            target_audience=target_audience,
            key_challenges=key_challenges,
            success_rate_estimate=success_rate_estimate,
            market_demand=market_demand,
            career_development=career_development
        )

    def _analyze_factors(self, request: JobDifficultyRequest) -> List[DifficultyFactor]:
        """分析各个难度因素"""
        factors = []

        # 1. 学历要求因素
        education_factor = self._analyze_education(request.education_requirement)
        if education_factor:
            factors.append(education_factor)

        # 2. 经验要求因素
        experience_factor = self._analyze_experience(request.experience_requirement)
        if experience_factor:
            factors.append(experience_factor)

        # 3. 技术要求因素
        tech_factor = self._analyze_technical_requirements(request.requirements)
        if tech_factor:
            factors.append(tech_factor)

        # 4. 职位级别因素
        level_factor = self._analyze_job_level(request.job_title)
        if level_factor:
            factors.append(level_factor)

        # 5. 薪资水平因素
        salary_factor = self._analyze_salary(request.salary_range)
        if salary_factor:
            factors.append(salary_factor)

        return factors

    def _analyze_education(self, education: Optional[str]) -> Optional[DifficultyFactor]:
        """分析学历要求"""
        if not education:
            return None

        score = 5.0  # 默认分数
        for edu_level, weight in self.EDUCATION_WEIGHTS.items():
            if edu_level in education:
                score = weight
                break

        return DifficultyFactor(
            factor_name="学历要求",
            score=score,
            weight=0.2,
            description=f"要求{education}学历，难度评分：{score}/10"
        )

    def _analyze_experience(self, experience: Optional[str]) -> Optional[DifficultyFactor]:
        """分析工作经验要求"""
        if not experience:
            return None

        score = 5.0  # 默认分数
        description = experience

        # 提取年限数字
        years_match = re.findall(r'(\d+)', experience)
        if years_match:
            years = int(years_match[-1])  # 取最大年限
            if years >= 10:
                score = 10.0
            elif years >= 8:
                score = 9.0
            elif years >= 5:
                score = 8.0
            elif years >= 3:
                score = 6.5
            elif years >= 1:
                score = 4.0
            else:
                score = 2.0
        elif "应届" in experience or "无经验" in experience:
            score = 2.0

        return DifficultyFactor(
            factor_name="工作经验",
            score=score,
            weight=0.25,
            description=f"要求{description}，经验门槛评分：{score}/10"
        )

    def _analyze_technical_requirements(self, requirements: Optional[str]) -> Optional[DifficultyFactor]:
        """分析技术要求"""
        if not requirements:
            return None

        score = 5.0
        tech_keywords = []

        # 高级技术关键词
        advanced_keywords = [
            "架构", "分布式", "微服务", "高并发", "大数据", "机器学习",
            "深度学习", "算法", "性能优化", "系统设计", "技术选型"
        ]

        # 中级技术关键词
        intermediate_keywords = [
            "框架", "数据库", "Redis", "MySQL", "MongoDB", "Docker",
            "Kubernetes", "Spring", "Vue", "React"
        ]

        # 统计关键词出现次数
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in requirements)
        intermediate_count = sum(1 for keyword in intermediate_keywords if keyword in requirements)

        # 计算分数
        if advanced_count >= 3:
            score = 9.0
            tech_keywords = [kw for kw in advanced_keywords if kw in requirements]
        elif advanced_count >= 1:
            score = 7.5
            tech_keywords = [kw for kw in advanced_keywords if kw in requirements]
        elif intermediate_count >= 3:
            score = 6.0
            tech_keywords = [kw for kw in intermediate_keywords if kw in requirements]
        elif intermediate_count >= 1:
            score = 4.5
            tech_keywords = [kw for kw in intermediate_keywords if kw in requirements]
        else:
            score = 3.0

        tech_desc = f"涉及技术：{', '.join(tech_keywords[:5])}" if tech_keywords else "基础技术要求"

        return DifficultyFactor(
            factor_name="技术要求",
            score=score,
            weight=0.3,
            description=f"{tech_desc}，技术难度评分：{score}/10"
        )

    def _analyze_job_level(self, job_title: str) -> Optional[DifficultyFactor]:
        """分析职位级别"""
        score = 5.0
        level = "中级"

        # 高级职位关键词
        if any(keyword in job_title for keyword in ["总监", "VP", "CTO", "首席", "专家"]):
            score = 10.0
            level = "高管级"
        elif any(keyword in job_title for keyword in ["经理", "主管", "Leader", "Tech Lead"]):
            score = 8.5
            level = "管理级"
        elif any(keyword in job_title for keyword in ["高级", "资深", "Senior"]):
            score = 7.0
            level = "高级"
        elif any(keyword in job_title for keyword in ["初级", "Junior", "助理", "实习"]):
            score = 3.0
            level = "初级"
        else:
            score = 5.0
            level = "中级"

        return DifficultyFactor(
            factor_name="职位级别",
            score=score,
            weight=0.15,
            description=f"职位级别为{level}，难度评分：{score}/10"
        )

    def _analyze_salary(self, salary_range: Optional[str]) -> Optional[DifficultyFactor]:
        """分析薪资水平"""
        if not salary_range:
            return None

        score = 5.0

        # 提取薪资数字（k为单位）
        salary_numbers = re.findall(r'(\d+)[kK]', salary_range)
        if salary_numbers:
            max_salary = max([int(s) for s in salary_numbers])

            if max_salary >= 50:
                score = 9.5
            elif max_salary >= 35:
                score = 8.0
            elif max_salary >= 25:
                score = 6.5
            elif max_salary >= 15:
                score = 5.0
            elif max_salary >= 10:
                score = 3.5
            else:
                score = 2.0

        return DifficultyFactor(
            factor_name="薪资水平",
            score=score,
            weight=0.1,
            description=f"薪资范围{salary_range}，薪资竞争力评分：{score}/10"
        )

    def _calculate_total_score(self, factors: List[DifficultyFactor]) -> float:
        """计算总体难度得分（加权平均）"""
        if not factors:
            return 50.0  # 默认中等难度

        weighted_sum = sum(factor.score * factor.weight for factor in factors)
        total_weight = sum(factor.weight for factor in factors)

        if total_weight == 0:
            return 50.0

        # 转换为0-100分制
        return (weighted_sum / total_weight) * 10

    def _determine_difficulty_level(self, score: float) -> DifficultyLevel:
        """根据得分确定难度等级"""
        for level, (min_score, max_score) in self.DIFFICULTY_THRESHOLDS.items():
            if min_score <= score < max_score:
                return level
        return DifficultyLevel.VERY_HARD

    def _generate_summary(
        self,
        request: JobDifficultyRequest,
        level: DifficultyLevel,
        score: float
    ) -> str:
        """生成难度总结"""
        level_desc = {
            DifficultyLevel.VERY_EASY: "很低",
            DifficultyLevel.EASY: "较低",
            DifficultyLevel.MEDIUM: "中等",
            DifficultyLevel.HARD: "较高",
            DifficultyLevel.VERY_HARD: "很高",
        }

        summary = f"【{request.job_title}】岗位整体难度为{level_desc[level]}（难度得分：{score:.1f}/100）。"

        if level == DifficultyLevel.VERY_HARD:
            summary += "该岗位要求非常高，需要深厚的专业功底和丰富的实战经验，建议有充分准备后再投递。"
        elif level == DifficultyLevel.HARD:
            summary += "该岗位有一定门槛，需要扎实的技术能力和相关项目经验，建议提前做好充分准备。"
        elif level == DifficultyLevel.MEDIUM:
            summary += "该岗位难度适中，具备相关专业背景和一定实践经验即可胜任。"
        elif level == DifficultyLevel.EASY:
            summary += "该岗位入门难度较低，适合有一定基础的求职者投递。"
        else:
            summary += "该岗位门槛较低，适合应届生或转行人士投递。"

        return summary

    def _generate_suggestions(
        self,
        request: JobDifficultyRequest,
        level: DifficultyLevel,
        factors: List[DifficultyFactor]
    ) -> List[str]:
        """生成备考建议"""
        suggestions = []

        # 根据难度等级给出通用建议
        if level in [DifficultyLevel.HARD, DifficultyLevel.VERY_HARD]:
            suggestions.append("建议系统梳理专业知识体系，查漏补缺")
            suggestions.append("准备2-3个深度项目案例，突出技术亮点和解决方案")
        elif level == DifficultyLevel.MEDIUM:
            suggestions.append("准备1-2个相关项目经验，能清晰阐述技术细节")
            suggestions.append("复习岗位相关的核心技术栈")

        # 根据具体因素给出针对性建议
        for factor in factors:
            if factor.factor_name == "技术要求" and factor.score >= 7:
                suggestions.append("深入学习岗位要求的高级技术（如微服务、分布式系统等）")
            elif factor.factor_name == "工作经验" and factor.score >= 7:
                suggestions.append("整理过往工作经历，突出技术成长路径和核心贡献")
            elif factor.factor_name == "学历要求" and factor.score >= 8:
                suggestions.append("如学历不够，建议通过技术博客、开源项目等方式证明实力")

        # 通用建议
        suggestions.append("准备常见面试问题，包括技术面试和行为面试")
        suggestions.append("了解目标公司的业务和技术栈，展现求职诚意")

        return suggestions[:5]  # 返回最多5条建议

    def _generate_competitive_analysis(
        self,
        request: JobDifficultyRequest,
        level: DifficultyLevel
    ) -> str:
        """生成竞争分析"""
        if level == DifficultyLevel.VERY_HARD:
            return "该岗位属于高端人才岗位，竞争非常激烈。建议有5年以上相关经验、技术能力突出者投递，成功率会更高。"
        elif level == DifficultyLevel.HARD:
            return "该岗位竞争较为激烈，建议有3年以上相关经验且技术扎实者投递。提前准备好项目案例和技术方案将大幅提升竞争力。"
        elif level == DifficultyLevel.MEDIUM:
            return "该岗位竞争适中，具备相关专业背景和1-2年实践经验即有较大机会。建议充分准备面试，展现学习能力和潜力。"
        elif level == DifficultyLevel.EASY:
            return "该岗位竞争压力较小，适合应届生或1年左右工作经验者投递。建议展现积极学习态度和快速成长能力。"
        else:
            return "该岗位门槛较低，竞争相对缓和，适合入门级求职者。建议突出个人学习能力和发展潜力。"

    def _estimate_preparation_time(
        self,
        level: DifficultyLevel,
        factors: List[DifficultyFactor]
    ) -> str:
        """预估准备时间"""
        if level == DifficultyLevel.VERY_HARD:
            return "6-12周（建议系统性准备）"
        elif level == DifficultyLevel.HARD:
            return "4-8周（需要深度准备）"
        elif level == DifficultyLevel.MEDIUM:
            return "2-4周（适度准备）"
        elif level == DifficultyLevel.EASY:
            return "1-2周（基础准备）"
        else:
            return "3-7天（快速准备）"

    def _determine_target_audience(
        self,
        request: JobDifficultyRequest,
        level: DifficultyLevel
    ) -> str:
        """确定适合人群"""
        audience_parts = []

        # 根据经验要求
        if request.experience_requirement:
            exp_text = request.experience_requirement
            if "应届" in exp_text or "无经验" in exp_text:
                audience_parts.append("应届毕业生")
            elif any(year in exp_text for year in ["1-3", "1年", "2年"]):
                audience_parts.append("1-3年工作经验者")
            elif any(year in exp_text for year in ["3-5", "3年", "4年", "5年"]):
                audience_parts.append("3-5年工作经验者")
            elif any(year in exp_text for year in ["5-8", "5年以上"]):
                audience_parts.append("5年以上资深从业者")
            else:
                audience_parts.append("有相关工作经验者")

        # 根据学历要求
        if request.education_requirement:
            if "硕士" in request.education_requirement or "博士" in request.education_requirement:
                audience_parts.append("研究生及以上学历")
            elif "本科" in request.education_requirement:
                audience_parts.append("本科及以上学历")

        # 根据技能要求
        if request.required_skills and len(request.required_skills) > 0:
            tech_level = "熟悉" if level in [DifficultyLevel.EASY, DifficultyLevel.VERY_EASY] else "精通"
            audience_parts.append(f"{tech_level}{request.required_skills[0]}等技术")

        if not audience_parts:
            # 根据难度等级给出默认人群
            if level == DifficultyLevel.VERY_HARD:
                return "资深专家、技术带头人"
            elif level == DifficultyLevel.HARD:
                return "高级工程师、有丰富项目经验者"
            elif level == DifficultyLevel.MEDIUM:
                return "中级工程师、有一定项目经验者"
            elif level == DifficultyLevel.EASY:
                return "初级工程师、应届毕业生"
            else:
                return "技术入门者、转行人士"

        return "、".join(audience_parts)

    def _identify_key_challenges(
        self,
        request: JobDifficultyRequest,
        factors: List[DifficultyFactor]
    ) -> List[str]:
        """识别主要挑战"""
        challenges = []

        # 从难度因素中提取挑战
        for factor in factors:
            if factor.score >= 7:
                if factor.factor_name == "技术要求":
                    if request.requirements:
                        # 提取高级技术关键词
                        advanced_keywords = [
                            "架构", "分布式", "微服务", "高并发",
                            "大数据", "机器学习", "算法", "性能优化"
                        ]
                        found_keywords = [kw for kw in advanced_keywords if kw in request.requirements]
                        if found_keywords:
                            challenges.append(f"{found_keywords[0]}相关技术能力")

                elif factor.factor_name == "工作经验":
                    challenges.append("丰富的项目实战经验")

                elif factor.factor_name == "学历要求":
                    challenges.append("学历门槛较高")

                elif factor.factor_name == "职位级别":
                    if "高级" in request.job_title or "资深" in request.job_title:
                        challenges.append("需要较强的技术深度和广度")
                    elif "经理" in request.job_title or "主管" in request.job_title:
                        challenges.append("需要具备管理和协调能力")

        # 根据岗位职责添加挑战
        if request.job_responsibilities:
            if "架构" in request.job_responsibilities:
                challenges.append("系统架构设计能力")
            if "优化" in request.job_responsibilities or "性能" in request.job_responsibilities:
                challenges.append("性能调优和问题排查能力")
            if "团队" in request.job_responsibilities or "管理" in request.job_responsibilities:
                challenges.append("团队协作和管理能力")

        # 如果没有识别到挑战，给出默认挑战
        if not challenges:
            challenges.append("技术能力达标")
            challenges.append("项目经验积累")

        return challenges[:5]  # 返回最多5个挑战

    def _estimate_success_rate(
        self,
        level: DifficultyLevel,
        score: float
    ) -> str:
        """估算成功率"""
        if level == DifficultyLevel.VERY_HARD:
            return "竞争激烈，符合条件者成功率约20-30%"
        elif level == DifficultyLevel.HARD:
            return "有一定难度，符合条件者成功率约30-40%"
        elif level == DifficultyLevel.MEDIUM:
            return "难度适中，符合条件者成功率约40-60%"
        elif level == DifficultyLevel.EASY:
            return "难度较低，符合条件者成功率约60-80%"
        else:
            return "门槛较低，符合条件者成功率约80%以上"

    def _analyze_market_demand(
        self,
        request: JobDifficultyRequest
    ) -> str:
        """分析市场需求"""
        job_title = request.job_title.lower()

        # 热门技术岗位
        hot_keywords = {
            "java": "Java开发岗位市场需求量大，一线城市需求尤其旺盛",
            "python": "Python岗位需求持续增长，在数据分析、AI领域需求强劲",
            "前端": "前端开发岗位需求稳定，Vue/React技术栈需求量大",
            "算法": "算法工程师需求旺盛，但对学历和技术要求较高",
            "测试": "测试岗位需求稳定，自动化测试工程师需求增长",
            "运维": "运维岗位向DevOps转型，云原生技术需求增加",
            "产品": "产品经理岗位竞争激烈，需要综合能力",
            "数据": "数据相关岗位需求持续增长，大数据、数据分析方向热门"
        }

        for keyword, description in hot_keywords.items():
            if keyword in job_title:
                return description

        # 根据行业判断
        if request.industry:
            industry = request.industry
            if "互联网" in industry:
                return "互联网行业技术岗位需求旺盛，发展机会多"
            elif "金融" in industry:
                return "金融行业技术岗位稳定，对技术和业务理解要求高"
            elif "教育" in industry:
                return "教育行业稳步发展，在线教育领域需求增长"

        return "市场需求因地区和细分方向而异，建议关注目标城市的招聘趋势"

    def _analyze_career_development(
        self,
        request: JobDifficultyRequest
    ) -> str:
        """职业发展前景"""
        job_title = request.job_title.lower()

        # 根据职位类型给出发展建议
        if "初级" in job_title or "junior" in job_title:
            return "初级岗位是职业起点，可向中高级工程师、技术专家方向发展"
        elif "高级" in job_title or "senior" in job_title:
            return "高级岗位可向架构师、技术专家或技术管理方向发展，晋升空间较大"
        elif "架构" in job_title:
            return "架构师是技术路线的高级岗位，可向技术总监、CTO方向发展"
        elif "经理" in job_title or "主管" in job_title:
            return "管理岗位可向高级管理者方向发展，需要平衡技术和管理能力"
        elif "专家" in job_title:
            return "技术专家是技术深度方向的发展路径，可成为领域权威"
        elif "算法" in job_title or "ai" in job_title or "机器学习" in job_title:
            return "AI/算法方向发展前景广阔，可向算法专家、AI架构师方向发展"
        elif "数据" in job_title:
            return "数据方向发展稳定，可向数据科学家、数据架构师方向发展"
        elif "测试" in job_title:
            return "测试岗位可向测试开发、质量专家、测试架构师方向发展"
        elif "运维" in job_title:
            return "运维可向DevOps工程师、SRE、云架构师方向转型发展"
        elif "产品" in job_title:
            return "产品岗位可向高级产品经理、产品总监方向发展"
        else:
            return "技术岗位发展路径多样，可选择技术深度或管理方向，建议根据个人兴趣规划"


# 创建全局分析器实例
job_difficulty_analyzer = JobDifficultyAnalyzer()
