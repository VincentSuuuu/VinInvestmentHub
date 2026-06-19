import requests


NOTION_VERSION = "2022-06-28"


def build_sources_schema_properties():
    return {
        "Classification Status": {
            "select": {
                "options": [
                    {"name": "Unclassified", "color": "gray"},
                    {"name": "Suggested", "color": "blue"},
                    {"name": "Confirmed", "color": "green"},
                    {"name": "Needs Review", "color": "yellow"},
                ]
            }
        },
        "Suggested Theme": {"rich_text": {}},
        "Suggested Geography": {"rich_text": {}},
        "Suggested Asset Class": {"rich_text": {}},
        "Suggested Entities": {"rich_text": {}},
        "Suggested Taxonomy L1": {"rich_text": {}},
        "Suggested Taxonomy L2": {"rich_text": {}},
        "Suggested Taxonomy L3": {"rich_text": {}},
        "Classification Confidence": {
            "select": {
                "options": [
                    {"name": "High", "color": "green"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "red"},
                ]
            }
        },
        "Classification Reason": {"rich_text": {}},
        "Classifier Run At": {"date": {}},
    }


def update_sources_schema(token: str, database_id: str):
    response = requests.patch(
        f"https://api.notion.com/v1/databases/{database_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
        json={"properties": build_sources_schema_properties()},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
