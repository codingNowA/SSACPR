"""
面试考试评分服务
"""
import logging
from typing import List, Dict, Any
from app.ai.llm.client import default_llm_client

logger = logging.getLogger(__name__)


class InterviewExamService:
    """面试考试评分服务"""

    async def evaluate_exam(
        self,
        answers: List[Dict[str, Any]],
        total_time: int,
    ) -> Dict[str, Any]:
        """
        评估整个考试

        Args:
            answers: 答案列表，每个包含 question_id, question, answer, time_spent
            total_time: 总用时（秒）

        Returns:
            评分结果，包含总分、各题得分、参考答案、建议等
        """
        num_questions = len(answers)
        avg_time = total_time / num_questions if num_questions > 0 else 0

        # 评估每道题
        answer_evaluations = []
        total_content_score = 0

        for i, ans in enumerate(answers):
            evaluation = await self._evaluate_single_answer(
                question=ans["question"],
                answer=ans["answer"],
                time_spent=ans["time_spent"],
            )
            answer_evaluations.append(evaluation)
            total_content_score += evaluation["score"]

        # 计算平均内容得分
        content_score = total_content_score / num_questions if num_questions > 0 else 0

        # 计算时间得分（基于答题速度）
        time_score = self._calculate_time_score(avg_time, num_questions)

        # 综合得分（内容70%，时间30%）
        total_score = round(content_score * 0.7 + time_score * 0.3, 1)

        # 生成总体评价和建议
        summary, suggestions = await self._generate_summary_and_suggestions(
            total_score=total_score,
            content_score=content_score,
            time_score=time_score,
            avg_time=avg_time,
            num_questions=num_questions,
        )

        return {
            "total_score": total_score,
            "content_score": round(content_score, 1),
            "time_score": round(time_score, 1),
            "avg_time": round(avg_time, 1),
            "total_time": total_time,
            "summary": summary,
            "suggestions": suggestions,
            "answers": answer_evaluations,
        }

    async def _evaluate_single_answer(
        self,
        question: str,
        answer: str,
        time_spent: int,
    ) -> Dict[str, Any]:
        """评估单个答案"""
        prompt = f"""请评估以下面试题的回答质量（0-100分）：

问题：{question}

考生回答：{answer}

答题用时：{time_spent}秒

请提供：
1. 得分（0-100）
2. 参考答案（简洁专业，200字以内）
3. 反馈（指出回答的优缺点，100字以内）

以JSON格式返回：
{{
    "score": 85,
    "reference_answer": "参考答案内容...",
    "feedback": "反馈内容..."
}}"""

        try:
            response = await default_llm_client.chat(
                user_prompt=prompt,
                temperature=0.3,
            )

            # 解析响应
            import json
            import re

            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "question": question,
                    "user_answer": answer,
                    "score": result.get("score", 60),
                    "reference_answer": result.get("reference_answer", "参考答案生成失败"),
                    "feedback": result.get("feedback", ""),
                }

        except Exception as e:
            logger.error(f"评估答案失败: {e}")

        # 失败时返回默认值
        return {
            "question": question,
            "user_answer": answer,
            "score": 60,
            "reference_answer": "参考答案生成失败，请联系管理员。",
            "feedback": "评估失败",
        }

    def _calculate_time_score(self, avg_time: float, num_questions: int) -> float:
        """
        计算时间得分

        策略：
        - 最佳答题时间：60-120秒/题
        - 过快（<30秒）：可能思考不充分
        - 过慢（>180秒）：可能思路不清晰
        """
        if avg_time < 30:
            # 过快
            return 60.0
        elif avg_time <= 60:
            # 偏快，但可接受
            return 70.0 + (avg_time - 30) / 30 * 10
        elif avg_time <= 120:
            # 理想范围
            return 90.0
        elif avg_time <= 180:
            # 偏慢
            return 90.0 - (avg_time - 120) / 60 * 20
        else:
            # 过慢
            return max(50.0, 70.0 - (avg_time - 180) / 60 * 10)

    async def _generate_summary_and_suggestions(
        self,
        total_score: float,
        content_score: float,
        time_score: float,
        avg_time: float,
        num_questions: int,
    ) -> tuple:
        """生成总体评价和建议"""
        prompt = f"""请对以下面试考试结果进行总结和建议：

综合得分：{total_score}
内容得分：{content_score}
时间得分：{time_score}
平均答题时间：{avg_time:.1f}秒/题
题目数量：{num_questions}

请提供：
1. 总体评价（100字以内，客观评价表现）
2. 3-5条改进建议（每条30字以内）

以JSON格式返回：
{{
    "summary": "总体评价...",
    "suggestions": ["建议1", "建议2", "建议3"]
}}"""

        try:
            response = await default_llm_client.chat(
                user_prompt=prompt,
                temperature=0.3,
            )

            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return (
                    result.get("summary", "表现良好，继续保持。"),
                    result.get("suggestions", ["多练习", "注意答题时间"])
                )

        except Exception as e:
            logger.error(f"生成总结失败: {e}")

        # 默认返回
        if total_score >= 85:
            summary = "表现优秀！答题内容充实，逻辑清晰，时间把控得当。"
            suggestions = ["继续保持", "可尝试更深入的思考", "注意细节完善"]
        elif total_score >= 70:
            summary = "表现良好，答题基本准确，但仍有提升空间。"
            suggestions = ["加强专业知识积累", "提高答题速度", "注意要点覆盖"]
        elif total_score >= 60:
            summary = "表现一般，部分问题回答不够充分。"
            suggestions = ["系统学习相关知识", "多做练习", "提升答题技巧", "合理分配时间"]
        else:
            summary = "需要加强，建议系统性复习相关知识。"
            suggestions = ["系统学习基础知识", "多做模拟练习", "寻求专业指导", "制定学习计划"]

        return summary, suggestions


# 单例
interview_exam_service = InterviewExamService()
