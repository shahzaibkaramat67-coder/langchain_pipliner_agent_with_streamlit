from dataclasses import dataclass
import os


@dataclass(frozen=True)
class APISettings:
    base_url: str
    api_key: str
    model: str
    tavily_api_key: str

    @classmethod
    def from_environment(cls) -> "APISettings":
        return cls(
            base_url=os.getenv("FREELLMAPI_BASE_URL", "").strip(),
            api_key=os.getenv("FREELLMAPI_API_KEY", "").strip(),
            model=os.getenv("FREELLMAPI_MODEL", "").strip(),
            tavily_api_key=os.getenv("TAVILY_API_KEY", "").strip(),
        )
