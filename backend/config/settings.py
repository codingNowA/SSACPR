#AppSettings 则是整个应用的顶层配置,包含应用名称、运行环境等全局元数据
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


@dataclass(frozen=True)
class LLMSettings:
	provider: str = os.getenv("LLM_PROVIDER", "openai_compatible")
	base_url: str = os.getenv("LLM_BASE_URL", "")
	api_key: str = os.getenv("LLM_API_KEY", "")
	model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
	timeout: int = int(os.getenv("LLM_TIMEOUT", "30"))
	max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
	temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
	dry_run: bool = os.getenv("LLM_DRY_RUN", "false").lower() == "true"


@dataclass(frozen=True)
class AppSettings:
	app_name: str = os.getenv("APP_NAME", "career-planning-agent")
	env: str = os.getenv("APP_ENV", "development")
	llm: LLMSettings = LLMSettings()


settings = AppSettings()


def get_llm_settings() -> LLMSettings:
	return settings.llm


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
	return os.getenv(key, default)

