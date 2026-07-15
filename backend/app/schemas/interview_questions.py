"""
面试题推荐相关的数据模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class InterviewQuestion(BaseModel):
    """单个面试题"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "question": "请介绍一下Java中的集合框架",
            "category": "基础知识",
            "difficulty": "中等",
            "key_points": [
                "Collection和Map两大接口体系",
                "List、Set、Queue的特点和使用场景",
                "ArrayList vs LinkedList性能对比",
                "HashMap底层实现原理"
            ],
            "tags": ["Java", "集合框架", "数据结构"]
        }
    })

    question: str = Field(..., description="面试题内容")
    category: str = Field(..., description="题目分类（如：基础知识、项目经验、算法题等）")
    difficulty: str = Field(..., description="难度等级（简单、中等、困难）")
    key_points: List[str] = Field(default_factory=list, description="参考答案要点")
    tags: List[str] = Field(default_factory=list, description="相关技术标签")


class InterviewQuestionsRecommendation(BaseModel):
    """面试题推荐结果"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_title": "Java后端开发工程师",
            "total_questions": 15,
            "questions_by_category": {
                "基础知识": 5,
                "项目经验": 4,
                "算法与数据结构": 3,
                "系统设计": 3
            },
            "questions": []
        }
    })

    job_title: Optional[str] = Field(default=None, description="目标岗位")
    total_questions: int = Field(..., description="推荐题目总数")
    questions_by_category: dict = Field(default_factory=dict, description="按分类统计的题目数量")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="推荐的面试题列表")


class InterviewQuestionsRequest(BaseModel):
    """面试题推荐请求"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_text": "岗位：Java后端开发工程师\n要求：\n1. 熟练掌握Java、Spring Boot\n2. 熟悉MySQL、Redis\n3. 了解微服务架构",
            "max_questions": 15
        }
    })

    job_text: str = Field(..., description="岗位描述文本", min_length=10)
    max_questions: int = Field(default=15, description="最多推荐题目数量", ge=5, le=50)


class InterviewQuestionsResponse(BaseModel):
    """面试题推荐响应"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "recommendation": {},
            "message": "成功推荐15道面试题"
        }
    })

    success: bool = Field(..., description="推荐是否成功")
    recommendation: InterviewQuestionsRecommendation = Field(..., description="推荐结果")
    message: str = Field(..., description="响应消息")
