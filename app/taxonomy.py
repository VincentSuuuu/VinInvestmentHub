VALID_THEMES = {
    "US-China Trade",
    "China Macro",
    "US Macro",
    "Policy",
    "AI",
    "EV",
    "Healthcare",
    "Fiscal",
    "Monetary",
}

VALID_GEOGRAPHIES = {"China", "US", "Global", "Europe", "Asia"}

VALID_ASSET_CLASSES = {"Equity", "Bond", "FX", "Commodity", "Crypto", "Macro"}


def _clean_list(values):
    if not values:
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _filter_known(values, allowed):
    return [value for value in _clean_list(values) if value in allowed]


def normalize_suggestions(raw):
    return {
        "theme": _filter_known(raw.get("theme", []), VALID_THEMES),
        "geography": _filter_known(raw.get("geography", []), VALID_GEOGRAPHIES),
        "asset_class": _filter_known(raw.get("asset_class", []), VALID_ASSET_CLASSES),
        "entities": _clean_list(raw.get("entities", [])),
        "taxonomy_l1": _clean_list(raw.get("taxonomy_l1", [])),
        "taxonomy_l2": _clean_list(raw.get("taxonomy_l2", [])),
        "taxonomy_l3": _clean_list(raw.get("taxonomy_l3", [])),
    }
