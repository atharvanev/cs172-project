# CS 172 Project - Web Crawler

This repository contains a Scrapy-based HTML web crawler (`wiki`). It reads seed URLs from a file, follows links up to a configurable hop depth, saves each crawled HTML response under a `pages/` directory, and can export structured fields to JSON (`-o …`).

## Team Members

- Atharva Nevasekar
- Nikhil Rao
- Austin Le
- David Lee
- Brandon Sun

## Features

- Seed-based crawling from `crawling/seed_urls.txt`.
- Bounds from spider arguments `max_pages` and `max_depth`.
- Duplicate reduction using normalized URLs plus `visited` / `scheduled` sets.
- Optional hostname suffix filtering with `domain_suffixes` (e.g. `.edu`, `.gov`).
- Polite defaults: obey `robots.txt`, delay between downloads, limited concurrency per domain.
- Saves raw HTML snapshots to disk and emits JSON/XML/etc. feeds via Scrapy’s `-o` option.

## Project layout

- `crawling/webcrawler/spiders/wiki_spider.py` — spider implementation.
- `crawling/webcrawler/settings.py` — Scrapy settings (delay, concurrency, encoding, depth).
- `crawling/seed_urls.txt` — one seed URL per line (blank lines skipped).
- `crawling/pages/` — created at runtime relative to where you run `scrapy`; when you `cd crawling` first, snapshots land here (`crawling/pages/` from repo root).

## Setup

From the repo root:

```bash
bash setup.sh
source venv/bin/activate
```

If `scrapy` is missing inside the venv (the repo’s script uses bare `pip` after creating the venv), install dependencies explicitly into the environment:

```bash
./venv/bin/pip install -r requirements.txt
```

## Seeds

Edit `crawling/seed_urls.txt`. With `domain_suffixes` unset, seeds should be on **`*.wikipedia.org`** hosts so Scrapy’s default `allowed_domains` matches.

## Running

Always run Scrapy **from `crawling/`** so `seed_urls.txt` and the `pages/` folder resolve correctly.

```bash
cd crawling
scrapy crawl wiki
scrapy crawl wiki -o output.json
scrapy crawl wiki -a max_pages=100 -a max_depth=2 -o output.json
scrapy crawl wiki -a domain_suffixes=.edu,.gov -a max_pages=50 -a max_depth=1 -o output.json
```

### Spider arguments

- **`max_pages`** (default `50`): closes the crawl (`CloseSpider`) once this many **unique pages** have been accepted for scraping—after redirects, duplicates, and off-policy redirects are skipped, and after `duplicate` skips (those may still have been downloaded earlier). It is not a strict cap on downloader requests queued ahead of time.
- **`max_depth`** (default `1`): seeds are depth `0`; each followed link increments depth. Scrapy global `DEPTH_LIMIT` is left at `0` so depth is controlled only by this argument.
- **`domain_suffixes`** (optional): comma-separated suffix list (e.g. `.edu,gov`). Values are normalized to start with `.`. When **empty**, the spider keeps Scrapy restriction to `wikipedia.org`. When **set**, `allowed_domains` is cleared so cross-domain queues are allowed, and only `http/https` URLs whose hostnames end with a listed suffix are kept (seeds, link discovery, redirects to a final URL, and exported `outgoing_links`).

### Normalization used for URLs

- Drops URL fragments (`#…`).
- Lowercases scheme and host.
- Strips trailing `/` from paths unless the path is `/`.
- Preserves query strings as-is after normalization.

## Output

### HTML snapshots

Each saved page is stored as **`Page-{slug}-{16-hex-hash}.html`**, where `{slug}` comes from the last path segment and `{hash}` is derived from the normalized URL so different URLs do not collide on disk.

### JSON (or other feed) items

Exported records include whatever `WebcrawlerItem` defines. Example shape:

```json
{
  "url": "https://en.wikipedia.org/wiki/Example",
  "title": "Example - Wikipedia",
  "body": "<!DOCTYPE html>…",
  "crawled_at": "2026-05-02T15:00:00",
  "depth": 0,
  "outgoing_links": [
    "https://en.wikipedia.org/wiki/Other_page"
  ]
}
```

Notes:

- **`url`** is the normalized URL stored in items.
- **`body`** is the full HTML/text body from the HTTP response (`response.text`), not plain stripped text.

## Limitations

- Heavy JavaScript pages are not rendered in a browser.
- Crawl breadth depends heavily on seeds and `robots.txt`.
- Duplicate URL detection avoids re-processing the same normalized URL **in this spider**, but many similar URLs still differ before normalization.
