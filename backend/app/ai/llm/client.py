from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

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

	def chat(
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

		request = urllib.request.Request(
			self._normalize_url(self.settings.base_url),
			data=json.dumps(payload).encode("utf-8"),
			headers={
				"Content-Type": "application/json",
				"Authorization": f"Bearer {self.settings.api_key}",
			},
			method="POST",
		)

		try:
			with urllib.request.urlopen(request, timeout=self.settings.timeout) as response:
				body = response.read().decode("utf-8")
		except urllib.error.URLError as exc:
			raise LLMClientError(f"LLM 调用失败: {exc}") from exc

		raw = json.loads(body)
		content = self._extract_content(raw)
		return LLMResult(content=content, model=payload["model"], raw=raw)

	def generate_text(
		self,
		prompt: str,
		system_prompt: Optional[str] = None,
		**kwargs: Any,
	) -> str:
		return self.chat(prompt, system_prompt=system_prompt, **kwargs).content

	def chat_json(
		self,
		user_prompt: str,
		system_prompt: Optional[str] = None,
		**kwargs: Any,
	) -> Dict[str, Any]:
		result = self.chat(user_prompt, system_prompt=system_prompt, **kwargs)
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
