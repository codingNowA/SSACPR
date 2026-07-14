"""
岗位信息提取服务
"""
import re
from typing import List, Optional, Dict, Tuple
from app.schemas.job_extraction import ExtractedJobInfo, JobExtractionResponse


class JobInfoExtractor:
    """岗位信息提取器"""

    def __init__(self):
        # 学历关键词
        self.education_keywords = {
            "博士": "博士",
            "硕士": "硕士",
            "研究生": "硕士",
            "本科": "本科",
            "学士": "本科",
            "大专": "大专",
            "专科": "大专",
            "高中": "高中",
            "中专": "中专",
            "不限": "不限"
        }

        # 经验关键词模式
        self.experience_patterns = [
            r'(\d+[-~]\d+)\s*年',
            r'(\d+)\s*年以上',
            r'(\d+)\s*年以下',
            r'(\d+)\+\s*年',
            r'应届生',
            r'无经验',
            r'经验不限'
        ]

        # 薪资模式
        self.salary_patterns = [
            r'(\d+)[kK][-~](\d+)[kK]',
            r'(\d+)[-~](\d+)k',
            r'(\d+)千[-~](\d+)千',
            r'(\d+)万[-~](\d+)万',
            r'月薪[：:]\s*(\d+)[-~](\d+)',
            r'薪资[：:]\s*(\d+)[-~](\d+)'
        ]

        # 技能关键词（常见技术栈）
        self.skill_keywords = [
            # 编程语言
            "Java", "Python", "JavaScript", "C++", "Go", "Rust", "TypeScript",
            "PHP", "C#", "Ruby", "Swift", "Kotlin", "Scala",
            # 前端
            "React", "Vue", "Angular", "HTML", "CSS", "jQuery", "Node.js",
            "Webpack", "TypeScript", "Less", "Sass",
            # 后端框架
            "Spring", "Spring Boot", "Django", "Flask", "FastAPI", "Express",
            "Hibernate", "MyBatis",
            # 数据库
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server",
            "Elasticsearch", "HBase", "Cassandra",
            # 架构
            "微服务", "分布式", "高并发", "架构设计", "系统设计",
            # 中间件
            "Kafka", "RabbitMQ", "Nginx", "Tomcat", "Docker", "Kubernetes",
            # 其他
            "Git", "Linux", "RESTful", "GraphQL", "gRPC", "WebSocket",
            "机器学习", "深度学习", "数据分析", "算法", "NLP", "计算机视觉"
        ]

        # 行业关键词（顺序重要：更具体的行业放前面）
        self.industry_keywords = {
            "人工智能": ["人工智能", "AI", "机器学习", "深度学习", "算法工程", "NLP", "计算机视觉"],
            "计算机/软件": ["计算机相关", "计算机专业", "软件开发", "软件工程", "IT技术", "程序开发", "信息技术"],
            "互联网": ["互联网", "电商", "社交", "O2O"],
            "金融": ["金融", "银行", "证券", "保险", "支付"],
            "游戏": ["游戏", "手游", "端游"],
            "教育": ["教育", "培训", "在线教育"],
            "医疗": ["医疗", "健康", "医药"],
            "电商": ["电商", "零售", "新零售"]
        }

    def extract(self, job_text: str) -> JobExtractionResponse:
        """
        从岗位文本中提取关键信息

        Args:
            job_text: 岗位描述文本

        Returns:
            JobExtractionResponse: 提取结果
        """
        extracted_info = ExtractedJobInfo()
        extraction_notes = []
        missing_fields = []

        # 提取岗位名称
        job_title = self._extract_job_title(job_text)
        if job_title:
            extracted_info.job_title = job_title
            extraction_notes.append(f"成功提取岗位名称: {job_title}")
        else:
            missing_fields.append("岗位名称")

        # 提取学历要求
        education = self._extract_education(job_text)
        if education:
            extracted_info.education_requirement = education
            extraction_notes.append(f"成功提取学历要求: {education}")
        else:
            missing_fields.append("学历要求")

        # 提取工作经验
        experience = self._extract_experience(job_text)
        if experience:
            extracted_info.experience_requirement = experience
            extraction_notes.append(f"成功提取经验要求: {experience}")
        else:
            missing_fields.append("工作经验")

        # 提取薪资范围
        salary = self._extract_salary(job_text)
        if salary:
            extracted_info.salary_range = salary
            extraction_notes.append(f"成功提取薪资范围: {salary}")
        else:
            missing_fields.append("薪资范围")

        # 提取工作地点
        location = self._extract_location(job_text)
        if location:
            extracted_info.location = location
            extraction_notes.append(f"成功提取工作地点: {location}")
        else:
            missing_fields.append("工作地点")

        # 提取技能要求
        required_skills, preferred_skills = self._extract_skills(job_text)
        extracted_info.required_skills = required_skills
        extracted_info.preferred_skills = preferred_skills
        if required_skills:
            extraction_notes.append(f"成功提取{len(required_skills)}项必备技能")

        # 提取岗位职责
        responsibilities = self._extract_responsibilities(job_text)
        if responsibilities:
            extracted_info.job_responsibilities = responsibilities

        # 提取任职要求
        requirements = self._extract_requirements(job_text)
        if requirements:
            extracted_info.job_requirements = requirements

        # 提取福利待遇
        benefits = self._extract_benefits(job_text)
        if benefits:
            extracted_info.company_benefits = benefits
            extraction_notes.append("成功提取福利待遇信息")

        # 提取行业
        industry, industry_tags = self._extract_industry(job_text)
        if industry:
            extracted_info.industry = industry
            extracted_info.industry_tags = industry_tags
            if len(industry_tags) > 1:
                extraction_notes.append(f"识别行业: {' > '.join(industry_tags)}")
            else:
                extraction_notes.append(f"识别行业: {industry}")

        # 提取公司类型
        company_type = self._extract_company_type(job_text)
        if company_type:
            extracted_info.company_type = company_type

        # 提取团队规模
        team_size = self._extract_team_size(job_text)
        if team_size:
            extracted_info.team_size = team_size

        # 提取工作模式
        work_mode = self._extract_work_mode(job_text)
        if work_mode:
            extracted_info.work_mode = work_mode

        # 计算置信度
        confidence = self._calculate_confidence(extracted_info, missing_fields)

        return JobExtractionResponse(
            success=confidence > 0.3,
            extracted_info=extracted_info,
            confidence_score=confidence,
            extraction_notes=extraction_notes,
            missing_fields=missing_fields
        )

    def _extract_job_title(self, text: str) -> Optional[str]:
        """提取岗位名称"""
        lines = text.strip().split('\n')
        # 通常第一行是岗位名称
        first_line = lines[0].strip()
        if first_line and len(first_line) < 50:
            return first_line

        # 尝试匹配常见模式
        patterns = [
            r'岗位[：:]\s*(.+)',
            r'职位[：:]\s*(.+)',
            r'招聘[：:]\s*(.+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_education(self, text: str) -> Optional[str]:
        """提取学历要求"""
        for keyword, education in self.education_keywords.items():
            pattern = rf'{keyword}[及以上]*'
            if re.search(pattern, text):
                if "以上" in text or "及以上" in text:
                    return f"{education}及以上"
                return education
        return None

    def _extract_experience(self, text: str) -> Optional[str]:
        """提取工作经验要求"""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text)
            if match:
                if "应届" in match.group(0) or "无经验" in match.group(0) or "不限" in match.group(0):
                    return "应届生/无经验要求"
                return match.group(0)
        return None

    def _extract_salary(self, text: str) -> Optional[str]:
        """提取薪资范围"""
        for pattern in self.salary_patterns:
            match = re.search(pattern, text)
            if match:
                if 'k' in match.group(0).lower():
                    return f"{match.group(1)}k-{match.group(2)}k"
                elif '万' in match.group(0):
                    return f"{match.group(1)}万-{match.group(2)}万"
                elif '千' in match.group(0):
                    return f"{match.group(1)}k-{match.group(2)}k"
                else:
                    return f"{match.group(1)}-{match.group(2)}"
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """提取工作地点"""
        # 中国主要城市
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉",
            "西安", "重庆", "天津", "苏州", "郑州", "长沙", "东莞", "沈阳",
            "青岛", "合肥", "佛山", "厦门", "大连", "宁波", "济南", "福州"
        ]

        for city in cities:
            if city in text:
                # 尝试提取更详细的地址（包括区）
                pattern = rf'{city}[-\s]*([^\s，。、]+区)?'
                match = re.search(pattern, text)
                if match:
                    return match.group(0).strip()
                return city

        # 尝试匹配"工作地点："模式
        patterns = [
            r'工作地点[：:]\s*(.+?)[\n，。]',
            r'地点[：:]\s*(.+?)[\n，。]',
            r'坐标[：:]\s*(.+?)[\n，。]'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_skills(self, text: str) -> Tuple[List[str], List[str]]:
        """提取技能要求"""
        required_skills = []
        preferred_skills = []

        # 查找所有技能关键词
        for skill in self.skill_keywords:
            if skill.lower() in text.lower() or skill in text:
                # 判断是必备还是优先
                context_patterns = [
                    rf'(.{{0,20}}){re.escape(skill)}(.{{0,20}})',
                ]
                for pattern in context_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        context = match.group(0)
                        if any(word in context for word in ["优先", "加分", "plus", "最好"]):
                            if skill not in preferred_skills:
                                preferred_skills.append(skill)
                        else:
                            if skill not in required_skills:
                                required_skills.append(skill)
                        break

        return required_skills, preferred_skills

    def _extract_responsibilities(self, text: str) -> Optional[str]:
        """提取岗位职责"""
        patterns = [
            r'岗位职责[：:]\s*(.+?)(?=任职要求|岗位要求|技能要求|$)',
            r'工作职责[：:]\s*(.+?)(?=任职要求|岗位要求|技能要求|$)',
            r'职责描述[：:]\s*(.+?)(?=任职要求|岗位要求|技能要求|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()[:500]  # 限制长度
        return None

    def _extract_requirements(self, text: str) -> Optional[str]:
        """提取任职要求"""
        patterns = [
            r'任职要求[：:]\s*(.+?)(?=\n\n薪资|薪酬|福利待遇|工作地点|地点[：:]|$)',
            r'岗位要求[：:]\s*(.+?)(?=\n\n薪资|薪酬|福利待遇|工作地点|地点[：:]|$)',
            r'技能要求[：:]\s*(.+?)(?=\n\n薪资|薪酬|福利待遇|工作地点|地点[：:]|$)',
            r'要求[：:]\s*(.+?)(?=\n\n薪资|薪酬|福利待遇|工作地点|地点[：:]|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # 清理多余的换行，但保留结构
                content = re.sub(r'\n{3,}', '\n\n', content)
                return content[:800]  # 增加长度限制到800字符

        return None

    def _extract_industry(self, text: str) -> tuple:
        """
        提取所属行业，支持多标签和层级关系

        Returns:
            (主要行业, 行业标签列表)
        """
        # 行业层级关系：子行业 -> 父行业
        industry_hierarchy = {
            "人工智能": "计算机/软件",
            "游戏": "计算机/软件"
        }

        matched_industries = []

        # 收集所有匹配的行业
        for industry, keywords in self.industry_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if industry not in matched_industries:
                        matched_industries.append(industry)
                    break  # 该行业已匹配，跳到下一个行业

        if not matched_industries:
            return None, []

        # 构建完整的行业标签列表（包含层级关系）
        industry_tags = []

        for industry in matched_industries:
            # 如果有父行业且父行业不在匹配列表中，先添加父行业
            if industry in industry_hierarchy:
                parent = industry_hierarchy[industry]
                if parent not in industry_tags:
                    industry_tags.append(parent)

            # 添加当前行业
            if industry not in industry_tags:
                industry_tags.append(industry)

        # 主要行业是最具体的那个（最后一个）
        primary_industry = industry_tags[-1] if industry_tags else None

        return primary_industry, industry_tags

    def _extract_work_mode(self, text: str) -> Optional[str]:
        """提取工作模式"""
        if "远程" in text or "remote" in text.lower():
            return "远程"
        elif "混合" in text or "hybrid" in text.lower():
            return "混合办公"
        elif "驻场" in text:
            return "驻场"
        else:
            return "现场办公"

    def _extract_benefits(self, text: str) -> Optional[str]:
        """提取福利待遇"""
        benefits_keywords = [
            "福利", "待遇", "补贴", "五险一金", "年终奖", "股票期权",
            "带薪年假", "弹性工作", "免费", "提供", "可转正", "导师"
        ]

        # 查找包含福利关键词的句子
        lines = text.split('\n')
        benefit_lines = []

        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in benefits_keywords):
                # 排除岗位职责和任职要求部分
                if not any(x in line for x in ["岗位职责", "任职要求", "工作职责", "岗位要求"]):
                    benefit_lines.append(line)

        if benefit_lines:
            return "；".join(benefit_lines[:3])  # 最多返回3条

        # 尝试匹配福利待遇段落
        patterns = [
            r'福利待遇[：:]\s*(.+?)(?=\n\n|工作地点|$)',
            r'薪资福利[：:]\s*(.+?)(?=\n\n|工作地点|$)',
            r'公司福利[：:]\s*(.+?)(?=\n\n|工作地点|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()[:200]

        return None

    def _extract_company_type(self, text: str) -> Optional[str]:
        """提取公司类型"""
        company_types = {
            "上市公司": ["上市公司", "A股", "港股", "美股"],
            "外企": ["外企", "外资", "跨国公司", "multinational"],
            "国企": ["国企", "国有企业", "央企"],
            "创业公司": ["创业公司", "初创", "startup"],
            "独角兽": ["独角兽"],
            "民营企业": ["民营", "私企"]
        }

        for company_type, keywords in company_types.items():
            for keyword in keywords:
                if keyword in text:
                    return company_type
        return None

    def _extract_team_size(self, text: str) -> Optional[str]:
        """提取团队规模"""
        # 匹配团队规模数字
        patterns = [
            r'团队[：:]?\s*(\d+)\s*人',
            r'(\d+)\s*人[的]?团队',
            r'团队规模[：:]?\s*(\d+)',
            r'(\d+[-~]\d+)\s*人'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}人"

        return None

    def _calculate_confidence(self, info: ExtractedJobInfo, missing: List[str]) -> float:
        """计算提取置信度"""
        # 关键字段权重
        weights = {
            "job_title": 0.25,
            "education": 0.15,
            "experience": 0.15,
            "salary": 0.15,
            "location": 0.10,
            "skills": 0.20
        }

        score = 0.0

        if info.job_title:
            score += weights["job_title"]
        if info.education_requirement:
            score += weights["education"]
        if info.experience_requirement:
            score += weights["experience"]
        if info.salary_range:
            score += weights["salary"]
        if info.location:
            score += weights["location"]
        if info.required_skills:
            score += weights["skills"]

        return round(score, 2)


# 全局单例
job_info_extractor = JobInfoExtractor()
