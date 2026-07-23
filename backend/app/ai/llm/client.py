"""
LLM 客户端封装 - 兼容 OpenAI API 格式
修复: _normalize_url 不再重复追加 /v1 前缀
安全: 日志中不输出 API Key 等敏感信息
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

import httpx
from config.settings import LLMSettings, get_llm_settings

logger = logging.getLogger(__name__)


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

        # 日志仅记录模型名称，不记录请求体（可能含敏感内容）和 API Key
        logger.debug("LLM request: model=%s", payload["model"])

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.timeout,
                verify=self.settings.verify_ssl,  # 从配置读取 SSL 验证选项
                follow_redirects=False,  # 禁用重定向以降低 SSRF 风险
            ) as client:
                response = await client.post(
                    self._normalize_url(self.settings.base_url),
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                try:
                    raw = response.json()
                except (json.JSONDecodeError, ValueError) as exc:
                    logger.error("LLM response is not valid JSON")
                    raise LLMClientError("LLM 返回内容不是合法的 JSON 响应") from exc
        except httpx.HTTPStatusError as exc:
            # 错误日志不包含 response 完整内容（可能含 API Key 等敏感信息）
            logger.error("LLM call failed: HTTP %s", exc.response.status_code)
            raise LLMClientError(f"LLM 调用失败 (HTTP {exc.response.status_code})") from exc
        except httpx.RequestError as exc:
            logger.error("LLM call failed: %s", type(exc).__name__)
            raise LLMClientError(f"LLM 调用失败: {type(exc).__name__}") from exc

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
        return self._parse_json_content(result.content)

    @staticmethod
    def _parse_json_content(content: str) -> Dict[str, Any]:
        """从模型输出中稳健地解析 JSON。

        兼容以下常见情况：
          - 直接是合法 JSON；
          - 被 ```json ... ``` 或 ``` ... ``` 代码围栏包裹；
          - JSON 前后夹带说明性文字（提取第一个 {...} 或 [...] 片段）。
        """
        text = (content or "").strip()

        # 1. 直接尝试
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 去除 markdown 代码围栏
        if text.startswith("```"):
            fenced = text.strip("`")
            # 去掉可能的语言标注行（如 json）
            if "\n" in fenced:
                first_line, rest = fenced.split("\n", 1)
                if first_line.strip().lower() in ("json", "javascript", ""):
                    fenced = rest
            fenced = fenced.strip()
            try:
                return json.loads(fenced)
            except json.JSONDecodeError:
                text = fenced

        # 3. 提取第一个 JSON 对象/数组片段
        for opener, closer in (("{", "}"), ("[", "]")):
            start = text.find(opener)
            end = text.rfind(closer)
            if start != -1 and end != -1 and end > start:
                candidate = text[start:end + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

        raise LLMClientError("LLM 返回内容不是合法 JSON")

    def _normalize_url(self, base_url: str) -> str:
        """规范化 LLM API 地址。

        base_url 可能是:
          - https://api.openai.com/v1
          - https://xxx.maas.aliyuncs.com/compatible-mode/v1
          - https://api.openai.com/v1/chat/completions (已经完整)

        只需追加 /chat/completions, 不再追加 /v1。
        """
        normalized = base_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            return normalized
        return f"{normalized}/chat/completions"

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
        # 返回合法 JSON，保证 chat_json / json.loads 调用方在 dry-run 下也能正常工作
        content = json.dumps(
            {
                "dry_run": True,
                "model": model or self.settings.model,
                "system_prompt": system_prompt or "",
                "user_prompt": user_prompt,
            },
            ensure_ascii=False,
        )
        return LLMResult(content=content, model=model or self.settings.model, raw={"dry_run": True})


default_llm_client = LLMClient()
