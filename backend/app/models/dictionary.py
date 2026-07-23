"""
词库与权重配置数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 请求模型 ====================
class DictionaryCreate(BaseModel):
    """创建词条请求"""
    word: str = Field(..., max_length=100, description="词条名称")
    type: str = Field(..., max_length=50, description="类型: skill/industry/soft_skill")
    weight: float = Field(0.5, ge=0, le=1, description="权重 (0-1)")
    description: Optional[str] = Field(None, description="描述")


class DictionaryUpdate(BaseModel):
    """更新词条请求（全部可选）"""
    word: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0, le=1)
    description: Optional[str] = None


# ==================== 响应模型 ====================
class DictionaryResponse(BaseModel):
    """词条响应"""
    id: int
    word: str
    type: str
    weight: float
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DictionaryListResponse(BaseModel):
    """词条列表响应"""
    items: List[DictionaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int