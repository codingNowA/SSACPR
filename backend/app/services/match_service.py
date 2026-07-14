"""
岗位匹配服务 - 核心匹配算法

流程：
1. 从 PostgreSQL 加载简历画像
2. 从 OpenSearch 召回候选岗位（关键词 + 偏好过滤）
3. 混合打分：技能匹配 + 语义匹配 + 偏好匹配
4. LLM 生成匹配理由
5. 分层返回结果

修复：
- math import 移到顶部
- 薪资偏好匹配纳入 _preference_score
- jieba 分词提取技能替代硬编码词表
- 公司性质偏好匹配
"""
from __future__ import annotations

import json
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

import asyncpg

from app.ai.llm.prompts import (
    MATCH_SYSTEM_PROMPT,
    build_match_user_prompt,
)
from app.ai.llm.chain import llm_service
from app.schemas.job import (
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    MatchCategory,
    MatchHistoryItem,
    MatchHistoryResponse,
    MatchPreferences,
    ResumeProfile,
)
from app.services.job_service import JobService, job_service, get_db_pool, parse_salary_range

logger = logging.getLogger(__name__)

# ============================================================
# 技能提取（基于 jieba 分词）
# ============================================================

# 技能领域词典（用于 jieba 自定义分词 + 关键词匹配）
SKILL_LEXICON: List[str] = [
    # 编程语言
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Golang", "C++", "C#",
    "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    # Web 框架
    "FastAPI", "Flask", "Django", "Spring", "SpringBoot", "Express", "Koa",
    "React", "Vue", "Angular", "Next.js", "Nuxt.js",
    # 数据库
    "SQL", "MySQL", "PostgreSQL", "Redis", "MongoDB", "Elasticsearch",
    "OpenSearch", "ClickHouse", "SQLite", "Oracle",
    # 基础设施
    "Docker", "Kubernetes", "K8s", "Linux", "Nginx", "Tomcat",
    "AWS", "Azure", "GCP", "阿里云", "腾讯云",
    # 工具链
    "Git", "CI/CD", "Jenkins", "GitHub Actions", "Terraform",
    # 数据 & AI
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Hadoop", "Spark", "Hive", "Flink", "Kafka", "Airflow",
    # 前端
    "HTML", "CSS", "Sass", "Less", "Webpack", "Vite",
    # 通信 & 架构
    "REST", "GraphQL", "gRPC", "Microservice", "微服务", "分布式",
    "消息队列", "设计模式",
    # 方法论
    "Agile", "Scrum", "DevOps", "TDD",
    # 通用技能
    "数据结构", "算法", "操作系统", "计算机网络", "数据库原理",
    "Excel", "Power BI", "Tableau", "SPSS",
]

# 小写索引，用于快速匹配
_SKILL_LOWER_MAP = {s.lower(): s for s in SKILL_LEXICON}

# 尝试加载 jieba
_try_jieba = True


def extract_skills_from_text(text: str) -> List[str]:
    """
    从文本中提取技能关键词。

    优先使用 jieba 分词匹配自定义技能词典，
    回退到简单的字符串包含匹配。
    """
    global _try_jieba

    if not text:
        return []

    found_skills = []
    text_lower = text.lower()

    # 方法1：直接字符串匹配（始终执行，作为兜底）
    # 注意：跳过单字符技能（如 "R"），避免误匹配
    for skill_lower, skill_original in _SKILL_LOWER_MAP.items():
        if len(skill_lower) <= 1:
            continue
        if skill_lower in text_lower:
            found_skills.append(skill_original)

    # 方法2：jieba 分词匹配（更精准，能识别"精通Python开发"中的 Python）
    if _try_jieba:
        try:
            import jieba
            # 动态添加技能词到 jieba 词典
            for skill in SKILL_LEXICON:
                jieba.add_word(skill)
            words = jieba.lcut(text)
            for word in words:
                word_stripped = word.strip()
                # 跳过单字符分词结果，避免误匹配 "R" 等
                if len(word_stripped) <= 1:
                    continue
                if word_stripped.lower() in _SKILL_LOWER_MAP:
                    original = _SKILL_LOWER_MAP[word_stripped.lower()]
                    if original not in found_skills:
                        found_skills.append(original)
        except ImportError:
            _try_jieba = False
            logger.debug("jieba 未安装，使用基础技能提取")
        except Exception as e:
            _try_jieba = False
            logger.debug(f"jieba 分词异常，回退到基础提取: {e}")

    return found_skills


# ============================================================
# 岗位匹配器
# ============================================================

