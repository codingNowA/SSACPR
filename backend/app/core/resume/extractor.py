"""
简历结构化提取器
使用 LLM 从简历文本中提取结构化信息
"""
import json
import re
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

重要提取规则：
1. **姓名**：仔细识别完整的中文姓名（2-4个字），如果原文姓名被识别错误（如"李 ie"、"王 abc"），请根据常见中文名推断正确姓名。常见名字：辰、明、华、伟、强、磊、娜、丽、芳等
2. **邮箱**：必须包含完整的 @ 和域名（必须有点号），格式如：example@gmail.com、user@company.com.cn
3. **电话**：保持原始格式，如：138-1234-5678 或 13812345678
4. **项目经历**：详细提取所有项目信息，包括：
   - 项目名称必须完整
   - 项目描述必须包含所有要点（使用的技术、实现的功能、技术细节等）
   - tech_stack 必须提取所有提到的技术栈
   - achievements 必须提取所有成果和数据指标（如性能提升、响应时间等）
5. 如果某个字段在简历中找不到，设置为 null
6. 数组字段如果为空，返回空数组 []
7. 工作经历包含全职工作和实习
8. 时间格式尽量统一为 YYYY-MM 或 YYYY.MM
9. 从简历中提取所有技能，并分类整理

常见错误避免：
- ❌ 姓名识别错误："李 ie" → ✅ 应该是 "李辰" 或其他常见中文名
- ❌ 邮箱缺少点号："lichen@emailcom" → ✅ "lichen@email.com"
- ❌ 项目描述过于简略 → ✅ 必须包含所有技术细节和实现要点
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
            # 清理和验证提取的数据
            result = self._clean_extracted_data(result)
            return result
        except Exception as e:
            raise ResumeExtractorError(f"LLM 提取失败: {str(e)}")

    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理和修复提取的数据中的常见错误

        Args:
            data: LLM 提取的原始数据

        Returns:
            清理后的数据
        """
        if not data:
            return data

        # 修复基本信息
        if 'basic_info' in data and data['basic_info']:
            basic = data['basic_info']

            # 修复姓名：去除多余空格和非中文字符
            if basic.get('name'):
                name = basic['name'].strip()
                # 移除姓名中的英文字母、数字和特殊符号，保留中文、空格和常见分隔符
                name = re.sub(r'[a-zA-Z0-9]+', '', name)
                name = re.sub(r'\s+', '', name)  # 移除所有空格
                basic['name'] = name if len(name) >= 2 else basic['name']

            # 修复邮箱：确保 @ 后有点号
            if basic.get('email'):
                email = basic['email'].strip()
                # 检查邮箱格式：必须包含 @ 和点号
                if '@' in email:
                    local, domain = email.split('@', 1)
                    # 如果域名中没有点号，尝试修复常见错误
                    if '.' not in domain:
                        # 常见错误：gmailcom -> gmail.com, emailcom -> email.com
                        common_domains = {
                            'gmailcom': 'gmail.com',
                            'emailcom': 'email.com',
                            'qqcom': 'qq.com',
                            '163com': '163.com',
                            '126com': '126.com',
                            'outlookcom': 'outlook.com',
                            'hotmailcom': 'hotmail.com',
                        }
                        domain_lower = domain.lower()
                        if domain_lower in common_domains:
                            domain = common_domains[domain_lower]
                            email = f"{local}@{domain}"
                basic['email'] = email

        # 修复项目经历中的常见 OCR 错误
        if 'project_experience' in data and data['project_experience']:
            for project in data['project_experience']:
                if not project:
                    continue

                # 修复项目描述中的 "JEF" → "基于"
                if project.get('description'):
                    desc = project['description']
                    # 替换常见的 OCR 错误："JEF" 或 "J$F" 或 "JtF" → "基于"
                    desc = re.sub(r'\bJEF\b', '基于', desc)
                    desc = re.sub(r'\bJ\$F\b', '基于', desc)
                    desc = re.sub(r'\bJtF\b', '基于', desc)
                    desc = re.sub(r'\bJ&F\b', '基于', desc)
                    project['description'] = desc

        return data

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
