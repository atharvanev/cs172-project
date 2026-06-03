from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC, STORED
import json
import os

INDEX_DIR = "whoosh_index"

def get_schema():
    return Schema(
        url = ID(stored=True, unique=True),
        title = TEXT(stored=True),
        body = TEXT(stored=True),
        crawled_at = ID(stored=True),
        depth = NUMERIC(stored=True),
        outgoing_links = STORED()
    )

def create_index(index_dir=INDEX_DIR):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        return index.create_in(index_dir, get_schema())
    return index.open_dir(index_dir)

def build_index(json_path="output.json", index_dir=INDEX_DIR):
    ix = create_index(index_dir)
    writer = ix.writer()

    with open(json_path) as f:
        pages = json.load(f)

    print(f"Indexing {len(pages)} pages:")

    for page in pages:
        writer.update_document(
            url = str(page.get("url", "")),
            title = str(page.get("title", "")),
            body = str(page.get("body", "")),
            crawled_at = str(page.get("crawled_at", "")),
            depth = int(page.get("depth", 0)),
            outgoing_links = page.get("outgoing_links", [])
        )
        print(f"Indexed: {page.get('url')}")

    writer.commit()
    print("Finished Building Index")

if __name__ == "__main__":
    build_index("500mb.json", "whoosh_index_500mb")