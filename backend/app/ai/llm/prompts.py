"""
LLM 提示词模板
"""
from __future__ import annotations

from typing import List, Optional


# ============================================================
# 岗位匹配提示词
# ============================================================

MATCH_SYSTEM_PROMPT = """你是一名专业的职业规划顾问。你的任务是分析求职者的简历画像与目标岗位的匹配程度。

你需要：
1. 评估简历与岗位的整体匹配度（0-100分）
2. 找出求职者已具备的岗位所需技能（命中技能）
3. 找出求职者缺失但岗位要求的技能（缺失技能）
4. 给出简明的推荐理由（2-3句话）

请严格按照 JSON 格式输出，不要包含任何其他文字：
{
    "match_score": 85,
    "matched_skills": ["Python", "FastAPI", "SQL"],
    "missing_skills": ["Kubernetes", "微服务"],
    "match_reason": "求职者具备岗位要求的核心后端开发技能，项目经验与岗位需求高度相关。建议补充容器化和微服务方面的知识。"
}"""


def build_match_user_prompt(
    resume_summary: str,
    resume_skills: List[str],
    job_title: str,
    job_description: str,
    job_requirements: str,
    job_skills: Optional[List[str]] = None,
) -> str:
    """构建岗位匹配的用户提示词"""
    skills_str = "、".join(resume_skills) if resume_skills else "无"
    job_skills_str = "、".join(job_skills) if job_skills else "见岗位要求"

    return f"""## 求职者简历画像

### 个人摘要
{resume_summary or '未提供'}

### 技能标签
{skills_str}

---

## 目标岗位

### 岗位名称
{job_title}

### 岗位描述
{job_description or '未提供'}

### 岗位要求
{job_requirements or '未提供'}

### 要求技能
{job_skills_str}

---

请分析该求职者与目标岗位的匹配程度，按 JSON 格式输出。"""


# ============================================================
# 匹配理由补充提示词（当需要更详细的解释时）
# ============================================================

EXPLAIN_SYSTEM_PROMPT = """你是一名专业的职业规划顾问。请根据求职者的简历画像和岗位匹配结果，用简洁易懂的语言解释为什么推荐这个岗位。

要求：
- 先说匹配亮点（求职者适合这个岗位的地方）
- 再说差距与建议（求职者需要提升的方面）
- 语言简洁，3-5句话
- 避免使用过于技术化的术语
"""


def build_explain_user_prompt(
    job_title: str,
    company: Optional[str],
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
) -> str:
    """构建匹配解释的用户提示词"""
    company_info = f"（{company}）" if company else ""
    matched_str = "、".join(matched_skills) if matched_skills else "无"
    missing_str = "、".join(missing_skills) if missing_skills else "无"

    return f"""岗位：{job_title}{company_info}
匹配分数：{match_score}
命中技能：{matched_str}
缺失技能：{missing_str}

请解释为什么推荐这个岗位。"""


# ============================================================
# 岗位画像提取提示词
# ============================================================

JOB_PROFILE_SYSTEM_PROMPT = """你是一名专业的 HR 数据分析师。你的任务是从岗位描述中提取结构化的岗位画像。

请严格按照 JSON 格式输出：
{
    "core_skills": ["Python", "SQL", "Linux"],
    "bonus_skills": ["Kubernetes", "CI/CD"],
    "experience_level": "1-3年",
    "education_level": "本科及以上",
    "salary_estimate": "15K-25K",
    "difficulty": "中等",
    "career_path": "初级后端开发 -> 高级开发 -> 技术负责人",
    "key_responsibilities": ["负责后端API开发", "数据库设计与优化"]
}"""


def build_job_profile_user_prompt(title: str, description: str, requirements: str) -> str:
    """构建岗位画像提取的用户提示词"""
    return f"""## 岗位名称
{title}

## 岗位描述
{description or '未提供'}

## 岗位要求
{requirements or '未提供'}

请提取该岗位的结构化画像。"""
