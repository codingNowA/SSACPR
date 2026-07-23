"""
简历优化器
生成可执行的修改建议和面向岗位的优化文案
"""
import json
import logging
from typing import List, Optional, Dict, Any

from app.schemas.resume_structured import ResumeStructuredData
from app.schemas.resume_score import ResumeScore
from app.schemas.resume_optimize import (
    ResumeOptimization,
    OptimizationSuggestion,
    OptimizedSection,
    JobTargetedOptimization,
)
from app.ai.llm.client import default_llm_client, LLMClientError

logger = logging.getLogger(__name__)


class ResumeOptimizerError(Exception):
    """简历优化异常"""
    pass


class ResumeOptimizer:
    """简历优化器"""

    def __init__(self):
        self.llm_client = default_llm_client

    async def optimize_resume(
        self,
        structured_data: ResumeStructuredData,
        score: ResumeScore,
        resume_text: str,
        job_title: Optional[str] = None,
        job_description: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> ResumeOptimization:
        """
        生成简历优化建议和文案

        Args:
            structured_data: 结构化简历数据
            score: 简历评分结果
            resume_text: 原始简历文本
            job_title: 目标岗位
            job_description: 岗位描述
            focus_areas: 重点关注领域

        Returns:
            优化建议和文案
        """
        try:
            # 1. 生成通用优化建议
            general_suggestions = await self._generate_general_suggestions(
                structured_data, score, focus_areas
            )

            # 2. 如果提供了岗位信息，生成面向岗位的优化
            job_targeted = None
            if job_title or job_description:
                job_targeted = await self._generate_job_targeted_optimization(
                    structured_data, score, resume_text, job_title, job_description
                )

            # 3. 生成优先行动清单
            priority_actions = self._generate_priority_actions(
                general_suggestions, job_targeted
            )

            # 4. 预估改进效果
            estimated_improvement = self._estimate_improvement(
                score, general_suggestions, job_targeted
            )

            # 5. 生成优化总结
            overall_summary = self._generate_overall_summary(
                general_suggestions, job_targeted, estimated_improvement
            )

            return ResumeOptimization(
                general_suggestions=general_suggestions,
                job_targeted=job_targeted,
                priority_actions=priority_actions,
                estimated_improvement=estimated_improvement,
                overall_summary=overall_summary
            )

        except Exception as e:
            raise ResumeOptimizerError(f"优化失败: {str(e)}")

    async def _generate_general_suggestions(
        self,
        data: ResumeStructuredData,
        score: ResumeScore,
        focus_areas: Optional[List[str]]
    ) -> List[OptimizationSuggestion]:
        """生成通用优化建议（优先使用LLM）"""
        suggestions = []

        # 策略：优先调用LLM生成所有维度的建议，不设评分阈值

        # 1. 完整性建议（完整性主要是缺失字段，用硬编码更合适）
        logger.warning(f"[SUGGEST] 完整性评分: {score.completeness.total_score}")
        if score.completeness.missing_fields:
            suggestions.extend(self._generate_completeness_suggestions(data, score.completeness))

        # 2. 专业性建议（始终调用LLM）
        logger.warning(f"[SUGGEST] 专业性评分: {score.professionalism.total_score}")
        logger.warning(f"[SUGGEST] 调用LLM生成专业性建议")
        prof_suggestions = await self._generate_professionalism_suggestions(data, score.professionalism)
        suggestions.extend(prof_suggestions)

        # 3. 量化建议（始终调用LLM）
        logger.warning(f"[SUGGEST] 量化评分: {score.quantification.total_score}")
        logger.warning(f"[SUGGEST] 调用LLM生成量化建议")
        quant_suggestions = await self._generate_quantification_suggestions(data, score.quantification)
        suggestions.extend(quant_suggestions)

        # 4. 项目深度建议（始终调用LLM）
        logger.warning(f"[SUGGEST] 项目深度评分: {score.project_depth.total_score}")
        logger.warning(f"[SUGGEST] 调用LLM生成项目深度建议")
        proj_suggestions = await self._generate_project_suggestions(data, score.project_depth)
        suggestions.extend(proj_suggestions)

        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        suggestions.sort(key=lambda x: priority_order.get(x.priority, 3))

        return suggestions[:10]  # 最多返回10条建议

    def _generate_completeness_suggestions(
        self,
        data: ResumeStructuredData,
        completeness_score
    ) -> List[OptimizationSuggestion]:
        """生成完整性建议"""
        suggestions = []

        for field in completeness_score.missing_fields:
            if field == "基本信息":
                suggestions.append(OptimizationSuggestion(
                    category="基本信息",
                    priority="高",
                    title="补充基本信息",
                    description="简历缺少基本信息模块",
                    current_content="无",
                    suggested_content="添加姓名、电话、邮箱、求职意向等基本信息",
                    reason="基本信息是简历的必备内容，HR首先会查看这些信息",
                    examples=["姓名：张三", "电话：138****1234", "邮箱：example@email.com"]
                ))
            elif field in ["姓名", "电话", "邮箱"]:
                suggestions.append(OptimizationSuggestion(
                    category="基本信息",
                    priority="高",
                    title=f"补充{field}",
                    description=f"基本信息中缺少{field}",
                    current_content="无",
                    suggested_content=f"添加{field}信息",
                    reason=f"{field}是HR联系候选人的重要途径",
                    examples=[]
                ))
            elif field == "教育经历":
                suggestions.append(OptimizationSuggestion(
                    category="教育经历",
                    priority="高",
                    title="添加教育经历",
                    description="简历中缺少教育背景信息",
                    current_content="无",
                    suggested_content="添加学校、专业、学历、在校时间等信息",
                    reason="教育背景是招聘的重要筛选条件",
                    examples=["四川大学 | 计算机科学与技术 | 本科 | 2020.09-2024.06"]
                ))
            elif field == "工作经历":
                suggestions.append(OptimizationSuggestion(
                    category="工作经历",
                    priority="中",
                    title="添加工作/实习经历",
                    description="简历中缺少工作或实习经验",
                    current_content="无",
                    suggested_content="添加公司名称、职位、工作时间和工作内容",
                    reason="工作经验能体现实际能力和职业发展",
                    examples=["某某公司 | Python开发实习生 | 2023.06-2023.09"]
                ))
            elif field == "项目经验":
                suggestions.append(OptimizationSuggestion(
                    category="项目经验",
                    priority="中",
                    title="添加项目经验",
                    description="简历中缺少项目经历",
                    current_content="无",
                    suggested_content="添加项目名称、角色、技术栈和项目成果",
                    reason="项目经验能展示技术能力和解决问题的能力",
                    examples=["电商系统后端开发 | 后端开发 | Python、FastAPI、PostgreSQL"]
                ))
            elif field == "技能标签":
                suggestions.append(OptimizationSuggestion(
                    category="技能标签",
                    priority="中",
                    title="添加技能标签",
                    description="简历中缺少技能清单",
                    current_content="无",
                    suggested_content="列出掌握的编程语言、框架、工具等技能",
                    reason="技能标签便于快速匹配岗位要求",
                    examples=["编程语言：Python、Java", "框架：FastAPI、Spring Boot", "数据库：MySQL、Redis"]
                ))

        return suggestions

    async def _generate_professionalism_suggestions(
        self,
        data: ResumeStructuredData,
        professionalism_score
    ) -> List[OptimizationSuggestion]:
        """生成专业性建议（使用LLM）"""
        suggestions = []

        # 构建prompt
        system_prompt = """你是一位专业的简历顾问。请分析简历的专业性问题，给出具体的优化建议。
重点关注：
1. 语言表达是否规范、简洁
2. 时间格式是否统一
3. 描述是否详细充分

**重要**：如果要指出具体问题，current_content 应该从用户简历中**真实提取**原文，不要编造示例。如果无法获取真实内容，将 current_content 设为 null。

请以JSON格式返回建议列表，每条建议包含：
- title: 建议标题
- description: 问题描述
- current_content: 当前内容示例（从简历真实提取，或设为 null）
- suggested_content: 建议修改后的内容
- reason: 修改原因
"""

        user_prompt = f"""简历专业性评分：{professionalism_score.total_score}
语言质量：{professionalism_score.language_quality}
格式一致性：{professionalism_score.format_consistency}
细节丰富度：{professionalism_score.detail_richness}

工作经历数量：{len(data.work_experience)}
项目经验数量：{len(data.project_experience)}

简历实际内容示例：
工作经历：{json.dumps([{"company": exp.company, "position": exp.position, "time": f"{exp.start_date} - {exp.end_date}", "achievements": exp.achievements[:2] if exp.achievements else []} for exp in data.work_experience[:2]], ensure_ascii=False)}

项目经验：{json.dumps([{"name": proj.name, "time": f"{proj.start_date} - {proj.end_date}", "achievements": proj.achievements[:2] if proj.achievements else []} for proj in data.project_experience[:2]], ensure_ascii=False)}

请给出2-3条最重要的专业性改进建议，current_content 必须从上述实际内容中提取。"""

        try:
            logger.warning(f"[LLM] 调用大模型生成专业性建议...")
            result = await self.llm_client.generate_text(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            logger.warning(f"[LLM] 大模型调用完成，返回长度: {len(result) if result else 0}")

            # 尝试解析JSON
            try:
                llm_suggestions = json.loads(result)
                if isinstance(llm_suggestions, list):
                    for item in llm_suggestions[:3]:
                        suggestions.append(OptimizationSuggestion(
                            category="专业性",
                            priority="中",
                            title=item.get("title", "提升专业性"),
                            description=item.get("description", ""),
                            current_content=item.get("current_content"),
                            suggested_content=item.get("suggested_content", ""),
                            reason=item.get("reason", ""),
                            examples=[]
                        ))
            except json.JSONDecodeError:
                # 如果不是JSON，使用通用建议
                pass

        except LLMClientError:
            pass

        # 如果LLM失败或没有建议，使用规则建议
        if not suggestions:
            if professionalism_score.format_consistency < 85:
                suggestions.append(OptimizationSuggestion(
                    category="专业性",
                    priority="中",
                    title="统一时间格式",
                    description="简历中的日期格式不统一，影响专业性",
                    current_content="有的用2023-06，有的用2023.06",
                    suggested_content="统一使用 YYYY-MM 格式，如 2023-06",
                    reason="统一的格式让简历看起来更规范专业",
                    examples=["2023-06", "2024-01"]
                ))

            if professionalism_score.detail_richness < 70:
                suggestions.append(OptimizationSuggestion(
                    category="专业性",
                    priority="中",
                    title="丰富描述内容",
                    description="工作和项目描述过于简单，缺少细节",
                    current_content="负责后端开发",
                    suggested_content="负责用户模块后端开发，使用Python+FastAPI实现RESTful API，日均处理10万次请求",
                    reason="详细的描述能更好地展示你的工作内容和价值",
                    examples=[]
                ))

        return suggestions

    async def _generate_quantification_suggestions(
        self,
        data: ResumeStructuredData,
        quantification_score
    ) -> List[OptimizationSuggestion]:
        """生成量化建议（使用LLM）"""
        suggestions = []

        # 构建prompt
        system_prompt = """你是一位专业的简历顾问。请分析简历中缺乏量化数据的描述，给出具体的量化优化建议。

重点关注：
1. 识别可以量化但未量化的成果描述
2. 给出具体的量化改写建议
3. 提供真实可信的量化示例

**重要**：current_content 必须从用户提供的"简历中缺乏量化的描述示例"中**原文摘录**，不要自己编造内容。

请以JSON格式返回建议列表，每条建议包含：
- title: 建议标题
- description: 问题描述
- current_content: 当前非量化的描述（必须从提供的示例中原文摘录）
- suggested_content: 量化后的描述建议
- reason: 为什么要量化
"""

        # 收集非量化的成果描述
        non_quantified_examples = []
        for exp in data.work_experience:
            for achievement in exp.achievements or []:
                if not self._is_quantified(achievement):
                    non_quantified_examples.append(f"工作成果: {achievement}")
                    if len(non_quantified_examples) >= 3:
                        break

        for proj in data.project_experience:
            for achievement in proj.achievements or []:
                if not self._is_quantified(achievement):
                    non_quantified_examples.append(f"项目成果: {achievement}")
                    if len(non_quantified_examples) >= 3:
                        break

        examples_text = "\n".join(non_quantified_examples[:5]) if non_quantified_examples else "暂无具体示例"

        user_prompt = f"""简历量化评分：{quantification_score.total_score}
量化率：{quantification_score.quantification_rate:.0%}

简历中缺乏量化的描述示例：
{examples_text}

请给出2-3条最重要的量化改进建议，帮助将这些描述改写为包含具体数据的版本。"""

        try:
            logger.warning(f"[LLM] 调用大模型生成量化建议...")
            result = await self.llm_client.generate_text(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            logger.warning(f"[LLM] 大模型调用完成，返回长度: {len(result) if result else 0}")

            # 尝试解析JSON
            try:
                llm_suggestions = json.loads(result)
                if isinstance(llm_suggestions, list):
                    for item in llm_suggestions[:3]:
                        suggestions.append(OptimizationSuggestion(
                            category="量化程度",
                            priority="高" if quantification_score.total_score < 40 else "中",
                            title=item.get("title", "增加量化数据"),
                            description=item.get("description", ""),
                            current_content=item.get("current_content"),
                            suggested_content=item.get("suggested_content", ""),
                            reason=item.get("reason", ""),
                            examples=[]
                        ))
            except json.JSONDecodeError:
                logger.warning("[LLM] JSON解析失败，使用硬编码兜底")
                pass

        except Exception as e:
            logger.warning(f"[LLM] 调用失败: {e}，使用硬编码兜底")
            pass

        # 如果LLM失败或没有建议，使用硬编码兜底
        if not suggestions:
            if quantification_score.total_score < 70:
                priority = "高" if quantification_score.total_score < 40 else "中"
                current_example = non_quantified_examples[0] if non_quantified_examples else "提升了系统性能"
                suggestions.append(OptimizationSuggestion(
                    category="量化程度",
                    priority=priority,
                    title="增加量化数据",
                    description=f"当前量化率仅{quantification_score.quantification_rate:.0%}，大部分成果描述缺少具体数据",
                    current_content=current_example,
                    suggested_content=f"{current_example}，响应时间降低40%，从500ms优化到300ms",
                    reason="量化的成果更有说服力，能直观展示你的贡献",
                    examples=[
                        "优化数据库查询，查询速度提升60%",
                        "负责3个核心模块开发，代码量约8000行",
                        "支持日均10万用户访问，系统稳定性99.9%"
                    ]
                ))

        return suggestions

    async def _generate_project_suggestions(
        self,
        data: ResumeStructuredData,
        project_score
    ) -> List[OptimizationSuggestion]:
        """生成项目深度建议（使用LLM）"""
        suggestions = []

        # 构建prompt
        system_prompt = """你是一位专业的简历顾问。请分析简历中的项目经验，给出具体的优化建议。

重点关注：
1. 项目描述的深度和完整性
2. 技术栈的详细程度
3. 项目成果的具体性和量化
4. 个人职责和贡献的清晰度

**重要**：current_content 必须从用户提供的"当前项目信息"中**真实提取**，不要编造内容。

请以JSON格式返回建议列表，每条建议包含：
- title: 建议标题
- description: 问题描述
- current_content: 当前的项目描述示例（从提供的实际项目中提取）
- suggested_content: 优化后的描述
- reason: 优化理由
"""

        # 构建项目信息
        projects_info = []
        for proj in data.project_experience:
            tech_stack = " + ".join(proj.tech_stack) if proj.tech_stack else "未指定"
            achievements_text = "; ".join(proj.achievements[:2]) if proj.achievements else "无"
            projects_info.append(f"项目：{proj.name or '未命名'} | 技术栈：{tech_stack} | 成果：{achievements_text}")

        projects_text = "\n".join(projects_info) if projects_info else "暂无项目经验"

        user_prompt = f"""简历项目深度评分：{project_score.total_score}
项目数量：{project_score.project_count}
平均技术栈数量：{project_score.avg_tech_stack_count:.1f}
平均成果数量：{project_score.avg_achievement_count:.1f}

当前项目信息：
{projects_text}

请给出2-3条最重要的项目优化建议，帮助提升项目描述的深度和专业性。"""

        try:
            logger.warning(f"[LLM] 调用大模型生成项目建议...")
            result = await self.llm_client.generate_text(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            logger.warning(f"[LLM] 大模型调用完成，返回长度: {len(result) if result else 0}")

            # 尝试解析JSON
            try:
                llm_suggestions = json.loads(result)
                if isinstance(llm_suggestions, list):
                    for item in llm_suggestions[:3]:
                        suggestions.append(OptimizationSuggestion(
                            category="项目经验",
                            priority="中",
                            title=item.get("title", "优化项目描述"),
                            description=item.get("description", ""),
                            current_content=item.get("current_content"),
                            suggested_content=item.get("suggested_content", ""),
                            reason=item.get("reason", ""),
                            examples=[]
                        ))
            except json.JSONDecodeError:
                logger.warning("[LLM] JSON解析失败，使用硬编码兜底")
                pass

        except Exception as e:
            logger.warning(f"[LLM] 调用失败: {e}，使用硬编码兜底")
            pass

        # 如果LLM失败或没有建议，使用硬编码兜底
        if not suggestions:
            if project_score.project_count == 0:
                suggestions.append(OptimizationSuggestion(
                    category="项目经验",
                    priority="高",
                    title="添加项目经验",
                    description="简历中完全缺少项目经历",
                    current_content="无",
                    suggested_content="添加至少2-3个有代表性的项目，包括项目背景、职责、技术栈和成果",
                    reason="项目经验是技术能力的重要体现",
                    examples=["电商后台管理系统", "智能推荐引擎", "数据分析平台"]
                ))
            elif project_score.avg_tech_stack_count < 3:
                suggestions.append(OptimizationSuggestion(
                    category="项目经验",
                    priority="中",
                    title="补充技术栈信息",
                    description=f"项目的技术栈描述不够详细，平均仅{project_score.avg_tech_stack_count:.1f}项",
                    current_content="使用Python开发",
                    suggested_content="使用Python + FastAPI + PostgreSQL + Redis + Docker，前端使用React + TypeScript",
                    reason="详细的技术栈能展示技术能力和项目复杂度",
                    examples=[]
                ))

        return suggestions

    async def _generate_job_targeted_optimization(
        self,
        data: ResumeStructuredData,
        score: ResumeScore,
        resume_text: str,
        job_title: Optional[str],
        job_description: Optional[str]
    ) -> JobTargetedOptimization:
        """生成面向岗位的优化文案"""
        # 构建LLM prompt
        system_prompt = """你是一位专业的简历优化顾问，擅长针对特定岗位优化简历内容。

你的任务是：
1. 分析岗位要求和简历内容的匹配度
2. 识别简历中与岗位相关的优势
3. 找出需要改进的方面
4. 为关键章节生成优化后的文案

优化原则：
- 突出与岗位相关的经验和技能
- 使用岗位描述中的关键词
- 量化成果，体现价值
- 保持真实，不夸大不捏造
"""

        # 构建简历摘要
        resume_summary = self._build_resume_summary(data)

        user_prompt = f"""目标岗位：{job_title or '未指定'}
岗位描述：{job_description or '未提供'}

候选人简历摘要：
{resume_summary}

当前匹配度：{score.job_match.total_score if score.job_match else 60.0}

请以JSON格式返回：
{{
    "key_requirements": ["岗位关键要求1", "要求2"],
    "matched_points": ["已匹配优势1", "优势2"],
    "improvement_areas": ["需要改进1", "改进2"],
    "optimized_sections": [
        {{
            "section": "工作经历",
            "original": "原始内容示例",
            "optimized": "优化后内容",
            "improvements": ["改进点1", "改进点2"]
        }}
    ],
    "additional_suggestions": ["额外建议1", "建议2"]
}}
"""

        try:
            result = await self.llm_client.generate_text(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )

            # 解析LLM返回
            llm_result = json.loads(result)

            # LLM 可能返回合法 JSON 但不是对象（如列表/字符串），此时回退到基础版本
            if not isinstance(llm_result, dict):
                return self._generate_basic_job_targeted(data, score, job_title)

            # 构建OptimizedSection对象
            optimized_sections = []
            _sections = llm_result.get("optimized_sections") or []
            if not isinstance(_sections, list):
                _sections = []
            for section_data in _sections:
                if not isinstance(section_data, dict):
                    continue
                optimized_sections.append(OptimizedSection(
                    section=section_data.get("section", ""),
                    original=section_data.get("original", ""),
                    optimized=section_data.get("optimized", ""),
                    improvements=section_data.get("improvements", [])
                ))

            return JobTargetedOptimization(
                job_title=job_title or "未指定",
                match_score=score.job_match.total_score if score.job_match else 60.0,
                key_requirements=llm_result.get("key_requirements", []),
                matched_points=llm_result.get("matched_points", []),
                improvement_areas=llm_result.get("improvement_areas", []),
                optimized_sections=optimized_sections,
                additional_suggestions=llm_result.get("additional_suggestions", [])
            )

        except (json.JSONDecodeError, LLMClientError) as e:
            # LLM失败时返回基础版本
            return self._generate_basic_job_targeted(data, score, job_title)

    def _generate_basic_job_targeted(
        self,
        data: ResumeStructuredData,
        score: ResumeScore,
        job_title: Optional[str]
    ) -> JobTargetedOptimization:
        """生成基础的岗位优化（LLM失败时使用）"""
        matched_points = []
        improvement_areas = []

        if score.job_match:
            matched_points = [f"掌握 {skill}" for skill in score.job_match.matched_skills[:3]]
            improvement_areas = [f"建议学习 {skill}" for skill in score.job_match.missing_skills[:3]]

        return JobTargetedOptimization(
            job_title=job_title or "未指定",
            match_score=score.job_match.total_score if score.job_match else 60.0,
            key_requirements=["相关技能", "项目经验", "学习能力"],
            matched_points=matched_points or ["具备相关技术背景"],
            improvement_areas=improvement_areas or ["提升项目经验"],
            optimized_sections=[],
            additional_suggestions=["根据岗位要求调整简历重点", "突出相关项目经验"]
        )

    def _build_resume_summary(self, data: ResumeStructuredData) -> str:
        """构建简历摘要"""
        summary_parts = []

        if data.basic_info:
            summary_parts.append(f"基本信息：{data.basic_info.name or '未知'}")

        if data.education:
            edu = data.education[0]
            summary_parts.append(f"教育：{edu.school} {edu.degree} {edu.major}")

        if data.work_experience:
            summary_parts.append(f"工作经历：{len(data.work_experience)}段")
            for exp in data.work_experience[:2]:
                summary_parts.append(f"  - {exp.company} | {exp.position}")

        if data.project_experience:
            summary_parts.append(f"项目经验：{len(data.project_experience)}个")
            for proj in data.project_experience[:2]:
                summary_parts.append(f"  - {proj.name}")

        if data.skills:
            skills_by_cat = {}
            for skill in data.skills:
                cat = skill.category or "其他"
                if cat not in skills_by_cat:
                    skills_by_cat[cat] = []
                skills_by_cat[cat].append(skill.name)

            summary_parts.append("技能：")
            for cat, skills in list(skills_by_cat.items())[:3]:
                summary_parts.append(f"  - {cat}: {', '.join(skills[:5])}")

        return "\n".join(summary_parts)

    def _generate_priority_actions(
        self,
        general_suggestions: List[OptimizationSuggestion],
        job_targeted: Optional[JobTargetedOptimization]
    ) -> List[str]:
        """生成优先行动清单"""
        actions = []

        # 从通用建议中提取高优先级
        for suggestion in general_suggestions:
            if suggestion.priority == "高":
                actions.append(f"{suggestion.title}：{suggestion.suggested_content}")

        # 从岗位优化中提取
        if job_targeted:
            for area in job_targeted.improvement_areas[:2]:
                actions.append(f"岗位匹配：{area}")

        # 限制在5条以内
        return actions[:5]

    def _estimate_improvement(
        self,
        current_score: ResumeScore,
        general_suggestions: List[OptimizationSuggestion],
        job_targeted: Optional[JobTargetedOptimization]
    ) -> Dict[str, float]:
        """预估改进效果"""
        improvement = {}

        # 根据建议类别预估提升
        category_impact = {
            "基本信息": ("completeness", 10),
            "教育经历": ("completeness", 15),
            "工作经历": ("completeness", 15),
            "项目经验": ("project_depth", 20),
            "技能标签": ("completeness", 10),
            "专业性": ("professionalism", 15),
            "量化程度": ("quantification", 25),
        }

        for suggestion in general_suggestions:
            if suggestion.priority == "高":
                if suggestion.category in category_impact:
                    dimension, impact = category_impact[suggestion.category]
                    improvement[dimension] = improvement.get(dimension, 0) + impact

        # 岗位匹配提升
        if job_targeted and len(job_targeted.improvement_areas) > 0:
            improvement["job_match"] = 10 + len(job_targeted.improvement_areas) * 5

        # 限制提升幅度
        for key in improvement:
            improvement[key] = min(improvement[key], 30)

        return improvement

    def _generate_overall_summary(
        self,
        general_suggestions: List[OptimizationSuggestion],
        job_targeted: Optional[JobTargetedOptimization],
        estimated_improvement: Dict[str, float]
    ) -> str:
        """生成优化总结"""
        summary_parts = []

        # 建议总数
        total_suggestions = len(general_suggestions)
        high_priority = sum(1 for s in general_suggestions if s.priority == "高")

        summary_parts.append(f"共生成{total_suggestions}条优化建议，其中高优先级{high_priority}条。")

        # 主要改进方向
        if general_suggestions:
            main_areas = list(set(s.category for s in general_suggestions[:3]))
            summary_parts.append(f"主要改进方向：{' '.join(main_areas)}。")

        # 岗位优化
        if job_targeted:
            summary_parts.append(f"针对'{job_targeted.job_title}'岗位提供了{len(job_targeted.optimized_sections)}处定向优化。")

        # 预估提升
        if estimated_improvement:
            total_improvement = sum(estimated_improvement.values()) / len(estimated_improvement)
            summary_parts.append(f"预计优化后各维度平均提升{total_improvement:.0f}分。")

        return "".join(summary_parts)

    def _is_quantified(self, text: str) -> bool:
        """判断文本是否包含量化信息"""
        import re
        patterns = [
            r'\d+',  r'\d+%',  r'\d+人',  r'\d+万',
            r'\d+个',  r'\d+倍',  r'提升\d+',
            r'降低\d+',  r'增长\d+',
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False


# 全局实例
resume_optimizer = ResumeOptimizer()
