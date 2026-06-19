import pytest

from app.config import Settings


def test_settings_require_notion_database_id():
    with pytest.raises(ValueError, match="NOTION_SOURCES_DATABASE_ID"):
        Settings(notion_token="secret", notion_sources_database_id="")


def test_settings_accept_required_values():
    settings = Settings(
        notion_token="secret",
        notion_sources_database_id="2383b3ce-d227-8225-92d4-8765979cd4a8",
        openai_api_key="key",
    )

    assert settings.notion_token == "secret"
    assert settings.notion_sources_database_id == "2383b3ce-d227-8225-92d4-8765979cd4a8"
