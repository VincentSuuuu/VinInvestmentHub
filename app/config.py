import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    notion_token: str = ""
    notion_sources_database_id: str = ""
    notion_raw_signals_data_source_id: str = ""
    notion_raw_signals_database_id: str = ""
    notion_knowledge_database_id: str = ""
    notion_event_hubs_database_id: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    rsshub_base_url: str = "https://rsshub.rssforever.com"
    require_notion_token: bool = field(default=True, repr=False)
    require_sources_database: bool = field(default=True, repr=False)

    def __post_init__(self):
        if self.require_notion_token and not self.notion_token:
            raise ValueError("NOTION_TOKEN is required")
        if self.require_sources_database and not self.notion_sources_database_id:
            raise ValueError("NOTION_SOURCES_DATABASE_ID is required")


def load_settings(require_notion_token: bool = True, require_sources_database: bool = True) -> Settings:
    load_dotenv(dotenv_path=Path.cwd() / ".env", encoding="utf-8-sig", override=True)
    return Settings(
        notion_token=os.getenv("NOTION_TOKEN", ""),
        notion_sources_database_id=os.getenv("NOTION_SOURCES_DATABASE_ID", ""),
        notion_raw_signals_data_source_id=os.getenv("NOTION_RAW_SIGNALS_DATA_SOURCE_ID", ""),
        notion_raw_signals_database_id=os.getenv("NOTION_RAW_SIGNALS_DATABASE_ID", ""),
        notion_knowledge_database_id=os.getenv("NOTION_KNOWLEDGE_DATABASE_ID", ""),
        notion_event_hubs_database_id=os.getenv("NOTION_EVENT_HUBS_DATABASE_ID", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        rsshub_base_url=os.getenv("RSSHUB_BASE_URL", "https://rsshub.rssforever.com"),
        require_notion_token=require_notion_token,
        require_sources_database=require_sources_database,
    )
