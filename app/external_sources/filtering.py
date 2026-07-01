import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.external_sources.models import ExternalSignal, FeedItem, SourceDefinition


KEYWORD_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("突发", 4),
    ("快讯", 2),
    ("重磅", 4),
    ("重大", 3),
    ("紧急", 3),
    ("宣布", 2),
    ("制裁", 4),
    ("关税", 4),
    ("出口管制", 4),
    ("禁令", 3),
    ("停火", 4),
    ("袭击", 4),
    ("战争", 4),
    ("导弹", 4),
    ("伊朗", 3),
    ("以色列", 3),
    ("美联储", 4),
    ("联储", 3),
    ("降息", 3),
    ("加息", 3),
    ("央行", 3),
    ("人民银行", 3),
    ("财政部", 3),
    ("商务部", 3),
    ("白宫", 3),
    ("国务院", 3),
    ("特朗普", 3),
    ("习近平", 3),
    ("通胀", 3),
    ("CPI", 3),
    ("PMI", 3),
    ("GDP", 3),
    ("全球经济", 3),
    ("全球市场", 3),
    ("国际货币基金组织", 3),
    ("世界银行", 3),
    ("BREAKING", 4),
    ("Exclusive", 3),
    ("sanction", 4),
    ("tariff", 4),
    ("export control", 4),
    ("ceasefire", 4),
    ("attack", 4),
    ("missile", 4),
    ("war", 4),
    ("Federal Reserve", 4),
    ("Fed", 3),
    ("central bank", 3),
    ("PBOC", 3),
    ("Treasury", 3),
    ("White House", 3),
    ("Commerce Department", 3),
    ("Trump", 3),
    ("Xi", 3),
    ("inflation", 3),
    ("global economy", 3),
    ("global markets", 3),
    ("IMF", 3),
    ("World Bank", 3),
    ("G7", 3),
    ("G20", 3),
    ("rate cut", 3),
    ("rate hike", 3),
    ("oil", 2),
    ("OPEC", 3),
)

NOISE_TERMS = ("盘中", "股价异动", "评级", "个股", "涨幅", "跌幅")


def build_signal(item: FeedItem, source: SourceDefinition, min_score: int = 5) -> ExternalSignal | None:
    haystack = f"{item.title} {item.summary}"
    score, matched_terms = score_importance(haystack)
    if score < min_score:
        return None
    topics = infer_topics(haystack, source.default_topics)
    regions = infer_regions(haystack, source.default_regions)
    asset_classes = infer_asset_classes(haystack)
    importance_label = "关键" if score >= 6 else "重要"
    notes = f"重大事件初筛 score={score}; matched={', '.join(matched_terms[:8])}"
    return ExternalSignal(
        source_key=item.source_key,
        source_name=item.source_name,
        title=item.title,
        url=item.url,
        summary=item.summary,
        published_at=item.published_at,
        duplicate_key=build_duplicate_key(item),
        importance_score=score,
        importance_label=importance_label,
        matched_terms=tuple(matched_terms),
        suggested_topics=topics,
        suggested_regions=regions,
        suggested_asset_classes=asset_classes,
        source_trust=source.trust,
        source_registry_page_id=source.source_registry_page_id,
        notes=notes,
    )


def score_importance(text: str) -> tuple[int, list[str]]:
    normalized = text or ""
    lower = normalized.lower()
    score = 0
    matches = []
    for term, weight in KEYWORD_WEIGHTS:
        if _contains_term(normalized, lower, term):
            score += weight
            matches.append(term)
    if any(term in normalized for term in NOISE_TERMS) and score < 5:
        score = max(0, score - 2)
    return score, matches


def infer_topics(text: str, defaults: tuple[str, ...] = ()) -> tuple[str, ...]:
    rules = (
        ("中国宏观", ("中国", "北京", "国务院", "人民银行", "PBOC", "中国央行", "房地产")),
        ("美国宏观", ("美国", "美联储", "白宫", "特朗普", "Fed", "Federal Reserve", "White House", "Treasury", "Trump")),
        (
            "世界宏观",
            (
                "全球经济",
                "全球市场",
                "国际货币基金组织",
                "世界银行",
                "G7",
                "G20",
                "IMF",
                "World Bank",
                "global economy",
                "global markets",
                "global growth",
                "world economy",
            ),
        ),
        ("政策", ("政策", "监管", "法案", "制裁", "禁令", "rule", "policy", "sanction", "ban")),
        ("地缘政治", ("伊朗", "以色列", "中东", "战争", "袭击", "导弹", "war", "attack", "missile")),
        ("AI", ("AI", "人工智能", "芯片", "半导体", "Nvidia", "GPU", "semiconductor")),
        ("EV", ("电动车", "新能源车", "EV", "electric vehicle")),
        ("财政", ("财政", "预算", "赤字", "Treasury", "debt ceiling", "fiscal")),
        ("货币", ("美联储", "央行", "降息", "加息", "利率", "Fed", "central bank", "rate cut", "rate hike")),
        ("大宗商品", ("原油", "石油", "黄金", "铜", "OPEC", "oil", "gold", "copper")),
    )
    selected = []
    if _is_us_china_trade_signal(text):
        selected.append("中美贸易")
    selected.extend(_infer_multi_select(text, rules, ()))
    if not selected:
        selected.extend(defaults)
    return tuple(dict.fromkeys(selected))


