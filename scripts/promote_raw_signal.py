import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import load_settings
from app.notion_promotion import RawSignalPromotionClient, summarize_raw_signal


ACTION_LABELS = {
    "accept": "Accept to Knowledge",
    "output": "Promote to Output",
    "merge": "Merge with Existing",
    "watch": "Watch",
    "ignore": "Ignore",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review and promote one Notion Raw Signal.")
    parser.add_argument("--list", action="store_true", help="List New / Needs Review Raw Signals.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum rows to list.")
    parser.add_argument("--raw-page-id", default="", help="Raw Signals page id to act on.")
    parser.add_argument("--duplicate-key", default="", help="Find Raw Signal by duplicate key.")
    parser.add_argument("--action", choices=ACTION_LABELS.keys(), help="Promotion action.")
    parser.add_argument("--knowledge-page-id", default="", help="Existing Knowledge Item page id for merge.")
    parser.add_argument("--event-hub-page-id", default="", help="Event Hub page id for watch.")
    parser.add_argument("--dry-run", action="store_true", help="Print intended action without writing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    settings = load_settings(require_notion_token=True, require_sources_database=False)
    client = RawSignalPromotionClient(
        token=settings.notion_token,
        raw_signals_database_id=settings.notion_raw_signals_database_id,
        knowledge_database_id=settings.notion_knowledge_database_id,
    )

    if args.list or not args.action:
        rows = [summarize_raw_signal(row) for row in client.list_review_queue(args.limit)]
        return _print({"count": len(rows), "signals": rows}, args.json)

    raw_signal = _load_raw_signal(client, args.raw_page_id, args.duplicate_key)
    action_label = ACTION_LABELS[args.action]
    raw_summary = summarize_raw_signal(raw_signal)
    if args.dry_run:
        return _print(
            {
                "dry_run": True,
                "action": action_label,
                "raw_signal": raw_summary,
                "knowledge_page_id": args.knowledge_page_id,
                "event_hub_page_id": args.event_hub_page_id,
            },
            args.json,
        )

    if args.action == "accept":
        result = client.promote_to_knowledge(raw_signal)
    elif args.action == "output":
        result = client.promote_to_output(raw_signal)
    elif args.action == "merge":
        result = client.merge_with_existing(raw_signal, args.knowledge_page_id)
    elif args.action == "watch":
        result = client.watch(raw_signal, args.event_hub_page_id)
    elif args.action == "ignore":
        result = client.ignore(raw_signal)
    else:
        raise SystemExit(f"Unsupported action: {args.action}")

    return _print(
        {
            "dry_run": False,
            "action": result.action,
            "raw_signal_page_id": result.raw_signal_page_id,
            "status": result.status,
            "knowledge_page_id": result.knowledge_page_id,
            "event_hub_page_id": result.event_hub_page_id,
        },
        args.json,
    )


def _load_raw_signal(client: RawSignalPromotionClient, raw_page_id: str, duplicate_key: str):
    if raw_page_id:
        return client.get_raw_signal(raw_page_id)
    if duplicate_key:
        raw_signal = client.find_raw_signal_by_duplicate_key(duplicate_key)
        if raw_signal:
            return raw_signal
        raise SystemExit(f"No Raw Signal found for duplicate key: {duplicate_key}")
    raise SystemExit("--raw-page-id or --duplicate-key is required when --action is set")


def _print(payload: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if "signals" in payload:
        print(f"Found {payload['count']} reviewable Raw Signal(s).")
        for signal in payload["signals"]:
            topics = ", ".join(signal["topics"])
            print(f"- {signal['title']} [{signal['importance']} | {signal['status']} | {topics}]")
            print(f"  raw_page_id={signal['id']}")
            print(f"  duplicate_key={signal['duplicate_key']}")
            print(f"  url={signal['url']}")
        return 0
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
