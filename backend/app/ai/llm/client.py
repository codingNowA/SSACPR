from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

import httpx
from config.settings import LLMSettings, get_llm_settings


@dataclass(frozen=True)
class ChatMessage:
	role: str
	content: str


@dataclass(frozen=True)
class LLMResult:
	content: str
	model: str
	raw: Dict[str, Any]


class LLMClientError(RuntimeError):
	pass


class LLMClient:
	def __init__(self, settings: Optional[LLMSettings] = None) -> None:
		self.settings = settings or get_llm_settings()

	def build_messages(
		self,
		user_prompt: str,
		system_prompt: Optional[str] = None,
		history: Optional[List[ChatMessage]] = None,
	) -> List[Dict[str, str]]:
		messages: List[Dict[str, str]] = []
		if system_prompt:
			messages.append({"role": "system", "content": system_prompt})
		if history:
			messages.extend({"role": item.role, "content": item.content} for item in history)
		messages.append({"role": "user", "content": user_prompt})
		return messages

	async def chat(
		self,
		user_prompt: str,
		system_prompt: Optional[str] = None,
		history: Optional[List[ChatMessage]] = None,
		temperature: Optional[float] = None,
		model: Optional[str] = None,
		extra_payload: Optional[Mapping[str, Any]] = None,
	) -> LLMResult:
		if self.settings.dry_run:
			return self._dry_run_result(user_prompt=user_prompt, system_prompt=system_prompt, model=model)

		if not self.settings.base_url or not self.settings.api_key:
			raise LLMClientError("LLM 配置不完整，请检查 LLM_BASE_URL 和 LLM_API_KEY")

		payload: Dict[str, Any] = {
			"model": model or self.settings.model,
			"messages": self.build_messages(user_prompt, system_prompt, history),
			"temperature": temperature if temperature is not None else self.settings.temperature,
		}
		if extra_payload:
			payload.update(dict(extra_payload))

		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.settings.api_key}",
		}

		try:
			async with httpx.AsyncClient(timeout=self.settings.timeout) as client:
				response = await client.post(
					self._normalize_url(self.settings.base_url),
					json=payload,
					headers=headers,
				)
				response.raise_for_status()
				raw = response.json()
		except httpx.HTTPStatusError as exc:
			raise LLMClientError(f"LLM 调用失败 (HTTP {exc.response.status_code}): {exc.response.text}") from exc
		except httpx.RequestError as exc:
			raise LLMClientError(f"LLM 调用失败: {exc}") from exc

		content = self._extract_content(raw)
		return LLMResult(content=content, model=payload["model"], raw=raw)

	async def generate_text(
		self,
		prompt: str,
		system_prompt: Optional[str] = None,
		**kwargs: Any,
	) -> str:
		result = await self.chat(prompt, system_prompt=system_prompt, **kwargs)
		return result.content

	async def chat_json(
		self,
		user_prompt: str,
		system_prompt: Optional[str] = None,
		**kwargs: Any,
	) -> Dict[str, Any]:
		result = await self.chat(user_prompt, system_prompt=system_prompt, **kwargs)
		try:
			return json.loads(result.content)
		except json.JSONDecodeError as exc:
			raise LLMClientError("LLM 返回内容不是合法 JSON") from exc

	def _normalize_url(self, base_url: str) -> str:
		normalized = base_url.rstrip("/")
		if normalized.endswith("/chat/completions"):
			return normalized
		return f"{normalized}/v1/chat/completions"

	def _extract_content(self, raw: Mapping[str, Any]) -> str:
		choices = raw.get("choices") or []
		if not choices:
			return ""
		message = choices[0].get("message") or {}
		return str(message.get("content", ""))

	def _dry_run_result(
		self,
		user_prompt: str,
		system_prompt: Optional[str],
		model: Optional[str],
	) -> LLMResult:
		content = "\n".join(
			[
				"[DRY_RUN] LLM 调用已拦截",
				f"model={model or self.settings.model}",
				f"system_prompt={system_prompt or ''}",
				f"user_prompt={user_prompt}",
			]
		)
		return LLMResult(content=content, model=model or self.settings.model, raw={"dry_run": True})


default_llm_client = LLMClient()
