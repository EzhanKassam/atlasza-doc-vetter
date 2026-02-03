from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class Settings:
    llm_provider: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    redact_before_sending: bool
    max_chars_per_doc: int

def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai").strip(),
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini").strip(),
        redact_before_sending=os.getenv("REDACT_BEFORE_SENDING", "true").lower() == "true",
        max_chars_per_doc=int(os.getenv("MAX_CHARS_PER_DOC", "18000")),
    )
