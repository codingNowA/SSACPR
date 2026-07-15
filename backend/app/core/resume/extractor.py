"""
简历结构化提取器
使用 LLM 从简历文本中提取结构化信息
"""
import json
from typing import Dict, Any, Optional

from app.ai.llm.client import default_llm_client, LLMClientError
from app.schemas.resume_structured import (
    ResumeStructuredData,
    BasicInfo,
    Education,
    WorkExperience,
    ProjectExperience,
    SkillTag,
)


class ResumeExtractorError(Exception):
    """简历提取异常"""
    pass


class ResumeExtractor:
    """简历结构化提取器"""

    def __init__(self):
        self.llm_client = default_llm_client

    async def extract_structured_data(self, resume_text: str) -> ResumeStructuredData:
        """
        从简历文本中提取结构化数据

        Args:
            resume_text: 简历文本

        Returns:
            结构化数据

        Raises:
            ResumeExtractorError: 提取失败
        """
        if not resume_text or len(resume_text.strip()) < 10:
            raise ResumeExtractorError("简历文本为空或过短")

        try:
            # 使用 LLM 提取结构化数据
            extracted_data = await self._llm_extract(resume_text)

            # 转换为 Pydantic 模型
            structured_data = self._parse_extracted_data(extracted_data)

            return structured_data

        except LLMClientError as e:
            raise ResumeExtractorError(f"LLM 调用失败: {str(e)}")
        except Exception as e:
            raise ResumeExtractorError(f"提取失败: {str(e)}")

    async def _llm_extract(self, resume_text: str) -> Dict[str, Any]:
        """
        使用 LLM 提取结构化数据

        Args:
            resume_text: 简历文本

        Returns:
            提取的 JSON 数据
        """
        system_prompt = """你是一个专业的简历解析助手。你的任务是从简历文本中提取结构化信息。

请严格按照以下 JSON 格式返回数据（只返回 JSON，不要有其他文字）：

{
  "basic_info": {
    "name": "姓名",
    "phone": "电话",
    "email": "邮箱",
    "age": 年龄（数字），
    "gender": "性别",
    "location": "所在地",
    "job_intention": "求职意向"
  },
  "education": [
    {
      "school": "学校名称",
      "major": "专业",
      "degree": "学历（本科/硕士/博士）",
      "start_date": "开始时间（如：2018-09）",
      "end_date": "结束时间（如：2022-06）",
      "gpa": "GPA",
      "description": "描述"
    }
  ],
  "work_experience": [
    {
      "company": "公司名称",
      "position": "职位",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "description": "工作内容描述",
      "achievements": ["成果1", "成果2"]
    }
  ],
  "project_experience": [
    {
      "name": "项目名称",
      "role": "项目角色",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "description": "项目描述",
      "tech_stack": ["技术1", "技术2"],
      "achievements": ["成果1", "成果2"]
    }
  ],
  "skills": [
    {
      "category": "技能分类（如：编程语言/框架/工具）",
      "name": "技能名称",
      "level": "熟练度（熟练/精通/了解）"
    }
  ]
}

注意：
1. 如果某个字段在简历中找不到，设置为 null
2. 数组字段如果为空，返回空数组 []
3. 工作经历包含全职工作和实习
4. 时间格式尽量统一为 YYYY-MM 或 YYYY.MM
5. 从简历中提取所有技能，并分类整理
"""

        user_prompt = f"""请从以下简历文本中提取结构化信息：

{resume_text}

请严格按照 JSON 格式返回数据。"""

        try:
            result = await self.llm_client.chat_json(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # 降低温度以获得更确定的输出
            )
            return result
        except Exception as e:
            raise ResumeExtractorError(f"LLM 提取失败: {str(e)}")

    def _parse_extracted_data(self, data: Dict[str, Any]) -> ResumeStructuredData:
        """
        将提取的 JSON 数据转换为 Pydantic 模型

        Args:
            data: LLM 提取的 JSON 数据

        Returns:
            结构化数据模型
        """
        try:
            # 解析基本信息（字段可能为 null，使用 or {} 兜底）
            basic_info_data = data.get('basic_info') or {}
            basic_info = BasicInfo(**basic_info_data) if basic_info_data else None

            # 解析教育经历（LLM 可能对空字段返回 null，使用 or [] 兜底）
            education_list = []
            for edu in (data.get('education') or []):
                if edu:
                    education_list.append(Education(**edu))

            # 解析工作经历
            work_list = []
            for work in (data.get('work_experience') or []):
                if work:
                    work_list.append(WorkExperience(**work))

            # 解析项目经验
            project_list = []
            for project in (data.get('project_experience') or []):
                if project:
                    project_list.append(ProjectExperience(**project))

            # 解析技能标签
            skill_list = []
            for skill in (data.get('skills') or []):
                if skill and skill.get('name'):
                    skill_list.append(SkillTag(**skill))

            return ResumeStructuredData(
                basic_info=basic_info,
                education=education_list,
                work_experience=work_list,
                project_experience=project_list,
                skills=skill_list,
            )

        except Exception as e:
            raise ResumeExtractorError(f"数据解析失败: {str(e)}")


# 全局实例
resume_extractor = ResumeExtractor()
