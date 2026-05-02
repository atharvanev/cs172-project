# CS 172 Project - Web Crawler

This repository contains a Scrapy-based HTML web crawler. It starts from a list of seed URLs, traverses hyperlinks up to a configurable hop depth, saves crawled pages to disk, and exports structured page metadata.

## Team Members

- Atharva Nevasekar
- Nikhil Rao
- Austin Le
- David Lee
- Brandon Sun

## Features

- Seed-based crawling from `crawling/seed_urls.txt`.
- Configurable crawl bounds with `max_pages` and `max_depth`.
- Optional hostname suffix filtering with `domain_suffixes` (for example `.edu` or `.gov`).
- Duplicate prevention using normalized URL tracking.
- Polite crawling defaults (`robots.txt` support and request delay).
- HTML page snapshot storage and JSON export of extracted fields.

## Project Structure

- `crawling/webcrawler/spiders/wiki_spider.py`: main crawl logic.
- `crawling/webcrawler/settings.py`: Scrapy configuration.
- `crawling/seed_urls.txt`: crawl starting URLs.
- `crawling/pages/`: saved HTML page snapshots.

## Setup

From the repository root:

```bash
bash setup.sh
source venv/bin/activate
```

## Seed URLs

Edit `crawling/seed_urls.txt` to change crawl starting points.

## Run the Crawler

From the repository root:

```bash
cd crawling
scrapy crawl wiki
scrapy crawl wiki -o output.json
scrapy crawl wiki -a max_pages=100 -a max_depth=2 -o output.json
scrapy crawl wiki -a domain_suffixes=.edu,.gov -a max_pages=50 -a max_depth=1 -o output.json
```

Runtime arguments:
- `max_pages`: maximum total pages to schedule/fetch before stopping (default: `50`)
- `max_depth`: maximum hyperlink depth from seed URLs (default: `1`)
- `domain_suffixes`: comma-separated hostname suffix filters like `.edu` or `.gov` (optional). When unset, the crawler uses Scrapy `allowed_domains` (`wikipedia.org` for this spider). When set, only `http/https` URLs whose hostnames end with one of the suffixes are scheduled, and outgoing links recorded in JSON follow the same filter.

## Output

- Crawled HTML files are saved to `crawling/pages/`.
- Structured crawl results are written to `output.json` when using `-o output.json`.

Example output record:

```json
{
  "url": "https://example.edu/page.html",
  "title": "Example Page",
  "body": "stripped text content...",
  "crawled_at": "2025-04-28T10:30:00",
  "depth": 2,
  "outgoing_links": [
    "https://example.edu/other.html"
  ]
}
```

## Current Crawler Behavior

- Obeys `robots.txt`.
- Uses polite crawl rate (`DOWNLOAD_DELAY = 1`, `CONCURRENT_REQUESTS_PER_DOMAIN = 1`).
- Deduplicates crawls using normalized URLs.
- Skips non-HTTP/HTTPS links during scheduling.

When `domain_suffixes` is enabled, swap `seed_urls.txt` to URLs on hosts that satisfy the suffix rule; Wikipedia seeds plus a `.edu`-only filter will not crawl anything useful.

## Limitations

- JavaScript-heavy pages may require a headless browser for full rendering.
- Crawl coverage depends on seed URL selection.
- Domain policies and robots rules can reduce reachable pages.

