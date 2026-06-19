from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.classifier import classify_source
from app.config import load_settings
from app.models import ClassificationResult, SourceInput
from app.notion_client import NotionClient
from app.providers.openai_provider import OpenAIProvider


def create_app(classification_provider=None):
    app = FastAPI(title="Source Classifier MVP")
    app.state.classification_provider = classification_provider

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.post("/api/classify")
    def classify(source: SourceInput):
        try:
            provider = app.state.classification_provider
            if provider is None:
                settings = load_settings()
                provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
            result = classify_source(source, provider)
            return {"source": source.model_dump(), "classification": result.model_dump(mode="json")}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/api/sync")
    def sync(payload: dict):
        try:
            settings = load_settings()
            source = SourceInput(**payload["source"])
            result = ClassificationResult(**payload["classification"])
            client = NotionClient(settings.notion_token, settings.notion_sources_database_id)
            return client.create_source(source, result)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
    return app


app = create_app()
