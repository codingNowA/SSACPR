"""
岗位难度评估服务

基于多个维度评估岗位难度：
- 技能复杂度
- 经验要求
- 学历要求
- 薪资水平
- 公司知名度
"""
import re
from typing import Dict, Any, Optional


class JobDifficultyService:
    """岗位难度评估服务"""

    def calculate_difficulty(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算岗位难度

        Args:
            job: 岗位信息字典

        Returns:
            难度评估结果
        """
        dimensions = {
            "skill_complexity": self._evaluate_skill_complexity(job),
            "experience": self._evaluate_experience(job),
            "education": self._evaluate_education(job),
            "salary": self._evaluate_salary(job),
            "company": self._evaluate_company(job),
        }

        # 加权计算总分
        weights = {
            "skill_complexity": 0.35,  # 技能复杂度权重最高
            "experience": 0.25,
            "education": 0.15,
            "salary": 0.15,
            "company": 0.10,
        }

        total_score = sum(dimensions[k] * weights[k] for k in dimensions)
        total_score = round(total_score, 1)

        # 确定难度等级
        level = self._get_difficulty_level(total_score)

        return {
            "total_score": total_score,
            "level": level,
            "dimensions": dimensions,
        }

    def _evaluate_skill_complexity(self, job: Dict[str, Any]) -> float:
        """评估技能复杂度 (0-100)"""
        score = 50.0  # 基础分

        requirements = (job.get("requirements") or "") + " " + (job.get("description") or "")
        requirements_lower = requirements.lower()

        # 高级技能关键词
        advanced_keywords = [
            "架构", "分布式", "微服务", "高并发", "性能优化", "系统设计",
            "算法", "机器学习", "深度学习", "大数据", "云原生", "kubernetes",
            "devops", "cicd", "容器化", "负载均衡", "缓存", "消息队列",
            "elasticsearch", "redis", "kafka", "docker", "团队管理", "技术选型"
        ]

        # 中级技能关键词
        intermediate_keywords = [
            "java", "python", "golang", "c++", "spring", "django", "flask",
            "mysql", "postgresql", "mongodb", "git", "linux", "nginx",
            "restful", "api", "前端", "后端", "全栈", "测试", "调试"
        ]

        # 统计关键词出现次数
        advanced_count = sum(1 for kw in advanced_keywords if kw in requirements_lower)
        intermediate_count = sum(1 for kw in intermediate_keywords if kw in requirements_lower)

        # 根据关键词数量调整分数
        score += min(advanced_count * 5, 30)  # 高级技能最多加30分
        score += min(intermediate_count * 2, 20)  # 中级技能最多加20分

        # 技能数量
        if "5种以上" in requirements or "多种" in requirements:
            score += 10
        elif "3种以上" in requirements:
            score += 5

        return min(score, 100)

    def _evaluate_experience(self, job: Dict[str, Any]) -> float:
        """评估经验要求 (0-100)"""
        exp_required = job.get("experience_required", "") or ""
        exp_lower = exp_required.lower()

        # 提取年限数字
        numbers = re.findall(r'(\d+)', exp_required)

        if "10年" in exp_required or (numbers and int(numbers[0]) >= 10):
            return 95
        elif "8年" in exp_required or "7年" in exp_required or (numbers and int(numbers[0]) >= 7):
            return 85
        elif "5年" in exp_required or "6年" in exp_required or (numbers and int(numbers[0]) >= 5):
            return 70
        elif "3年" in exp_required or "4年" in exp_required or (numbers and int(numbers[0]) >= 3):
            return 50
        elif "1年" in exp_required or "2年" in exp_required or (numbers and int(numbers[0]) >= 1):
            return 30
        elif "应届" in exp_required or "不限" in exp_required or "无要求" in exp_required:
            return 10

        return 40  # 默认

    def _evaluate_education(self, job: Dict[str, Any]) -> float:
        """评估学历要求 (0-100)"""
        edu_required = job.get("education_required", "") or ""
        edu_lower = edu_required.lower()

        if "博士" in edu_required:
            return 100
        elif "硕士" in edu_required or "研究生" in edu_required:
            return 80
        elif "本科" in edu_required or "学士" in edu_required:
            return 50
        elif "大专" in edu_required or "专科" in edu_required:
            return 25
        elif "不限" in edu_required or "无要求" in edu_required:
            return 10

        return 40  # 默认

    def _evaluate_salary(self, job: Dict[str, Any]) -> float:
        """评估薪资水平 (0-100)"""
        salary_range = job.get("salary_range", "") or ""

        # 提取薪资数字 (K)
        numbers = re.findall(r'(\d+)', salary_range.upper().replace('K', ''))

        if not numbers:
            return 50

        # 取最大值作为参考
        max_salary = max(int(n) for n in numbers)

        if max_salary >= 80:
            return 95
        elif max_salary >= 60:
            return 85
        elif max_salary >= 45:
            return 70
        elif max_salary >= 30:
            return 50
        elif max_salary >= 20:
            return 35
        elif max_salary >= 15:
            return 25

        return 15

    def _evaluate_company(self, job: Dict[str, Any]) -> float:
        """评估公司知名度 (0-100)"""
        company = job.get("company", "") or ""
        company_type = job.get("company_type", "") or ""

        # 知名大厂
        top_companies = [
            "阿里", "腾讯", "字节", "百度", "华为", "美团", "京东", "网易",
            "小米", "滴滴", "快手", "拼多多", "google", "microsoft", "apple",
            "amazon", "facebook", "meta", "netflix", "ibm"
        ]

        company_lower = company.lower()
        if any(tc in company_lower for tc in top_companies):
            return 90

        # 上市公司
        if "上市" in company_type or "500强" in company_type:
            return 75

        # 独角兽/知名创业公司
        if "独角兽" in company_type or "B轮" in company_type or "C轮" in company_type:
            return 60

        # 初创公司
        if "创业" in company_type or "A轮" in company_type or "天使轮" in company_type:
            return 40

        return 50  # 默认

    def _get_difficulty_level(self, score: float) -> str:
        """根据分数确定难度等级"""
        if score >= 80:
            return "极难"
        elif score >= 65:
            return "困难"
        elif score >= 50:
            return "中等"
        elif score >= 35:
            return "简单"
        else:
            return "入门"


# 单例
job_difficulty_service = JobDifficultyService()
