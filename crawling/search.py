from pathlib import Path
import html
import re

from whoosh import index
from whoosh.qparser import MultifieldParser

_BASE_DIR = Path(__file__).resolve().parent
INDEX_DIR = str(_BASE_DIR / "whoosh_index_500mb")
SNIPPET_WINDOW = 180


def _query_terms(query_text):
    return [
        term.lower()
        for term in re.findall(r"\w+", query_text)
        if len(term) > 1
    ]


def _best_snippet_window(body, terms, window=SNIPPET_WINDOW):
    if not body:
        return ""
    if not terms:
        return body[:window]

    lower_body = body.lower()
    best_start = 0
    best_score = 0

    for term in terms:
        for match in re.finditer(re.escape(term), lower_body):
            start = max(match.start() - window // 3, 0)
            end = min(start + window, len(body))
            snippet = lower_body[start:end]
            coverage = sum(1 for query_term in set(terms) if query_term in snippet)
            frequency = sum(snippet.count(query_term) for query_term in terms)
            score = coverage * 4 + frequency

            if score > best_score:
                best_score = score
                best_start = start

    return body[best_start : best_start + window].strip()


def make_snippet(body, query_text):
    terms = _query_terms(query_text)
    snippet = _best_snippet_window(body, terms)
    if not snippet:
        return ""

    prefix = "..." if len(body) > len(snippet) and not body.startswith(snippet) else ""
    suffix = "..." if body.find(snippet) + len(snippet) < len(body) else ""
    escaped = html.escape(snippet)

    if terms:
        pattern = re.compile(
            r"(" + "|".join(re.escape(html.escape(term)) for term in set(terms)) + r")",
            re.IGNORECASE,
        )
        escaped = pattern.sub(r"<mark>\1</mark>", escaped)

    return f"{prefix}{escaped}{suffix}"


def search(query_text, limit=10):
    ind = index.open_dir(INDEX_DIR)
    with ind.searcher() as searcher:
        if not query_text or not query_text.strip():
            return []

        parser = MultifieldParser(["title", "body"], schema=ind.schema)
        query = parser.parse(query_text)
        results = searcher.search(query, limit=limit)

        return [
            {
                "url": hit["url"],
                "title": hit["title"],
                "score": hit.score,
                "snippet": make_snippet(hit["body"], query_text),
                "outgoing_links": hit["outgoing_links"],
            }
            for hit in results
        ]

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Search: ")
    hits = search(query)
    if not hits:
        print("No results.")
    for i, hit in enumerate(hits, 1):
        print(f"\n{i}. {hit['title']} (score: {hit['score']:.4f})")
        print(f"   {hit['url']}")
        print(f"   {hit['snippet'][:200]}")
