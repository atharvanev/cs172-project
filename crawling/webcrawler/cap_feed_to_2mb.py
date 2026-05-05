#!/usr/bin/env python3
"""
Cap a Scrapy-style JSON array feed (see 2mb.json) to a maximum UTF-8 byte size
while preserving the same layout: [\n + objects joined by ",\\n" + \\n]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 2 MiB (binary); change if you need decimal MB (2_000_000).
MAX_BYTES = 2 * 1024 * 1024


def serialize_feed(items: list) -> str:
    """Match 2mb.json layout: opening bracket and newline, items separated by comma+newline."""
    if not items:
        return "[\n]"
    body = ",\n".join(json.dumps(item, ensure_ascii=False) for item in items)
    return "[\n" + body + "\n]"


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("2mb.json")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("2mb_capped.json")

    data = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        data = [data]

    while data and len(serialize_feed(data).encode("utf-8")) > MAX_BYTES:
        data.pop()

    out = serialize_feed(data)
    dst.write_text(out, encoding="utf-8")
    print(f"Wrote {dst} ({len(out.encode('utf-8'))} bytes, {len(data)} items)")


if __name__ == "__main__":
    main()
