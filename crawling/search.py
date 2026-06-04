from pathlib import Path

from whoosh import index, scoring
from whoosh.qparser import MultifieldParser

_BASE_DIR = Path(__file__).resolve().parent
INDEX_DIR = str(_BASE_DIR / "whoosh_index_500mb")

def search(query_text, limit=10):
    ind = index.open_dir(INDEX_DIR)
    with ind.searcher(weighting=scoring.BM25F()) as searcher:
        if not query_text or not query_text.strip():
            return []

        parser = MultifieldParser(
            ["title", "body"],
            schema=ind.schema,
            fieldboosts={"title": 2.0, "body": 1.0},
        )
        query = parser.parse(query_text)
        results = searcher.search(query, limit=limit)

        return [
            {
                "url": hit["url"],
                "title": hit["title"],
                "score": hit.score,
                "snippet": hit.highlights("body", top=3) or hit["body"][:300],
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
