import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import load_settings
from app.external_sources.pipeline import collect_external_signals
from app.external_sources.rss import fetch_feed_xml
from app.external_sources.sources import build_default_sources
from app.notion_raw_signals import RawSignalsNotionClient


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch major external news events into Phase 6 Raw Signals.")
    parser.add_argument("--source", choices=["all", "gelonghui", "caixin", "reuters"], default="all")
    parser.add_argument("--min-score", type=int, default=5)
    parser.add_argument("--limit-per-feed", type=int, default=30)
    parser.add_argument("--max-age-days", type=int, default=14)
    parser.add_argument("--request-timeout", type=int, default=10, help="Per-feed HTTP timeout in seconds.")
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=10,
        help="Maximum candidates to print or write. Use 0 for no cap.",
    )
    parser.add_argument("--write-notion", action="store_true", help="Create pages in the Raw Signals data source.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    settings = load_settings(require_notion_token=False, require_sources_database=False)
    sources = build_default_sources(settings.rsshub_base_url)
    source_keys = None if args.source == "all" else [args.source]
    errors = []

    def collect_error(source_key: str, feed_url: str, exc: Exception):
        errors.append({"source": source_key, "feed_url": feed_url, "error": str(exc)})

    def fetch_with_timeout(feed_url: str) -> str:
        return fetch_feed_xml(feed_url, timeout=args.request_timeout)

    all_signals = collect_external_signals(
        sources=sources,
        source_keys=source_keys,
        min_score=args.min_score,
        limit_per_feed=args.limit_per_feed,
        max_age_days=args.max_age_days,
        fetch_xml=fetch_with_timeout,
        on_error=collect_error,
    )
    signals = all_signals
    if args.max_candidates > 0:
        signals = all_signals[: args.max_candidates]

    created = []
    skipped_existing = []
    if args.write_notion:
        if not settings.notion_token:
            raise SystemExit("NOTION_TOKEN is required when --write-notion is set")
        client = RawSignalsNotionClient(
            token=settings.notion_token,
            raw_signals_data_source_id=settings.notion_raw_signals_data_source_id,
            raw_signals_database_id=settings.notion_raw_signals_database_id,
        )
        for signal in signals:
            result = client.create_raw_signal(signal)
            if result.get("existing"):
                skipped_existing.append(result)
            else:
                created.append(result)

    payload = {
        "source": args.source,
        "min_score": args.min_score,
        "max_age_days": args.max_age_days,
        "request_timeout": args.request_timeout,
        "max_candidates": args.max_candidates,
        "count": len(signals),
        "total_candidate_count": len(all_signals),
        "write_notion": args.write_notion,
        "created_count": len(created),
        "skipped_existing_count": len(skipped_existing),
        "errors": errors,
        "signals": [_serialize_signal(signal) for signal in signals],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Found {len(signals)} major candidate signals.")
        if errors:
            print(f"Skipped {len(errors)} feed(s) due to fetch or parse errors.")
        for signal in signals:
            print(f"- [{signal.importance_label} score={signal.importance_score}] {signal.source_name}: {signal.title}")
            print(f"  {signal.url}")
    return 0


def _serialize_signal(signal):
    data = asdict(signal)
    if signal.published_at:
        data["published_at"] = signal.published_at.isoformat()
    return data


if __name__ == "__main__":
    raise SystemExit(main())
