from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
import json
import os

INDEX_DIR = "whoosh_index"

def get_schema():
    return Schema(
        url = ID(stored=True, unique=True),
        title = TEXT(stored=True),
        body = TEXT(stored=True),
        crawled_at = ID(stored=True),
        depth = NUMERIC(stored=True)
    )

def create_index():
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
        return index.create_in(INDEX_DIR, get_schema())
    return index.open_dir(INDEX_DIR)

def build_index():
    index = create_index()
    writer = index.writer()

    with open("output.json") as f:
        pages = json.load(f)

    print(f"Indexing {len(pages)} pages:")

    for page in pages:
        writer.update_document(
            url = str(page.get("url", "")),
            title = str(page.get("title", "")),
            body = str(page.get("body", "")),
            crawled_at = str(page.get("crawled_at", "")),
            depth = int(page.get("depth", 0))
        )
        print(f"Indexed: {page.get('url')}")

    writer.commit()
    print("Finished Building Index")

if __name__ == "__main__":
    build_index()