class JobMatcher:
    """岗位匹配器"""

    # 权重配置
    WEIGHT_SKILL = 0.45        # 技能关键词匹配
    WEIGHT_SEMANTIC = 0.35     # 语义匹配（基于 OpenSearch 相关度）
    WEIGHT_PREFERENCE = 0.20   # 用户偏好匹配

    # 分层阈值
    THRESHOLD_HIGH = 80.0
    THRESHOLD_MEDIUM = 60.0

    def __init__(self, job_svc: Optional[JobService] = None) -> None:
        self.job_svc = job_svc or job_service

    # ----------------------------------------------------------
    # 主入口
    # ----------------------------------------------------------

    async def match(self, request: JobMatchRequest) -> JobMatchResponse:
        """
        执行岗位匹配

        1. 加载简历画像
        2. 召回候选岗位
        3. 混合打分
        4. LLM 生成推荐理由
        5. 分层返回 + 持久化匹配记录
        """
        # 1. 加载简历画像
        profile = await self._load_resume_profile(request.resume_id)
        if profile is None:
            raise ValueError(f"简历 ID {request.resume_id} 不存在或未解析")

        # 2. 召回候选岗位
        search_keywords = profile.skills[:15] if profile.skills else []
        if profile.target_position:
            search_keywords = [profile.target_position] + search_keywords

        candidates = await self.job_svc.recall_jobs(
            keywords=search_keywords if search_keywords else None,
            preferences=request.preferences,
            size=100,
        )

        if not candidates:
            return JobMatchResponse(resume_id=request.resume_id, total=0)

        # 3. 混合打分
        scored = []
        for candidate in candidates:
            scores = self._calculate_scores(profile, candidate, request.preferences)
            scored.append((candidate, scores))

        # 按总分降序
        scored.sort(key=lambda x: x[1]["final_score"], reverse=True)
        scored = scored[: request.top_k]

        # 4. LLM 生成推荐理由（对 top 结果）
        results: List[JobMatchResult] = []
        for candidate, scores in scored:
            match_reason = await self._generate_match_reason(profile, candidate, scores)

            result = JobMatchResult(
                job_id=candidate.get("id", 0),
                job_title=candidate.get("title", ""),
                company=candidate.get("company"),
                location=candidate.get("location"),
                salary_range=candidate.get("salary_range"),
                match_score=round(scores["final_score"], 1),
                matched_skills=scores["matched_skills"],
                missing_skills=scores["missing_skills"],
                match_reason=match_reason,
                category=self._categorize(scores["final_score"]),
            )
            results.append(result)

        # 5. 分层
        highly = [r for r in results if r.category == MatchCategory.highly_matched][:10]
        fairly = [r for r in results if r.category == MatchCategory.fairly_matched][:10]
        development = [r for r in results if r.category == MatchCategory.development_direction][:5]

        response = JobMatchResponse(
            resume_id=request.resume_id,
            total=len(results),
            highly_matched=highly,
            fairly_matched=fairly,
            development_direction=development,
        )

        # 持久化匹配记录
        await self._save_match_records(request.resume_id, results)

        return response

    # ----------------------------------------------------------
    # 评分算法
    # ----------------------------------------------------------

    def _calculate_scores(
        self,
        profile: ResumeProfile,
        candidate: Dict[str, Any],
        preferences: Optional[MatchPreferences] = None,
    ) -> Dict[str, Any]:
        """
        混合打分

        返回:
        {
            "skill_score": float,       # 技能匹配分 0-100
            "semantic_score": float,    # 语义相关度 0-100
            "preference_score": float,  # 偏好匹配分 0-100
            "final_score": float,       # 加权总分 0-100
            "matched_skills": [...],
            "missing_skills": [...],
        }
        """
        # --- 技能关键词匹配 ---
        resume_skills = set(s.lower().strip() for s in profile.skills if s)
        job_skills_raw = candidate.get("skills", []) or []
        # 如果没有 skills 字段，从 requirements 文本中提取
        if not job_skills_raw:
            job_skills_raw = extract_skills_from_text(
                candidate.get("requirements", "") or ""
            )
        job_skills = set(s.lower().strip() for s in job_skills_raw if s)

        matched = list(resume_skills & job_skills)
        missing = list(job_skills - resume_skills)

        if job_skills:
            skill_score = len(matched) / len(job_skills) * 100
        else:
            skill_score = 50.0  # 无技能数据时给中间分

        # --- 语义相关度（基于 OpenSearch _score 归一化）---
        raw_score = candidate.get("_score", 0)
        if raw_score > 0:
            # BM25 _score 通常在 0-30，用 sigmoid 映射到 0-100
            semantic_score = 100 / (1 + math.exp(-0.3 * (raw_score - 10)))
        else:
            # 无 OpenSearch 分数时，基于标题相似度给基础分
            semantic_score = self._title_similarity_score(
                profile.target_position or "",
                candidate.get("title", ""),
            )

        # --- 偏好匹配 ---
        preference_score = self._preference_score(candidate, preferences)

        # --- 加权总分 ---
        final_score = (
            self.WEIGHT_SKILL * skill_score
            + self.WEIGHT_SEMANTIC * semantic_score
            + self.WEIGHT_PREFERENCE * preference_score
        )

        return {
            "skill_score": round(skill_score, 1),
            "semantic_score": round(semantic_score, 1),
            "preference_score": round(preference_score, 1),
            "final_score": round(final_score, 1),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
        }

    def _preference_score(
        self,
        candidate: Dict[str, Any],
        preferences: Optional[MatchPreferences] = None,
    ) -> float:
        """
        计算偏好匹配分

        综合考量：行业、城市、学历、经验、薪资、公司性质
        每个维度权重相等，未设置偏好则不计入
        """
        if preferences is None:
            return 50.0  # 无偏好时给中间分

        hits = 0
        total = 0

        # 行业
        if preferences.industries:
            total += 1
            if candidate.get("industry") in preferences.industries:
                hits += 1

        # 城市
        if preferences.cities:
            total += 1
            if candidate.get("location") in preferences.cities:
                hits += 1

        # 学历
        if preferences.education:
            total += 1
            job_edu = candidate.get("education_required", "") or ""
            if preferences.education in job_edu or job_edu in ("不限", "学历不限"):
                hits += 1

        # 经验
        if preferences.experience:
            total += 1
            job_exp = candidate.get("experience_required", "") or ""
            if preferences.experience in job_exp or job_exp in ("不限", "经验不限"):
                hits += 1

        # 公司性质
        if preferences.company_types:
            total += 1
            if candidate.get("company_type") in preferences.company_types:
                hits += 1

        # 薪资匹配
        if preferences.salary_min is not None or preferences.salary_max is not None:
            total += 1
            salary = parse_salary_range(candidate.get("salary_range"))
            if salary is None:
                # 无法解析薪资，给部分分
                hits += 0.5
            else:
                job_min, job_max = salary
                # 用户期望与岗位薪资有交集即算匹配
                salary_match = True
                if preferences.salary_min is not None and job_max < preferences.salary_min:
                    salary_match = False
                if preferences.salary_max is not None and job_min > preferences.salary_max:
                    salary_match = False
                if salary_match:
                    hits += 1

        if total == 0:
            return 50.0

        return hits / total * 100

    def _title_similarity_score(self, target: str, title: str) -> float:
        """简单的标题相似度评分（字符重叠度）"""
        if not target or not title:
            return 30.0
        target_chars = set(target.lower())
        title_chars = set(title.lower())
        if not target_chars:
            return 30.0
        overlap = len(target_chars & title_chars) / len(target_chars | title_chars)
        return overlap * 80 + 20  # 映射到 20-100

    def _categorize(self, score: float) -> MatchCategory:
        """根据分数分层"""
        if score >= self.THRESHOLD_HIGH:
            return MatchCategory.highly_matched
        elif score >= self.THRESHOLD_MEDIUM:
            return MatchCategory.fairly_matched
        else:
            return MatchCategory.development_direction

    # ----------------------------------------------------------
    # LLM 推荐理由
    # ----------------------------------------------------------

    async def _generate_match_reason(
        self,
        profile: ResumeProfile,
        candidate: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> str:
        """调用 LLM 生成匹配推荐理由"""
        try:
            user_prompt = build_match_user_prompt(
                resume_summary=profile.summary or "",
                resume_skills=profile.skills,
                job_title=candidate.get("title", ""),
                job_description=candidate.get("description", ""),
                job_requirements=candidate.get("requirements", ""),
                job_skills=candidate.get("skills"),
            )
            result = await llm_service.chat_json(
                prompt=user_prompt,
                system_prompt=MATCH_SYSTEM_PROMPT,
                temperature=0.3,
            )
            return result.get("match_reason", "")
        except Exception as e:
            logger.warning(f"LLM 生成匹配理由失败，使用默认理由: {e}")
            # 降级：生成简单的规则理由
            matched = scores.get("matched_skills", [])
            missing = scores.get("missing_skills", [])
            parts = []
            if matched:
                parts.append(f"命中技能：{'、'.join(matched[:5])}")
            if missing:
                parts.append(f"建议补充：{'、'.join(missing[:3])}")
            return "；".join(parts) if parts else "综合匹配"

    # ----------------------------------------------------------
    # 简历画像加载
    # ----------------------------------------------------------

    async def _load_resume_profile(self, resume_id: int) -> Optional[ResumeProfile]:
        """从 PostgreSQL 加载简历画像"""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT parsed_data FROM resumes WHERE id = $1",
                resume_id,
            )
        if row is None or row["parsed_data"] is None:
            return None

        parsed = row["parsed_data"]
        if isinstance(parsed, str):
            parsed = json.loads(parsed)

        return self._build_profile_from_parsed(parsed)

    def _build_profile_from_parsed(self, parsed: Dict[str, Any]) -> ResumeProfile:
        """将 parsed_data JSON 转换为 ResumeProfile"""
        skills = parsed.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

        education_raw = parsed.get("education", [])
        education = [edu for edu in education_raw if isinstance(edu, dict)] if isinstance(education_raw, list) else []

        experience_raw = parsed.get("experience", [])
        experience = [exp for exp in experience_raw if isinstance(exp, dict)] if isinstance(experience_raw, list) else []

        projects_raw = parsed.get("projects", [])
        projects = [proj for proj in projects_raw if isinstance(proj, dict)] if isinstance(projects_raw, list) else []

        return ResumeProfile(
            name=parsed.get("name"),
            skills=skills,
            education=education,
            experience=experience,
            projects=projects,
            summary=parsed.get("summary") or parsed.get("self_evaluation"),
            target_position=parsed.get("target_position"),
            target_industry=parsed.get("target_industry"),
        )

    # ----------------------------------------------------------
    # 匹配记录持久化
    # ----------------------------------------------------------

    async def _save_match_records(
        self, resume_id: int, results: List[JobMatchResult]
    ) -> None:
        """保存匹配记录到 PostgreSQL"""
        if not results:
            return

        pool = await get_db_pool()
        # 获取 resume 关联的 user_id
        async with pool.acquire() as conn:
            user_row = await conn.fetchrow(
                "SELECT user_id FROM resumes WHERE id = $1", resume_id
            )
        user_id = user_row["user_id"] if user_row else None

        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO matches (user_id, resume_id, job_id, match_score,
                                         matched_skills, missing_skills, reason)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7)
                    """,
                    [
                        (
                            user_id,
                            resume_id,
                            r.job_id,
                            r.match_score,
                            json.dumps(r.matched_skills, ensure_ascii=False),
                            json.dumps(r.missing_skills, ensure_ascii=False),
                            r.match_reason,
                        )
                        for r in results
                    ],
                )

    # ----------------------------------------------------------
    # 匹配历史查询
    # ----------------------------------------------------------

    async def get_match_history(
        self,
        resume_id: Optional[int] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> MatchHistoryResponse:
        """查询匹配历史"""
        pool = await get_db_pool()
        conditions = []
        params = []
        idx = 1

        if resume_id:
            conditions.append(f"m.resume_id = ${idx}")
            params.append(resume_id)
            idx += 1
        if user_id:
            conditions.append(f"m.user_id = ${idx}")
            params.append(user_id)
            idx += 1

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_row = await pool.fetchrow(
            f"SELECT COUNT(*) as cnt FROM matches m {where}", *params
        )
        total = count_row["cnt"]

        offset = (page - 1) * page_size
        rows = await pool.fetch(
            f"""
            SELECT m.id, m.resume_id, m.job_id, m.match_score,
                   m.matched_skills, m.missing_skills, m.reason,
                   m.created_at,
                   j.title as job_title, j.company
            FROM matches m
            LEFT JOIN jobs j ON m.job_id = j.id
            {where}
            ORDER BY m.created_at DESC
            LIMIT {page_size} OFFSET {offset}
            """,
            *params,
        )

        items = []
        for r in rows:
            matched_skills = r["matched_skills"]
            if isinstance(matched_skills, str):
                matched_skills = json.loads(matched_skills)
            missing_skills = r["missing_skills"]
            if isinstance(missing_skills, str):
                missing_skills = json.loads(missing_skills)

            items.append(MatchHistoryItem(
                id=r["id"],
                resume_id=r["resume_id"],
                job_id=r["job_id"],
                job_title=r["job_title"],
                company=r["company"],
                match_score=float(r["match_score"]),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                reason=r["reason"],
                created_at=r["created_at"],
            ))

        return MatchHistoryResponse(total=total, items=items)


# 单例
job_matcher = JobMatcher()
