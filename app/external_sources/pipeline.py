from collections.abc import Callable, Iterable
from datetime import datetime, timedelta, timezone

from app.external_sources.filtering import build_signal
from app.external_sources.models import ExternalSignal, SourceDefinition
from app.external_sources.rss import fetch_feed_xml, parse_feed_xml


FetchXml = Callable[[str], str]
ErrorHandler = Callable[[str, str, Exception], None]


def collect_external_signals(
    sources: dict[str, SourceDefinition],
    source_keys: Iterable[str] | None = None,
    min_score: int = 5,
    limit_per_feed: int = 30,
    max_age_days: int | None = 14,
    now: datetime | None = None,
    fetch_xml: FetchXml = fetch_feed_xml,
    on_error: ErrorHandler | None = None,
) -> list[ExternalSignal]:
    selected_keys = list(source_keys or sources.keys())
    cutoff = _cutoff_datetime(max_age_days, now)
    signals_by_key: dict[str, ExternalSignal] = {}
    for source_key in selected_keys:
        source = sources[source_key]
        for feed_url in source.feed_urls:
            try:
                xml_text = fetch_xml(feed_url)
                items = parse_feed_xml(xml_text, source)[:limit_per_feed]
            except Exception as exc:
                if on_error:
                    on_error(source_key, feed_url, exc)
                continue
            for item in items:
                if cutoff and item.published_at and item.published_at < cutoff:
                    continue
                signal = build_signal(item, source, min_score=min_score)
                if signal is None:
                    continue
                existing = signals_by_key.get(signal.duplicate_key)
                if existing is None or signal.importance_score > existing.importance_score:
                    signals_by_key[signal.duplicate_key] = signal
    signals = list(signals_by_key.values())
    return sorted(signals, key=lambda signal: (signal.published_at is not None, signal.published_at), reverse=True)


def _cutoff_datetime(max_age_days: int | None, now: datetime | None) -> datetime | None:
    if max_age_days is None:
        return None
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) - timedelta(days=max_age_days)
