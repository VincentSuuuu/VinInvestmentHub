import pytest

from app.config import Settings, load_settings


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


def test_settings_can_load_without_legacy_sources_for_dry_run():
    settings = Settings(require_notion_token=False, require_sources_database=False)

    assert settings.notion_token == ""
    assert settings.rsshub_base_url == "https://rsshub.rssforever.com"


def test_load_settings_accepts_utf8_bom_env(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\ufeffNOTION_TOKEN=secret\nNOTION_SOURCES_DATABASE_ID=sources-db\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = load_settings()

    assert settings.notion_token == "secret"
    assert settings.notion_sources_database_id == "sources-db"
