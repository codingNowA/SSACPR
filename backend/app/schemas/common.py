from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
	code: int = Field(default=200, description="业务状态码")
	message: str = Field(default="success", description="响应消息")
	data: Optional[T] = Field(default=None, description="响应数据")
	timestamp: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		description="响应时间戳",
	)

	@classmethod
	def success(
		cls,
		data: Optional[T] = None,
		message: str = "success",
		code: int = 200,
	) -> "ApiResponse[T]":
		return cls(code=code, message=message, data=data)

	@classmethod
	def error(
		cls,
		message: str = "error",
		code: int = 400,
		data: Optional[T] = None,
	) -> "ApiResponse[T]":
		return cls(code=code, message=message, data=data)


Response = ApiResponse
