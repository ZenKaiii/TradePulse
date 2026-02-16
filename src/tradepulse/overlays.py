from typing import Dict, List


def match_overlays(
    texts: List[str], stocks: List[str], keywords: List[str], geopolitics: List[str]
) -> Dict[str, List[str]]:
    joined = " ".join(texts).lower()

    stock_hits = [symbol for symbol in stocks if symbol.lower() in joined]
    keyword_hits = [keyword for keyword in keywords if keyword.lower() in joined]

    geo_hits = []
    for topic in geopolitics:
        tokens = [t for t in topic.lower().split("-") if t]
        if tokens and any(token in joined for token in tokens):
            geo_hits.append(topic)

    return {"stocks": stock_hits, "keywords": keyword_hits, "geopolitics": geo_hits}
