"""
面试模拟问答服务

使用LLM对用户的面试答案进行评估和反馈
"""
import logging
from typing import Dict, Any, Optional
from app.ai.llm.client import default_llm_client, LLMClientError

logger = logging.getLogger(__name__)


class InterviewMockService:
    """面试模拟问答服务"""

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_context: Optional[Dict[str, Any]] = None,
        resume_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        评估面试答案

        Args:
            question: 面试问题
            answer: 用户的答案
            job_context: 岗位上下文（可选）
            resume_context: 简历上下文（可选）

        Returns:
            评估结果，包括评分、优缺点、改进建议
        """
        # 构建评估提示词
        prompt = self._build_evaluation_prompt(
            question, answer, job_context, resume_context
        )

        try:
            # 调用LLM进行评估
            response = await default_llm_client.chat(
                user_prompt=prompt,
                temperature=0.3,
            )

            # 解析LLM响应
            feedback = self._parse_llm_response(response.content)

            return feedback

        except LLMClientError as e:
            logger.error(f"LLM评估失败: {e}")
            return self._get_default_feedback()
        except Exception as e:
            logger.error(f"评估答案失败: {e}")
            # 返回默认反馈
            return self._get_default_feedback()

    def _build_evaluation_prompt(
        self,
        question: str,
        answer: str,
        job_context: Optional[Dict[str, Any]],
        resume_context: Optional[Dict[str, Any]],
    ) -> str:
        """构建评估提示词"""
        context_info = ""

        if job_context:
            context_info += f"\n岗位信息：{job_context.get('title', '')}"
            if job_context.get('company'):
                context_info += f" @ {job_context['company']}"

        if resume_context:
            basic_info = resume_context.get('parsed_data', {}).get('basic_info', {})
            if basic_info.get('name'):
                context_info += f"\n应聘者：{basic_info['name']}"

        prompt = f"""你是一位资深的HR面试官，请评估以下面试答案。
{context_info}

面试问题：
{question}

应聘者的回答：
{answer}

请按照以下格式输出评估结果：

【评分】
0-100分的评分（纯数字）

【总体评价】
用1-2句话概括答案的整体质量

【优点】
- 优点1
- 优点2
（列出2-3个优点，如果没有明显优点则说明）

【不足】
- 不足1
- 不足2
（列出2-3个不足，如果没有明显不足则说明）

【改进建议】
- 建议1
- 建议2
- 建议3
（给出3-5条具体的改进建议）

【参考答案】
提供一个更好的参考答案（150-200字）

注意：
1. 评分要客观公正，考虑答案的完整性、逻辑性、专业性
2. 优缺点要具体、有针对性
3. 改进建议要可操作、有帮助
4. 参考答案要体现STAR法则（Situation情境、Task任务、Action行动、Result结果）
"""
        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        lines = response.strip().split('\n')

        # 初始化结果
        result = {
            "score": 70,
            "overall_assessment": "",
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "sample_answer": "",
        }

        current_section = None
        current_list = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别章节
            if "【评分】" in line:
                current_section = "score"
                continue
            elif "【总体评价】" in line:
                current_section = "overall"
                continue
            elif "【优点】" in line:
                current_section = "strengths"
                current_list = []
                continue
            elif "【不足】" in line:
                if current_list and current_section == "strengths":
                    result["strengths"] = current_list
                current_section = "weaknesses"
                current_list = []
                continue
            elif "【改进建议】" in line:
                if current_list and current_section == "weaknesses":
                    result["weaknesses"] = current_list
                current_section = "suggestions"
                current_list = []
                continue
            elif "【参考答案】" in line:
                if current_list and current_section == "suggestions":
                    result["suggestions"] = current_list
                current_section = "sample"
                continue

            # 解析内容
            if current_section == "score":
                # 提取数字
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = int(numbers[0])
                    result["score"] = max(0, min(100, score))
            elif current_section == "overall":
                if result["overall_assessment"]:
                    result["overall_assessment"] += " " + line
                else:
                    result["overall_assessment"] = line
            elif current_section in ["strengths", "weaknesses", "suggestions"]:
                # 列表项
                if line.startswith('-') or line.startswith('•'):
                    item = line.lstrip('-•').strip()
                    if item:
                        current_list.append(item)
                elif line and current_list:  # 多行内容
                    current_list[-1] += " " + line
            elif current_section == "sample":
                if result["sample_answer"]:
                    result["sample_answer"] += "\n" + line
                else:
                    result["sample_answer"] = line

        # 保存最后一个列表
        if current_list:
            if current_section == "strengths":
                result["strengths"] = current_list
            elif current_section == "weaknesses":
                result["weaknesses"] = current_list
            elif current_section == "suggestions":
                result["suggestions"] = current_list

        # 验证和清理
        if not result["overall_assessment"]:
            result["overall_assessment"] = "答案基本合理，但仍有改进空间。"

        if not result["strengths"]:
            result["strengths"] = ["已尝试回答问题"]

        if not result["weaknesses"]:
            result["weaknesses"] = ["回答可以更具体和详细"]

        if not result["suggestions"]:
            result["suggestions"] = [
                "增加具体的案例和数据支持",
                "使用STAR法则组织答案",
                "注意逻辑清晰，重点突出"
            ]

        return result

    def _get_default_feedback(self) -> Dict[str, Any]:
        """获取默认反馈（LLM调用失败时使用）"""
        return {
            "score": 60,
            "overall_assessment": "系统暂时无法评估，请稍后重试。",
            "strengths": ["已提供答案"],
            "weaknesses": ["无法自动评估"],
            "suggestions": [
                "建议寻求专业人士的反馈",
                "参考经典面试题目的回答方式",
                "多做模拟练习"
            ],
            "sample_answer": "暂无参考答案",
        }


# 单例
interview_mock_service = InterviewMockService()
