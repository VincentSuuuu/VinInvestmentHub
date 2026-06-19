from app.config import load_settings
from app.notion_schema import update_sources_schema


def main():
    settings = load_settings()
    result = update_sources_schema(
        token=settings.notion_token,
        database_id=settings.notion_sources_database_id,
    )
    print(f"Updated Sources schema: {result.get('id', settings.notion_sources_database_id)}")


if __name__ == "__main__":
    main()
