import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    notion_token: str
    notion_sources_database_id: str
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    def __post_init__(self):
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN is required")
        if not self.notion_sources_database_id:
            raise ValueError("NOTION_SOURCES_DATABASE_ID is required")


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        notion_token=os.getenv("NOTION_TOKEN", ""),
        notion_sources_database_id=os.getenv("NOTION_SOURCES_DATABASE_ID", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    )
