from app.providers.openai_provider import parse_model_json


def test_parse_model_json_accepts_fenced_json():
    text = """```json
{"source_type":"News","theme":["Policy"],"geography":["US"],"asset_class":["Macro"],"entities":["Fed"],"taxonomy_l1":["Policy"],"taxonomy_l2":["Fed Policy"],"taxonomy_l3":[],"confidence":"High","reason":"Fed source.","needs_review":false}
```"""

    result = parse_model_json(text)

    assert result["source_type"] == "News"
    assert result["confidence"] == "High"
