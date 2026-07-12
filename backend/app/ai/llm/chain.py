from typing import Any, Dict, List, Optional

from .client import ChatMessage, LLMClient, LLMResult, default_llm_client


class LLMService:
	def __init__(self, client: Optional[LLMClient] = None) -> None:
		self.client = client or default_llm_client

	def chat(
		self,
		prompt: str,
		system_prompt: Optional[str] = None,
		history: Optional[List[ChatMessage]] = None,
		**kwargs: Any,
	) -> LLMResult:
		return self.client.chat(
			user_prompt=prompt,
			system_prompt=system_prompt,
			history=history,
			**kwargs,
		)

	def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
		return self.client.generate_text(prompt=prompt, system_prompt=system_prompt, **kwargs)

	def chat_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
		return self.client.chat_json(user_prompt=prompt, system_prompt=system_prompt, **kwargs)


llm_service = LLMService()
