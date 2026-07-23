"""
岗位分析服务 - 提供岗位详细解读

功能：
1. 解析岗位信息（职责、技能、要求）
2. 市场数据对比（薪资竞争力、技能热度）
3. 职业发展路径建议
4. 适合人群画像
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class JobAnalysisService:
    """岗位分析服务"""

    async def analyze_job(self, job_id: int, job_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析岗位详情

        返回：
        {
            "job_id": 123,
            "job_title": "Python后端开发工程师",
            "company": "字节跳动",
            "core_info": {
                "responsibilities": ["开发后端服务", "优化系统性能"],
                "required_skills": ["Python", "Django", "MySQL"],
                "bonus_skills": ["Docker", "K8s"],
                "requirements": ["本科及以上", "3-5年经验"]
            },
            "market_analysis": {
                "salary_competitiveness": "高于市场平均30%",
                "skill_hotness": {
                    "Python": "热门(85%)",
                    "Django": "中等(45%)"
                }
            },
            "career_path": [
                {"stage": "初级开发", "duration": "0-2年"},
                {"stage": "中级开发", "duration": "2-5年"},
                {"stage": "高级开发/架构师", "duration": "5年+"}
            ],
            "suitable_candidates": {
                "education": "本科及以上",
                "experience": "3-5年Python开发经验",
                "skills": ["Python", "Web框架", "数据库"],
                "personality": "逻辑思维强、注重细节"
            }
        }
        """
        # 1. 加载岗位数据
        if job_data is None:
            job_data = await self._load_job_data(job_id)

        # 2. 提取核心信息
        core_info = self._extract_core_info(job_data)

        # 3. 市场分析
        market_analysis = await self._analyze_market(job_data, core_info)

        # 4. 职业发展路径
        career_path = self._generate_career_path(job_data.get("title", ""))

        # 5. 适合人群画像
        suitable_candidates = self._generate_candidate_profile(job_data, core_info)

        # 6. 岗位难度评估
        difficulty_assessment = self._assess_job_difficulty(job_data, core_info)

        return {
            "job_id": job_id,
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "salary_range": job_data.get("salary_range", ""),
            "core_info": core_info,
            "market_analysis": market_analysis,
            "career_path": career_path,
            "suitable_candidates": suitable_candidates,
            "difficulty_assessment": difficulty_assessment,
        }

    def _extract_core_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取岗位核心信息"""
        description = job_data.get("description", "")
        requirements = job_data.get("requirements", "")

        # 提取职责（岗位描述中的关键点）
        responsibilities = self._extract_responsibilities(description)

        # 提取技能要求
        skills = job_data.get("skills", []) or []
        required_skills = skills[:int(len(skills) * 0.7)] if skills else []
        bonus_skills = skills[int(len(skills) * 0.7):] if skills else []

        # 提取其他要求
        other_requirements = self._extract_requirements(requirements)

        return {
            "responsibilities": responsibilities,
            "required_skills": required_skills,
            "bonus_skills": bonus_skills,
            "requirements": other_requirements,
        }

    def _extract_responsibilities(self, description: str) -> List[str]:
        """从描述中提取职责要点"""
        if not description:
            return []

        # 按换行或句号分割
        lines = re.split(r'[；;。\n]', description)

        # 过滤出有效的职责描述（长度在10-100字符）
        responsibilities = []
        for line in lines:
            line = line.strip()
            if 10 <= len(line) <= 100:
                # 去除数字序号
                line = re.sub(r'^\d+[\.\、]\s*', '', line)
                responsibilities.append(line)

        return responsibilities[:5]  # 最多返回5条

    def _extract_requirements(self, requirements: str) -> List[str]:
        """提取其他要求（学历、经验等）"""
        if not requirements:
            return []

        req_list = []

        # 学历
        if any(edu in requirements for edu in ["本科", "硕士", "博士", "大专"]):
            for edu in ["博士", "硕士", "本科", "大专"]:
                if edu in requirements:
                    req_list.append(f"学历：{edu}及以上")
                    break

        # 工作年限
        exp_match = re.search(r'(\d+[-~]\d+年|\d+年以上|应届)', requirements)
        if exp_match:
            req_list.append(f"经验：{exp_match.group()}")

        return req_list

    async def _analyze_market(
        self,
        job_data: Dict[str, Any],
        core_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """市场分析"""
        # 薪资竞争力分析
        salary_competitiveness = self._analyze_salary_competitiveness(
            job_data.get("salary_range", ""),
            job_data.get("location", "")
        )

        # 技能热度分析
        skill_hotness = {}
        for skill in core_info["required_skills"][:5]:  # 只分析前5个技能
            hotness = self._get_skill_hotness(skill)
            skill_hotness[skill] = hotness

        return {
            "salary_competitiveness": salary_competitiveness,
            "skill_hotness": skill_hotness,
        }

    def _analyze_salary_competitiveness(self, salary_range: str, location: str) -> str:
        """分析薪资竞争力"""
        # 简化实现：从薪资范围提取平均值
        numbers = re.findall(r'(\d+)', salary_range)
        if len(numbers) >= 2:
            avg = (int(numbers[0]) + int(numbers[1])) / 2

            # 根据平均薪资判断竞争力
            if avg >= 30:
                return "高于市场平均30%以上"
            elif avg >= 20:
                return "略高于市场平均"
            elif avg >= 15:
                return "市场平均水平"
            else:
                return "略低于市场平均"

        return "薪资信息不足"

    def _get_skill_hotness(self, skill: str) -> str:
        """获取技能热度"""
        # 简化实现：根据常见技能判断
        hot_skills = ["Python", "Java", "JavaScript", "Go", "React", "Vue", "MySQL", "Redis"]
        warm_skills = ["Django", "Flask", "Spring", "Docker", "K8s", "MongoDB"]

        skill_lower = skill.lower()
        if any(s.lower() in skill_lower for s in hot_skills):
            return "热门(70%+岗位需求)"
        elif any(s.lower() in skill_lower for s in warm_skills):
            return "中等(30-70%岗位需求)"
        else:
            return "小众(30%以下岗位需求)"

    def _generate_career_path(self, job_title: str) -> List[Dict[str, str]]:
        """生成职业发展路径"""
        # 根据岗位标题判断职级
        if "初级" in job_title or "Junior" in job_title:
            return [
                {"stage": "初级开发工程师", "duration": "当前", "focus": "掌握基础技能，完成功能开发"},
                {"stage": "中级开发工程师", "duration": "1-2年后", "focus": "独立负责模块，优化性能"},
                {"stage": "高级开发工程师", "duration": "3-5年后", "focus": "技术攻关，架构设计"},
                {"stage": "技术专家/架构师", "duration": "5年+", "focus": "技术规划，团队建设"},
            ]
        elif "中级" in job_title:
            return [
                {"stage": "中级开发工程师", "duration": "当前", "focus": "独立负责模块，优化性能"},
                {"stage": "高级开发工程师", "duration": "2-3年后", "focus": "技术攻关，架构设计"},
                {"stage": "技术专家/架构师", "duration": "3-5年后", "focus": "技术规划，团队建设"},
                {"stage": "技术总监", "duration": "5年+", "focus": "战略规划，组织管理"},
            ]
        elif "高级" in job_title or "Senior" in job_title:
            return [
                {"stage": "高级开发工程师", "duration": "当前", "focus": "技术攻关，架构设计"},
                {"stage": "技术专家/架构师", "duration": "1-2年后", "focus": "技术规划，团队建设"},
                {"stage": "技术总监", "duration": "3-5年后", "focus": "战略规划，组织管理"},
            ]
        else:
            # 默认路径
            return [
                {"stage": "开发工程师", "duration": "当前", "focus": "技术深耕"},
                {"stage": "资深工程师", "duration": "2-3年后", "focus": "技术专家"},
                {"stage": "技术管理/架构师", "duration": "5年+", "focus": "技术规划或团队管理"},
            ]

    def _generate_candidate_profile(
        self,
        job_data: Dict[str, Any],
        core_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成适合人群画像"""
        requirements = job_data.get("requirements", "")

        # 学历要求
        education = "本科及以上"
        for edu in ["博士", "硕士", "本科", "大专"]:
            if edu in requirements:
                education = f"{edu}及以上"
                break

        # 经验要求
        experience = "不限"
        exp_match = re.search(r'(\d+[-~]\d+年|\d+年以上|应届)', requirements)
        if exp_match:
            experience = exp_match.group()

        # 核心技能
        skills = core_info["required_skills"][:5]

        # 性格特质（根据岗位类型推断）
        job_title = job_data.get("title", "").lower()
        if "算法" in job_title or "ai" in job_title:
            personality = "数学功底扎实、逻辑思维强、喜欢钻研"
        elif "前端" in job_title or "frontend" in job_title:
            personality = "审美能力强、注重细节、用户体验意识"
        elif "测试" in job_title or "qa" in job_title:
            personality = "细心谨慎、责任心强、善于沟通"
        else:
            personality = "逻辑思维强、学习能力强、团队协作"

        return {
            "education": education,
            "experience": experience,
            "skills": skills,
            "personality": personality,
        }

    def _assess_job_difficulty(
        self,
        job_data: Dict[str, Any],
        core_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估岗位难度

        评估维度：
        1. 技能要求复杂度
        2. 经验要求
        3. 学历要求
        4. 薪资水平（高薪资通常对应高难度）
        5. 公司规模和知名度

        返回：
        {
            "overall_difficulty": "中等",  # 简单/中等/困难/很困难
            "difficulty_score": 65,  # 0-100分
            "factors": {
                "skill_complexity": {"score": 70, "description": "需要掌握5+种技术栈"},
                "experience_requirement": {"score": 60, "description": "要求3-5年经验"},
                "education_requirement": {"score": 50, "description": "本科及以上"},
                "salary_level": {"score": 80, "description": "薪资高于市场平均"},
                "company_prestige": {"score": 70, "description": "知名大厂"}
            },
            "competitive_pressure": "较高",
            "preparation_time": "建议准备1-2个月"
        }
        """
        scores = {}

        # 1. 技能要求复杂度 (0-100)
        required_skills = core_info.get("required_skills", [])
        skill_count = len(required_skills)
        if skill_count >= 7:
            skill_score = 90
            skill_desc = f"需要掌握{skill_count}种技术栈，技术要求高"
        elif skill_count >= 5:
            skill_score = 70
            skill_desc = f"需要掌握{skill_count}种技术栈，技术要求较高"
        elif skill_count >= 3:
            skill_score = 50
            skill_desc = f"需要掌握{skill_count}种技术栈，技术要求适中"
        else:
            skill_score = 30
            skill_desc = f"需要掌握{skill_count}种技术栈，技术要求较低"

        scores["skill_complexity"] = {"score": skill_score, "description": skill_desc}

        # 2. 经验要求 (0-100)
        requirements = job_data.get("requirements", "")
        if "10年" in requirements or "10+" in requirements:
            exp_score = 100
            exp_desc = "要求10年以上经验，门槛极高"
        elif "7年" in requirements or "7-" in requirements or "8年" in requirements:
            exp_score = 85
            exp_desc = "要求7年以上经验，门槛很高"
        elif "5年" in requirements or "5-" in requirements:
            exp_score = 70
            exp_desc = "要求5年以上经验，门槛较高"
        elif "3年" in requirements or "3-" in requirements:
            exp_score = 50
            exp_desc = "要求3年以上经验，门槛适中"
        elif "1年" in requirements or "1-" in requirements:
            exp_score = 30
            exp_desc = "要求1年以上经验，门槛较低"
        elif "应届" in requirements:
            exp_score = 10
            exp_desc = "接受应届生，门槛低"
        else:
            exp_score = 40
            exp_desc = "经验要求待定"

        scores["experience_requirement"] = {"score": exp_score, "description": exp_desc}

        # 3. 学历要求 (0-100)
        if "博士" in requirements:
            edu_score = 90
            edu_desc = "要求博士学历，门槛很高"
        elif "硕士" in requirements:
            edu_score = 70
            edu_desc = "要求硕士及以上学历，门槛较高"
        elif "本科" in requirements:
            edu_score = 50
            edu_desc = "要求本科及以上学历，门槛适中"
        elif "大专" in requirements:
            edu_score = 30
            edu_desc = "要求大专及以上学历，门槛较低"
        else:
            edu_score = 40
            edu_desc = "学历要求待定"

        scores["education_requirement"] = {"score": edu_score, "description": edu_desc}

        # 4. 薪资水平 (0-100) - 高薪资对应高难度
        salary_range = job_data.get("salary_range", "")
        numbers = re.findall(r'(\d+)', salary_range)
        if len(numbers) >= 2:
            avg_salary = (int(numbers[0]) + int(numbers[1])) / 2
            if avg_salary >= 40:
                salary_score = 90
                salary_desc = "薪资40K+，高薪高压"
            elif avg_salary >= 30:
                salary_score = 75
                salary_desc = "薪资30K+，待遇优厚"
            elif avg_salary >= 20:
                salary_score = 60
                salary_desc = "薪资20K+，待遇良好"
            elif avg_salary >= 15:
                salary_score = 45
                salary_desc = "薪资15K+，市场平均"
            else:
                salary_score = 30
                salary_desc = "薪资15K以下，待遇一般"
        else:
            salary_score = 40
            salary_desc = "薪资信息不足"

        scores["salary_level"] = {"score": salary_score, "description": salary_desc}

        # 5. 公司知名度 (0-100) - 简化评估
        company = job_data.get("company", "").lower()
        famous_companies = ["字节", "腾讯", "阿里", "华为", "百度", "京东", "美团", "拼多多",
                          "bytedance", "tencent", "alibaba", "huawei", "baidu"]
        if any(fc in company for fc in famous_companies):
            company_score = 85
            company_desc = "知名大厂，竞争激烈"
        else:
            company_score = 50
            company_desc = "一般企业，竞争适中"

        scores["company_prestige"] = {"score": company_score, "description": company_desc}

        # 计算总分（加权平均）
        weights = {
            "skill_complexity": 0.3,
            "experience_requirement": 0.25,
            "education_requirement": 0.15,
            "salary_level": 0.2,
            "company_prestige": 0.1,
        }

        overall_score = sum(
            scores[k]["score"] * weights[k]
            for k in weights.keys()
        )

        # 判断难度等级
        if overall_score >= 80:
            difficulty_level = "很困难"
            competitive_pressure = "极高"
            prep_time = "建议准备3-6个月"
        elif overall_score >= 65:
            difficulty_level = "困难"
            competitive_pressure = "较高"
            prep_time = "建议准备2-3个月"
        elif overall_score >= 50:
            difficulty_level = "中等"
            competitive_pressure = "中等"
            prep_time = "建议准备1-2个月"
        elif overall_score >= 35:
            difficulty_level = "较简单"
            competitive_pressure = "较低"
            prep_time = "建议准备2-4周"
        else:
            difficulty_level = "简单"
            competitive_pressure = "低"
            prep_time = "建议准备1-2周"

        return {
            "overall_difficulty": difficulty_level,
            "difficulty_score": int(overall_score),
            "factors": scores,
            "competitive_pressure": competitive_pressure,
            "preparation_time": prep_time,
        }

    async def _load_job_data(self, job_id: int) -> Dict[str, Any]:
        """加载岗位数据"""
        # TODO: 从数据库加载
        return {}


# 单例
job_analysis_service = JobAnalysisService()
