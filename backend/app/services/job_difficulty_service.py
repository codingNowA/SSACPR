"""
岗位难度评估服务

基于多维度指标评估岗位难度（0-100分）
"""
import logging
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class JobDifficultyService:
    """岗位难度评估服务"""

    def calculate_difficulty(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算岗位难度分数（0-100）

        评估维度：
        1. 技能复杂度（30%）- 基于岗位要求的技能数量和深度
        2. 经验要求（25%）- 工作年限要求
        3. 学历要求（15%）- 学历门槛
        4. 薪资水平（20%）- 薪资越高通常难度越大
        5. 公司知名度（10%）- 知名公司竞争更激烈

        返回格式：
        {
            "total_score": 75,
            "level": "困难",
            "dimensions": {
                "skill_complexity": 80,
                "experience": 70,
                "education": 60,
                "salary": 85,
                "company": 65
            }
        }
        """
        scores = {
            "skill_complexity": self._assess_skill_complexity(job),
            "experience": self._assess_experience_requirement(job),
            "education": self._assess_education_requirement(job),
            "salary": self._assess_salary_level(job),
            "company": self._assess_company_prestige(job),
        }

        # 加权计算总分
        weights = {
            "skill_complexity": 0.30,
            "experience": 0.25,
            "education": 0.15,
            "salary": 0.20,
            "company": 0.10,
        }

        total_score = sum(scores[k] * weights[k] for k in scores.keys())
        total_score = round(total_score, 1)

        # 难度等级划分
        if total_score >= 80:
            level = "很困难"
        elif total_score >= 65:
            level = "困难"
        elif total_score >= 50:
            level = "中等"
        elif total_score >= 35:
            level = "较简单"
        else:
            level = "简单"

        return {
            "total_score": total_score,
            "level": level,
            "dimensions": scores,
        }

    def _assess_skill_complexity(self, job: Dict[str, Any]) -> float:
        """评估技能复杂度（0-100）"""
        score = 50.0  # 基础分

        # 从 requirements 或 description 提取技能关键词
        text = f"{job.get('requirements', '')} {job.get('description', '')}".lower()

        # 高级技能关键词
        advanced_skills = [
            'kubernetes', 'docker', 'microservices', '微服务', 'distributed', '分布式',
            'machine learning', '机器学习', 'deep learning', '深度学习', 'ai', '人工智能',
            'big data', '大数据', 'spark', 'hadoop', 'elasticsearch', 'redis', 'mongodb',
            'react', 'vue', 'angular', 'spring boot', 'springcloud', 'mybatis',
            'kafka', 'rabbitmq', 'nginx', 'linux', 'shell', 'python', 'java', 'golang',
            'c++', 'architecture', '架构', 'algorithm', '算法', 'data structure', '数据结构',
        ]

        skill_count = sum(1 for skill in advanced_skills if skill in text)

        # 技能数量越多，难度越高
        if skill_count >= 10:
            score = 90
        elif skill_count >= 7:
            score = 75
        elif skill_count >= 5:
            score = 60
        elif skill_count >= 3:
            score = 45
        else:
            score = 30

        # 检查是否要求多种编程语言
        languages = ['java', 'python', 'golang', 'c++', 'javascript', 'typescript', 'rust', 'scala']
        lang_count = sum(1 for lang in languages if lang in text)
        if lang_count >= 3:
            score += 10
        elif lang_count >= 2:
            score += 5

        return min(100.0, score)

    def _assess_experience_requirement(self, job: Dict[str, Any]) -> float:
        """评估经验要求（0-100）"""
        exp_text = job.get('experience_required', '').lower()

        # 提取年限数字
        years = self._extract_years(exp_text)

        if years is None:
            # 没有明确要求，默认中等
            return 40.0

        # 年限映射到分数
        if years >= 10:
            return 100.0
        elif years >= 7:
            return 90.0
        elif years >= 5:
            return 75.0
        elif years >= 3:
            return 60.0
        elif years >= 1:
            return 40.0
        else:
            return 20.0

    def _assess_education_requirement(self, job: Dict[str, Any]) -> float:
        """评估学历要求（0-100）"""
        edu_text = job.get('education_required', '').lower()

        if '博士' in edu_text or 'phd' in edu_text or '研究生' in edu_text:
            return 100.0
        elif '硕士' in edu_text or 'master' in edu_text:
            return 85.0
        elif '本科' in edu_text or 'bachelor' in edu_text or '学士' in edu_text:
            return 60.0
        elif '专科' in edu_text or '大专' in edu_text:
            return 35.0
        else:
            return 50.0  # 未明确，默认中等

    def _assess_salary_level(self, job: Dict[str, Any]) -> float:
        """评估薪资水平（0-100）"""
        salary_text = job.get('salary_range', '')

        # 解析薪资范围（单位：K/月）
        salary_range = self._parse_salary(salary_text)

        if salary_range is None:
            return 50.0  # 面议或无法解析，默认中等

        min_salary, max_salary = salary_range
        avg_salary = (min_salary + max_salary) / 2

        # 薪资映射到难度分数
        if avg_salary >= 40:
            return 100.0
        elif avg_salary >= 30:
            return 85.0
        elif avg_salary >= 20:
            return 70.0
        elif avg_salary >= 15:
            return 55.0
        elif avg_salary >= 10:
            return 40.0
        else:
            return 25.0

    def _assess_company_prestige(self, job: Dict[str, Any]) -> float:
        """评估公司知名度（0-100）"""
        company = job.get('company', '').lower()

        # 知名公司关键词
        top_companies = [
            'alibaba', '阿里', 'tencent', '腾讯', 'baidu', '百度', 'huawei', '华为',
            'bytedance', '字节', 'tiktok', 'meituan', '美团', 'jd', '京东', 'xiaomi', '小米',
            'didi', '滴滴', 'netease', '网易', 'pinduoduo', '拼多多', 'bilibili', 'b站',
            'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta', 'netflix',
            'ibm', 'oracle', 'salesforce', 'twitter', 'uber', 'airbnb', 'tesla',
        ]

        for top in top_companies:
            if top in company:
                return 90.0

        # 检查是否包含"有限公司"、"科技"等关键词
        if '科技' in company or 'technology' in company:
            return 60.0
        elif '有限公司' in company or 'co., ltd' in company:
            return 50.0
        else:
            return 40.0

    def _extract_years(self, text: str) -> Optional[float]:
        """从文本中提取年限数字"""
        # 匹配 "3年"、"3-5年"、"3到5年"、"3+ years"
        patterns = [
            r'(\d+)\s*[-到至~]\s*(\d+)\s*年',
            r'(\d+)\s*年',
            r'(\d+)\s*\+?\s*years?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    # 范围，取平均值
                    return (float(match.group(1)) + float(match.group(2))) / 2
                else:
                    return float(match.group(1))

        # 文字年限
        if '应届' in text or 'fresh' in text:
            return 0.0
        elif '十年' in text:
            return 10.0
        elif '五年' in text:
            return 5.0
        elif '三年' in text:
            return 3.0

        return None

    def _parse_salary(self, salary_text: str) -> Optional[tuple]:
        """解析薪资范围（单位：K）"""
        if not salary_text:
            return None

        text = salary_text.upper().replace(' ', '')

        # 匹配 "15K-25K" 或 "15-25K"
        pattern = r'(\d+)\s*[K万]?\s*[-–—]\s*(\d+)\s*[K万]?'
        match = re.search(pattern, text)
        if match:
            return (int(match.group(1)), int(match.group(2)))

        # 匹配 "15K+" 或 "15K"
        pattern2 = r'(\d+)\s*K'
        match2 = re.search(pattern2, text)
        if match2:
            val = int(match2.group(1))
            return (val, val)

        return None


    async def get_jobs_with_difficulty(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取岗位列表（带难度评估）

        支持排序、筛选和搜索
        """
        from app.services.job_service import get_db_pool

        pool = await get_db_pool()

        # 构建查询条件
        where_clauses = ["1=1"]
        params = {}

        if keyword:
            where_clauses.append("(title ILIKE %(keyword)s OR company ILIKE %(keyword)s OR description ILIKE %(keyword)s)")
            params["keyword"] = f"%{keyword}%"

        if location:
            where_clauses.append("location ILIKE %(location)s")
            params["location"] = f"%{location}%"

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        count_query = f"SELECT COUNT(*) FROM jobs WHERE {where_sql}"

        async with pool.acquire() as conn:
            total = await conn.fetchval(count_query, **params)

            # 查询数据
            offset = (page - 1) * page_size

            # 根据 sort_by 决定排序字段
            if sort_by == "difficulty":
                # 先获取所有数据，然后在Python中排序
                query = f"""
                    SELECT id, title, company, location, salary_range, industry,
                           description, requirements, experience_required, education_required
                    FROM jobs
                    WHERE {where_sql}
                """
                rows = await conn.fetch(query, **params)

                # 计算每个岗位的难度
                jobs_with_difficulty = []
                for row in rows:
                    job_dict = dict(row)
                    difficulty = self.calculate_difficulty(job_dict)
                    jobs_with_difficulty.append({
                        **job_dict,
                        "difficulty": {
                            "level": difficulty["level"],
                            "score": difficulty["total_score"],
                            "dimensions": difficulty["dimensions"]
                        }
                    })

                # 按难度排序
                reverse = (order.lower() == "desc")
                jobs_with_difficulty.sort(
                    key=lambda x: x["difficulty"]["score"],
                    reverse=reverse
                )

                # 分页
                start = offset
                end = offset + page_size
                items = jobs_with_difficulty[start:end]

            else:
                # 普通排序
                order_clause = f"ORDER BY {sort_by} {order.upper()}"
                query = f"""
                    SELECT id, title, company, location, salary_range, industry,
                           description, requirements, experience_required, education_required
                    FROM jobs
                    WHERE {where_sql}
                    {order_clause}
                    LIMIT {page_size} OFFSET {offset}
                """

                rows = await conn.fetch(query, **params)

                # 计算难度
                items = []
                for row in rows:
                    job_dict = dict(row)
                    difficulty = self.calculate_difficulty(job_dict)
                    items.append({
                        **job_dict,
                        "difficulty": {
                            "level": difficulty["level"],
                            "score": difficulty["total_score"],
                            "dimensions": difficulty["dimensions"]
                        }
                    })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def calculate_job_difficulty(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        计算单个岗位的难度
        """
        from app.services.job_service import get_db_pool

        pool = await get_db_pool()

        async with pool.acquire() as conn:
            query = """
                SELECT id, title, company, location, salary_range, industry,
                       description, requirements, experience_required, education_required
                FROM jobs
                WHERE id = $1
            """
            row = await conn.fetchrow(query, job_id)

            if not row:
                return None

            job_dict = dict(row)
            difficulty = self.calculate_difficulty(job_dict)

            return {
                "level": difficulty["level"],
                "score": difficulty["total_score"],
                "dimensions": difficulty["dimensions"]
            }


# 单例
job_difficulty_service = JobDifficultyService()