def infer_regions(text: str, defaults: tuple[str, ...] = ()) -> tuple[str, ...]:
    rules = (
        ("中国", ("中国", "北京", "上海", "香港", "人民币", "China", "Chinese", "Beijing", "Hong Kong", "yuan")),
        ("美国", ("美国", "华盛顿", "美元", "美联储", "US ", "U.S.", "United States", "Washington", "Fed", "Trump")),
        ("全球", ("全球", "国际", "国际货币基金组织", "世界银行", "global", "world", "IMF", "World Bank", "G7", "G20")),
        ("欧洲", ("欧洲", "欧盟", "德国", "法国", "Europe", "EU", "ECB")),
        ("亚洲", ("亚洲", "日本", "韩国", "印度", "Asia", "Japan", "Korea", "India")),
        ("中东", ("中东", "伊朗", "以色列", "沙特", "Middle East", "Iran", "Israel", "Saudi")),
    )
    return _infer_multi_select(text, rules, defaults)


def infer_asset_classes(text: str) -> tuple[str, ...]:
    rules = (
        ("股票", ("股票", "A股", "港股", "美股", "equity", "stock", "shares")),
        ("债券", ("债券", "国债", "收益率", "bond", "Treasury yield", "yield")),
        ("外汇", ("汇率", "人民币", "美元", "外汇", "FX", "currency", "dollar", "yuan")),
        ("商品", ("原油", "石油", "黄金", "铜", "commodity", "oil", "gold", "copper")),
        ("加密", ("比特币", "加密", "Bitcoin", "crypto")),
        ("宏观", ("宏观", "政策", "央行", "通胀", "GDP", "CPI", "PMI", "inflation", "central bank")),
    )
    inferred = _infer_multi_select(text, rules, ())
    return inferred or ("宏观",)


def build_duplicate_key(item: FeedItem) -> str:
    normalized_url = _normalize_url(item.url)
    basis = normalized_url or re.sub(r"\s+", " ", item.title.lower()).strip()
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]
    return f"{item.source_key}:{digest}"


def _infer_multi_select(text: str, rules: tuple[tuple[str, tuple[str, ...]], ...], defaults: tuple[str, ...]) -> tuple[str, ...]:
    lower = text.lower()
    selected: list[str] = []
    for label, terms in rules:
        for term in terms:
            if _contains_term(text, lower, term):
                selected.append(label)
                break
    if not selected:
        selected.extend(defaults)
    return tuple(dict.fromkeys(selected))


def _normalize_url(url: str) -> str:
    if not url:
        return ""
    split = urlsplit(url)
    query = [
        (key, value)
        for key, value in parse_qsl(split.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in {"from", "ref", "source"}
    ]
    return urlunsplit((split.scheme, split.netloc, split.path.rstrip("/"), urlencode(query), ""))


def _is_ascii(value: str) -> bool:
    return all(ord(char) < 128 for char in value)


def _contains_term(text: str, lower_text: str, term: str) -> bool:
    if not _is_ascii(term):
        return term in text
    escaped = re.escape(term.lower())
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.search(rf"\b{escaped}\b", lower_text) is not None


def _is_us_china_trade_signal(text: str) -> bool:
    lower = text.lower()
    explicit_terms = (
        "中美贸易",
        "中美关税",
        "美中贸易",
        "美中关税",
        "美国对中国",
        "中国对美国",
        "us-china",
        "china-us",
        "u.s.-china",
        "china tariff",
        "china tariffs",
        "chinese tariff",
        "chinese tariffs",
    )
    if any(_contains_term(text, lower, term) for term in explicit_terms):
        return True

    trade_terms = ("关税", "贸易战", "出口管制", "tariff", "export control", "trade war")
    china_terms = ("中国", "中方", "China", "Chinese", "Beijing")
    us_terms = ("美国", "美方", "US", "U.S.", "United States", "White House", "Trump")
    return (
        any(_contains_term(text, lower, term) for term in trade_terms)
        and any(_contains_term(text, lower, term) for term in china_terms)
        and any(_contains_term(text, lower, term) for term in us_terms)
    )
