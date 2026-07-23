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

        prompt = f"""你是一位严格且专业的HR面试官，请客观评估以下面试答案。
{context_info}

面试问题：
{question}

应聘者的回答：
{answer}

评分标准（严格执行）：
1. 完整性（30分）：答案是否完整回答了问题的所有方面
2. 准确性（30分）：内容是否准确、无明显错误
3. 逻辑性（20分）：表达是否清晰、逻辑是否连贯
4. 专业性（20分）：是否展现了相关专业知识和经验

评分规则：
- 答案过短（<50字）：0-30分
- 答案简单但基本正确（50-100字）：30-50分
- 答案较完整且正确（100-200字）：50-70分
- 答案完整、准确、有深度（>200字）：70-90分
- 答案优秀、有独特见解：90-100分
- 空答案或完全答非所问：0-10分
- 答案有明显错误：扣10-30分

请按照以下格式输出评估结果：

【评分】
0-100分的评分（纯数字，必须严格按照上述标准）

【总体评价】
用1-2句话概括答案的整体质量（指出具体问题，不要泛泛而谈）

【优点】
- 优点1
- 优点2
（列出2-3个具体优点，如果答案质量差则说明"暂无明显优点"或"仅提供了基本回答"）

【不足】
- 不足1
- 不足2
- 不足3
（列出2-4个具体不足，必须有针对性）

【改进建议】
- 建议1
- 建议2
- 建议3
（给出3-5条具体、可操作的改进建议）

【参考答案】
提供一个高质量的参考答案（200-300字，体现STAR法则）

注意：
1. 评分必须客观严格，不能因为有回答就给高分
2. 对于明显敷衍、过短、答非所问的答案，必须给低分（0-30分）
3. 优缺点和建议要具体、有针对性，避免套话
4. 参考答案要体现专业性和深度
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
