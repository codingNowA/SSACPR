from typing import Any, Dict, List, Optional

from .client import ChatMessage, LLMClient, LLMResult, default_llm_client


class LLMService:
	def __init__(self, client: Optional[LLMClient] = None) -> None:
		self.client = client or default_llm_client

	async def chat(
		self,
		prompt: str,
		system_prompt: Optional[str] = None,
		history: Optional[List[ChatMessage]] = None,
		**kwargs: Any,
	) -> LLMResult:
		return await self.client.chat(
			user_prompt=prompt,
			system_prompt=system_prompt,
			history=history,
			**kwargs,
		)

	async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
		return await self.client.generate_text(prompt=prompt, system_prompt=system_prompt, **kwargs)

	async def chat_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
		return await self.client.chat_json(user_prompt=prompt, system_prompt=system_prompt, **kwargs)


llm_service = LLMService()
