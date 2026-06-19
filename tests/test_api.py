from fastapi.testclient import TestClient

from app.main import create_app


def test_health_route():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


class RouteFakeProvider:
    def classify(self, source):
        return {
            "source_type": "News",
            "theme": ["US-China Trade"],
            "geography": ["US", "China"],
            "asset_class": ["Macro"],
            "entities": ["Tariff"],
            "taxonomy_l1": ["Policy"],
            "taxonomy_l2": ["US-China Trade"],
            "taxonomy_l3": ["Tariff escalation"],
            "confidence": "Medium",
            "reason": "Tariff policy source.",
            "needs_review": False,
        }


def test_classify_route_returns_suggestions():
    client = TestClient(create_app(classification_provider=RouteFakeProvider()))
    response = client.post(
        "/api/classify",
        json={"title": "Tariff update", "url": "https://example.com", "text": "Tariff policy update."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"]["title"] == "Tariff update"
    assert body["classification"]["theme"] == ["US-China Trade"]
    assert body["classification"]["classification_status"] == "Suggested"
