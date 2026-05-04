# CS 172 Project: Web Search Engine

This repo is for the CS 172 course project. Part A (web option) is a Wikipedia crawler built with Scrapy. It walks English Wikipedia articles starting from seed URLs, records each page’s URL, title, body text, crawl time, depth, and outgoing links, and writes structured data to JSON. Raw HTML snapshots also land under a `pages` folder while the crawl runs.

## Team

- Atharva Nevasekar
- Nikhil Rao
- Austin Le
- David Lee
- Brandon Sun

## What gets stored

Each crawled page is shaped roughly like this:

```json
{
  "url": "https://example.edu/page.html",
  "title": "Example Page",
  "body": "stripped text content...",
  "crawled_at": "2025-04-28T10:30:00",
  "depth": 2,
  "outgoing_links": ["https://example.edu/other.html", "..."]
}
```

Paths worth knowing:

- **Seed list:** `crawling/seed_urls.txt` (one URL per line; add more anytime)
- **Feed export:** `crawling/output.json` when you use `-o output.json`
- **Saved HTML:** `crawling/pages/` (created by the wiki spider)

## Quick start

From the repo root:

```bash
./run_wiki_crawler.sh
```

That creates `venv` if it is missing, installs from `requirements.txt`, then runs `scrapy crawl wiki -o output.json` inside `crawling/`.

If you already have `venv` and want to run Scrapy yourself (different flags or output path):

```bash
source venv/bin/activate
cd crawling
scrapy crawl wiki -o output.json
```

## Tune the crawl

Before a long run, open `crawling/webcrawler/settings.py` and adjust:

- **`DEPTH_LIMIT`** how many link hops away from a seed URL the spider may go
- **`STORAGE_THRESHOLD_MB`** soft cap on disk used by the `pages` folder; the spider stops when usage crosses this

Other useful knobs live in the same file (for example `DOWNLOAD_DELAY` and `CONCURRENT_REQUESTS_PER_DOMAIN`) if you want to be gentler on Wikipedia’s servers.

## Repo layout

| Path | Role |
|------|------|
| `requirements.txt` | Python deps (Scrapy, Beautiful Soup) |
| `run_wiki_crawler.sh` | Creates `venv` if needed, installs deps, runs wiki crawl to `output.json` |
| `crawling/scrapy.cfg` | Scrapy project config |
| `crawling/webcrawler/` | Settings, items, pipelines, middlewares |
| `crawling/webcrawler/spiders/wiki_spider.py` | Wikipedia spider (`name = wiki`) |

The spider only follows normal article URLs on `en.wikipedia.org` and skips namespaces like `Special:`, `Talk:`, and `Category:`.
