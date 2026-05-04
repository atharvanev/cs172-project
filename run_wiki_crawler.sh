#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -d "$ROOT/venv" ]]; then
  python3 -m venv "$ROOT/venv"
fi

"$ROOT/venv/bin/pip" install -r "$ROOT/requirements.txt"

cd "$ROOT/crawling"
exec "$ROOT/venv/bin/scrapy" crawl wiki -o output.json
