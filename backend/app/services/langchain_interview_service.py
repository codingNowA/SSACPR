"""
基于 LangChain 标准组件的交互式AI面试对话服务
使用课程中讲解的 LangChain 核心功能
"""
import os
import uuid
from typing import Dict, Optional
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.globals import set_debug
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory

# 加载环境变量
load_dotenv()


class LangChainInterviewService:
    """基于 LangChain 标准组件的交互式AI面试服务"""

    def __init__(self):
        # 从环境变量获取LLM配置
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = os.getenv("LLM_MODEL", "qwen-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        # 延迟初始化 LLM (仅在需要时创建)
        self._llm = None

        # 面试会话存储（实际项目中应该用Redis）
        self.sessions: Dict[str, Dict] = {}

        # 对话历史存储
        self.store: Dict[str, InMemoryChatMessageHistory] = {}

        # 系统提示词模板
        self.system_template = """你是一位经验丰富的技术面试官，正在面试一位应聘{job_title}的候选人{candidate_name}。

你的职责：
1. 根据候选人的回答，进行自然的对话式追问
2. 当候选人提到项目经验时，深入询问：
   - 项目背景和规模
   - 你负责的具体模块
   - 使用的技术栈和架构
   - 遇到的技术挑战及解决方案
   - 项目的成果和收获
3. 评估候选人的技术深度和实际经验
4. 在每个回答后，根据情况：
   - 如果回答浅显，追问细节
   - 如果提到项目，深挖项目细节
   - 如果回答完整，询问是否还有补充
5. 当候选人明确表示"没有了"、"回答完了"时，给出本题评价

**重要：当你给出本题评价后，自动提出下一个面试问题**
   - 根据{job_title}岗位要求，选择相关技术问题
   - 考虑候选人之前的回答表现，调整问题难度
   - 常见面试方向：基础知识、项目经验、算法数据结构、系统设计、数据库、网络、框架使用等
   - 提问格式：先简短总结当前问题评价（1-2句），然后自然过渡到下一题

面试风格：
- 友好但专业，像真实面试官
- 循序渐进，从基础到深入
- 鼓励候选人展开说明和举例
- 关注实际应用和问题解决能力
- 对项目经验保持好奇，多追问
- 一次面试涵盖多个技术点，全面评估候选人

评价标准：
- 技术理解深度（30分）
- 实践经验（30分）
- 问题解决能力（20分）
- 表达和沟通（20分）

当需要评价单题时，给出：
1. 本题回答总结
2. 优点（2-3条）
3. 不足（1-2条）
4. 改进建议（1-2条）
5. 评分（0-100分）
6. **然后立即提出下一个问题**

记住：你是面试官，要像真人一样自然对话，不要生硬地列出问题。评价完一题后自动问下一题，不要等候选人输入。"""

    @property
    def llm(self):
        """延迟初始化 LLM"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=self.temperature,
                max_tokens=1000,
                streaming=True  # 启用流式输出
            )
        return self._llm

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """获取会话历史 - 供 RunnableWithMessageHistory 使用"""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def _generate_first_question(self, job_title: str, resume_summary: Optional[str] = None) -> str:
        """
        AI自动生成第一个面试问题

        Args:
            job_title: 目标岗位
            resume_summary: 简历摘要（可选）

        Returns:
            str: 生成的第一个面试问题
        """
        # 构建提示词
        if resume_summary:
            # 如果有简历，生成针对性问题
            prompt = f"""你是一位经验丰富的技术面试官，正在为{job_title}岗位设计第一个面试问题。

候选人简历摘要：
{resume_summary}

请根据候选人的简历和岗位要求，生成一个合适的开场面试问题。要求：
1. 问题应该能让候选人展开介绍自己的优势
2. 可以针对简历中的项目经验或技术栈提问
3. 问题应该开放式，鼓励候选人详细阐述
4. 一句话提问，不要过长

只输出问题本身，不要其他说明。"""
        else:
            # 没有简历，根据岗位生成通用问题
            prompt = f"""你是一位经验丰富的技术面试官，正在为{job_title}岗位设计第一个面试问题。

请生成一个合适的开场面试问题。要求：
1. 问题应该能全面了解候选人的技术背景和项目经验
2. 常见的开场问题如：自我介绍、项目经验介绍、核心技术栈等
3. 问题应该开放式，鼓励候选人详细阐述
4. 根据{job_title}岗位特点选择最合适的切入点

只输出问题本身，不要其他说明。"""

        # 使用LLM生成问题
        try:
            question = self.llm.invoke(prompt).content.strip()
            return question
        except Exception as e:
            # 如果生成失败，返回默认问题
            return f"请先做一下自我介绍，包括你的教育背景、工作经验和在{job_title}方面的技术栈。"

    def _create_conversation_chain(self, job_title: str, candidate_name: str):
        """创建对话链 - 使用标准 LangChain 组件"""
        # 1. 创建提示模板（使用 ChatPromptTemplate 和 MessagesPlaceholder）
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_template.format(
                job_title=job_title,
                candidate_name=candidate_name
            )),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 2. 创建处理链：prompt -> llm -> output_parser
        chain = prompt | self.llm | StrOutputParser()

        # 3. 使用 RunnableWithMessageHistory 包装链，添加历史记忆
        chain_with_history = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return chain_with_history

    def start_session(
        self,
        job_title: str,
        initial_question: Optional[str] = None,
        candidate_name: Optional[str] = None,
        resume_summary: Optional[str] = None
    ) -> Dict:
        """
        开始面试会话

        Args:
            job_title: 目标岗位
            initial_question: 第一个面试题（可选，不提供则AI自动生成）
            candidate_name: 候选人姓名
            resume_summary: 简历摘要（可选，未来用于生成针对性问题）

        Returns:
            Dict: 会话信息和开场白
        """
        # 生成会话ID
        session_id = f"interview_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

        candidate_name = candidate_name or "候选人"

        # 如果没有提供第一个问题，让AI根据岗位生成
        if not initial_question:
            initial_question = self._generate_first_question(job_title, resume_summary)

        # 创建对话链
        conversation_chain = self._create_conversation_chain(job_title, candidate_name)

        # 保存会话
        self.sessions[session_id] = {
            "job_title": job_title,
            "candidate_name": candidate_name,
            "current_question": initial_question,
            "conversation_chain": conversation_chain,
            "question_count": 1,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "questions_asked": [initial_question],
            "resume_summary": resume_summary  # 保存简历摘要供后续参考
        }

        # 构造开场白
        name_part = f"{candidate_name}！" if candidate_name != "候选人" else "！"
        greeting = f"你好{name_part}欢迎参加{job_title}的技术面试。"
        opening = (
            f"{greeting}\n\n"
            f"我会问你一些技术问题，请你自由地阐述你的理解和经验。"
            f"特别是如果你提到相关项目经验，我会很感兴趣地深入了解。"
            f"准备好了吗？\n\n"
            f"**第一个问题**：{initial_question}"
        )

        return {
            "success": True,
            "session_id": session_id,
            "interviewer_message": opening,
            "question_number": 1,
            "response_type": "question"
        }

    async def continue_conversation(
        self,
        session_id: str,
        candidate_answer: str
    ) -> Dict:
        """
        继续对话

        Args:
            session_id: 会话ID
            candidate_answer: 候选人的回答

        Returns:
            Dict: 面试官的回应
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        session = self.sessions[session_id]
        conversation_chain = session["conversation_chain"]

        try:
            # 使用 RunnableWithMessageHistory 调用对话链
            interviewer_message = await conversation_chain.ainvoke(
                {"input": candidate_answer},
                config={"configurable": {"session_id": session_id}}
            )

            # 分析回应类型
            response_type = self._analyze_response_type(interviewer_message)

            # 计算对话轮次
            history = self.store.get(session_id)
            conversation_turn = len(history.messages) // 2 if history else 0

            return {
                "success": True,
                "session_id": session_id,
                "interviewer_message": interviewer_message,
                "response_type": response_type,
                "conversation_turn": conversation_turn
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"对话生成失败: {str(e)}"
            }

    def _analyze_response_type(self, response: str) -> str:
        """分析面试官回应的类型"""
        response_lower = response.lower()

        # 判断是否是评价总结
        evaluation_keywords = ["评分", "总结", "整体来说", "总体", "优点", "不足", "改进建议", "本题", "回答质量"]
        if any(keyword in response for keyword in evaluation_keywords):
            if "分" in response or "score" in response_lower:
                return "evaluation"

        # 判断是否是项目深挖
        project_keywords = ["项目", "负责", "模块", "技术栈", "架构", "挑战", "如何解决", "具体", "详细"]
        if any(keyword in response for keyword in project_keywords):
            return "project_deep_dive"

        # 判断是否是追问
        followup_keywords = ["能详细", "能展开", "具体是", "比如", "举例", "为什么", "怎么", "如何"]
        if any(keyword in response for keyword in followup_keywords):
            return "follow_up"

        # 判断是否询问补充
        more_keywords = ["还有", "补充", "想说", "其他", "还想"]
        if any(keyword in response for keyword in more_keywords):
            return "ask_for_more"

        return "follow_up"

    async def next_question(
        self,
        session_id: str,
        next_question: str
    ) -> Dict:
        """
        开始下一个问题

        Args:
            session_id: 会话ID
            next_question: 下一个问题

        Returns:
            Dict: 面试官提出新问题
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        session = self.sessions[session_id]

        session["question_count"] += 1
        session["current_question"] = next_question
        session["questions_asked"].append(next_question)

        # 构建过渡消息
        interviewer_message = f"好的，我们来看下一个问题。\n\n**第{session['question_count']}题**：{next_question}"

        # 将新问题添加到历史记录
        history = self._get_session_history(session_id)
        history.add_ai_message(interviewer_message)

        return {
            "success": True,
            "session_id": session_id,
            "interviewer_message": interviewer_message,
            "question_number": session["question_count"],
            "response_type": "question"
        }

    async def end_session(self, session_id: str) -> Dict:
        """
        结束面试会话

        Args:
            session_id: 会话ID

        Returns:
            Dict: 面试总结
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        session = self.sessions[session_id]
        conversation_chain = session["conversation_chain"]

        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()

        # 生成面试总结
        summary_prompt = """
面试即将结束，请基于整场面试对话，生成一份完整的面试评估报告：

## 整体评价
[优秀/良好/一般/需改进]

## 总体得分
[0-100分]

## 各问题表现总结
[简要总结每个问题的回答质量]

## 优点（3-5条）
-
-

## 不足（3-5条）
-
-

## 改进建议（3-5条）
-
-

## 录用建议
[是否推荐录用及理由]

请以结构化的Markdown格式输出。
"""

        try:
            summary = await conversation_chain.ainvoke(
                {"input": summary_prompt},
                config={"configurable": {"session_id": session_id}}
            )

            return {
                "success": True,
                "session_id": session_id,
                "interview_summary": summary,
                "total_questions": session["question_count"],
                "duration_minutes": self._calculate_duration(session),
                "questions_asked": session["questions_asked"]
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"生成总结失败: {str(e)}"
            }

    def _calculate_duration(self, session: Dict) -> int:
        """计算面试时长（分钟）"""
        start = datetime.fromisoformat(session["start_time"])
        end = datetime.fromisoformat(session.get("end_time", datetime.now().isoformat()))
        return int((end - start).total_seconds() / 60)

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # 获取对话历史
        history = self._get_session_history(session_id)
        conversation_history = []

        for i, msg in enumerate(history.messages):
            role = "assistant" if i % 2 == 0 else "user"
            conversation_history.append({
                "role": role,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })

        return {
            "session_id": session_id,
            "job_title": session["job_title"],
            "candidate_name": session["candidate_name"],
            "question_count": session["question_count"],
            "status": session["status"],
            "start_time": session["start_time"],
            "conversation_history": conversation_history
        }

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.store:
            del self.store[session_id]
        return True


# 创建全局实例
langchain_interview_service = LangChainInterviewService()
