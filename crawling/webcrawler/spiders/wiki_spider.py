import hashlib
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urldefrag, urlparse, urlsplit, urlunsplit

import scrapy
from scrapy.exceptions import CloseSpider

from webcrawler.items import WebcrawlerItem

folder = Path("pages")
folder.mkdir(parents=True, exist_ok=True)


def _parse_domain_suffixes(raw):
    if not raw or not str(raw).strip():
        return []
    return [
        (s if s.startswith(".") else f".{s}")
        for p in str(raw).split(",")
        if (s := p.strip().lower())
    ]


class Spider_Wiki_Scraper(scrapy.Spider):
    name = "wiki"
    allowed_domains = ["wikipedia.org"]

    def __init__(self, max_pages=50, max_depth=1, domain_suffixes="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.domain_suffixes = _parse_domain_suffixes(domain_suffixes)
        self.pages_crawled = 0
        self.visited_urls = set()
        self.scheduled_urls = set()
        if self.domain_suffixes:
            self.allowed_domains = []

    def _suffix_ok(self, url):
        return not self.domain_suffixes or (
            (h := urlparse(url).hostname) is not None
            and any(h.lower().endswith(s) for s in self.domain_suffixes)
        )

    def normalize_url(self, url):
        clean, _ = urldefrag(url)
        p = urlsplit(clean)
        path = (p.path or "/").rstrip("/") or "/"
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, p.query, ""))

    def _outlinks(self, response):
        seen, acc = set(), []
        for raw in response.xpath("//a/@href").getall():
            if raw.startswith("#"):
                continue
            n = self.normalize_url(response.urljoin(raw))
            if (
                n in seen
                or urlsplit(n).scheme not in ("http", "https")
                or not self._suffix_ok(n)
            ):
                continue
            seen.add(n)
            acc.append(n)
        return acc

    def _follow(self, links, depth):
        if depth >= self.max_depth:
            return
        for link in links:
            if link in self.visited_urls or link in self.scheduled_urls:
                continue
            self.scheduled_urls.add(link)
            yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1})

    async def start(self):
        with open("seed_urls.txt") as f:
            for line in f:
                url = line.strip()
                if not url:
                    continue
                n = self.normalize_url(url)
                if n in self.scheduled_urls:
                    continue
                if not self._suffix_ok(n):
                    if self.domain_suffixes:
                        self.logger.info("Skipping seed outside domain_suffixes: %s", n)
                    continue
                self.scheduled_urls.add(n)
                yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})

    def download_page(self, response):
        n = self.normalize_url(response.url)
        dig = hashlib.sha256(n.encode()).hexdigest()[:16]
        last = urlsplit(n).path.strip("/").split("/")[-1] or "index"
        slug = (re.sub(r"[^\w.\-]", "_", last, flags=re.UNICODE).strip("_") or "page")[:120]
        dest = folder / f"Page-{slug}-{dig}.html"
        dest.write_bytes(response.body)
        self.log(f"Saved file {dest.name}")

    def parse(self, response):
        if self.pages_crawled >= self.max_pages:
            raise CloseSpider("max_pages_reached")
        cur = self.normalize_url(response.url)
        if not self._suffix_ok(cur):
            self.logger.info("Skipping response outside domain_suffixes: %s", cur)
            return
        if cur in self.visited_urls:
            self.log(f"Duplicate Page Found: {cur}, skipping")
            return
        depth = response.meta.get("depth", 0)
        if depth > self.max_depth:
            return
        self.visited_urls.add(cur)
        self.pages_crawled += 1
        out = self._outlinks(response)
        item = WebcrawlerItem()
        item["url"], item["title"], item["body"] = cur, response.xpath("//title/text()").get(), response.text
        item["crawled_at"], item["depth"], item["outgoing_links"] = (
            datetime.now().isoformat(),
            depth,
            out,
        )
        yield from self._follow(out, depth)
        self.download_page(response)
        yield item
