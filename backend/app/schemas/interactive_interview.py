"""
交互式AI面试对话数据模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StartInterviewRequest(BaseModel):
    """开始面试请求"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_title": "Java后端开发工程师",
            "candidate_name": "张三"
        }
    })

    job_title: str = Field(..., description="目标岗位")
    initial_question: Optional[str] = Field(default=None, description="第一个面试题（可选，不提供则AI自动生成）")
    candidate_name: Optional[str] = Field(default=None, description="候选人姓名（可选）")
    resume_summary: Optional[str] = Field(default=None, description="简历摘要（可选，用于生成针对性问题）")


class StartInterviewResponse(BaseModel):
    """开始面试响应"""
    success: bool = Field(..., description="是否成功")
    session_id: str = Field(..., description="面试会话ID")
    interviewer_message: str = Field(..., description="面试官的开场白和第一个问题")
    question_number: int = Field(..., description="当前问题编号")
    response_type: str = Field(..., description="回应类型")
    message: Optional[str] = Field(default=None, description="错误消息")


class ContinueConversationRequest(BaseModel):
    """继续对话请求"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "interview_20240715_abc123",
            "candidate_answer": "我是张三，毕业于XX大学计算机专业，有3年Java开发经验。主要做过电商系统和支付系统的开发，熟悉Spring Boot、MySQL、Redis等技术。在电商项目中，我负责订单模块和库存模块的开发..."
        }
    })

    session_id: str = Field(..., description="面试会话ID")
    candidate_answer: str = Field(..., description="候选人的回答", min_length=5)


class ContinueConversationResponse(BaseModel):
    """继续对话响应"""
    success: bool = Field(..., description="是否成功")
    session_id: str = Field(..., description="面试会话ID")
    interviewer_message: str = Field(..., description="面试官的回应")
    response_type: str = Field(..., description="回应类型：question(新问题)、follow_up(追问)、project_deep_dive(项目深挖)、ask_for_more(询问补充)、evaluation(评价)")
    conversation_turn: int = Field(..., description="对话轮次")
    message: Optional[str] = Field(default=None, description="错误消息")


class NextQuestionRequest(BaseModel):
    """下一个问题请求"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "interview_20240715_abc123",
            "next_question": "请介绍一下Java中的集合框架，以及常用集合类的特点"
        }
    })

    session_id: str = Field(..., description="面试会话ID")
    next_question: str = Field(..., description="下一个面试题")


class NextQuestionResponse(BaseModel):
    """下一个问题响应"""
    success: bool = Field(..., description="是否成功")
    session_id: str = Field(..., description="面试会话ID")
    interviewer_message: str = Field(..., description="面试官提出新问题")
    question_number: int = Field(..., description="当前问题编号")
    response_type: str = Field(..., description="回应类型")
    message: Optional[str] = Field(default=None, description="错误消息")


class EndInterviewRequest(BaseModel):
    """结束面试请求"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "session_id": "interview_20240715_abc123"
        }
    })

    session_id: str = Field(..., description="面试会话ID")


class EndInterviewResponse(BaseModel):
    """结束面试响应"""
    success: bool = Field(..., description="是否成功")
    session_id: str = Field(..., description="面试会话ID")
    interview_summary: str = Field(..., description="面试总结评价（Markdown格式）")
    total_questions: int = Field(..., description="总问题数")
    duration_minutes: int = Field(..., description="面试时长（分钟）")
    questions_asked: List[str] = Field(default_factory=list, description="提问过的问题列表")
    message: Optional[str] = Field(default=None, description="错误消息")


class ConversationHistory(BaseModel):
    """对话历史"""
    role: str = Field(..., description="角色：user(候选人)或assistant(面试官)")
    content: str = Field(..., description="对话内容")
    timestamp: str = Field(..., description="时间戳")


class SessionInfoResponse(BaseModel):
    """会话信息响应"""
    success: bool = Field(..., description="是否成功")
    session_id: str = Field(..., description="面试会话ID")
    job_title: str = Field(..., description="目标岗位")
    candidate_name: str = Field(..., description="候选人姓名")
    question_count: int = Field(..., description="已提问数量")
    status: str = Field(..., description="会话状态：active(进行中)或completed(已完成)")
    start_time: str = Field(..., description="开始时间")
    conversation_history: List[ConversationHistory] = Field(default_factory=list, description="对话历史")
    message: Optional[str] = Field(default=None, description="错误消息")
