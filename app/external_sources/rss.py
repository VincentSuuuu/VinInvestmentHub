import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests

from app.external_sources.models import FeedItem, SourceDefinition


USER_AGENT = "VinInvestmentHub/0.1 (+notion raw signals)"


def fetch_feed_xml(url: str, timeout: int = 30) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    if not response.encoding or response.encoding.lower() == "iso-8859-1":
        response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def parse_feed_xml(xml_text: str, source: SourceDefinition) -> list[FeedItem]:
    root = ElementTree.fromstring(xml_text)
    if _strip_namespace(root.tag) == "rss":
        return _parse_rss(root, source)
    if _strip_namespace(root.tag) == "feed":
        return _parse_atom(root, source)
    channel = root.find("channel")
    if channel is not None:
        return _parse_rss(root, source)
    return []


def _parse_rss(root: ElementTree.Element, source: SourceDefinition) -> list[FeedItem]:
    items = []
    for item in root.findall(".//item"):
        title = _text(item, "title")
        link = _text(item, "link")
        guid = _text(item, "guid")
        summary = _text(item, "description") or _text(item, "summary")
        published = _parse_datetime(_text(item, "pubDate") or _text(item, "published"))
        if title:
            items.append(
                FeedItem(
                    source_key=source.key,
                    source_name=source.display_name,
                    title=_clean_text(title),
                    url=_clean_url(link),
                    summary=_clean_text(summary),
                    published_at=published,
                    raw_id=guid or link,
                )
            )
    return items


def _parse_atom(root: ElementTree.Element, source: SourceDefinition) -> list[FeedItem]:
    items = []
    for entry in root.findall(".//{*}entry"):
        title = _text(entry, "title")
        link = _atom_link(entry)
        raw_id = _text(entry, "id")
        summary = _text(entry, "summary") or _text(entry, "content")
        published = _parse_datetime(_text(entry, "published") or _text(entry, "updated"))
        if title:
            items.append(
                FeedItem(
                    source_key=source.key,
                    source_name=source.display_name,
                    title=_clean_text(title),
                    url=_clean_url(link),
                    summary=_clean_text(summary),
                    published_at=published,
                    raw_id=raw_id or link,
                )
            )
    return items


def _text(element: ElementTree.Element, tag_name: str) -> str:
    found = element.find(tag_name)
    if found is None:
        found = element.find(f"{{*}}{tag_name}")
    return found.text.strip() if found is not None and found.text else ""


def _atom_link(entry: ElementTree.Element) -> str:
    for link in entry.findall("{*}link"):
        href = link.attrib.get("href", "")
        rel = link.attrib.get("rel", "alternate")
        if href and rel == "alternate":
            return href
    first = entry.find("{*}link")
    return first.attrib.get("href", "") if first is not None else ""


def _strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _clean_text(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_url(value: str) -> str:
    value = (value or "").strip()
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return value
    return value


def _parse_datetime(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None
