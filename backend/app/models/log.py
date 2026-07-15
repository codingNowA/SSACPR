"""
日志查询数据模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# ==================== 响应模型 ====================
class LogResponse(BaseModel):
    """日志响应"""
    id: int
    user_id: Optional[int]
    action: Optional[str]
    module: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """日志列表响应"""
    items: List[LogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int