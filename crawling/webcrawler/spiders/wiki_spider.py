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


def load_seed_urls(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


class Spider_Wiki_Scraper(scrapy.Spider):
    name = "wiki"
    allowed_domains = ["wikipedia.org"]

    def __init__(self, max_pages=50, max_depth=1, domain_suffixes="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.domain_suffixes = self._parse_domain_suffixes(domain_suffixes)
        self.pages_crawled = 0
        self.visited_urls = set()
        self.scheduled_urls = set()
        if self.domain_suffixes:
            self.allowed_domains = []

    @staticmethod
    def _parse_domain_suffixes(raw):
        if not raw or not str(raw).strip():
            return []
        out = []
        for part in str(raw).split(","):
            s = part.strip().lower()
            if not s:
                continue
            out.append(s if s.startswith(".") else f".{s}")
        return out

    def _host_matches_suffixes(self, url):
        hostname = urlparse(url).hostname
        if hostname is None:
            return False
        h = hostname.lower()
        return any(h.endswith(suf) for suf in self.domain_suffixes)

    def _suffix_policy_ok(self, url):
        return not self.domain_suffixes or self._host_matches_suffixes(url)

    def _followable_http(self, normalized):
        return urlsplit(normalized).scheme in ("http", "https") and self._suffix_policy_ok(
            normalized
        )

    def normalize_url(self, url):
        clean_url, _ = urldefrag(url)
        parts = urlsplit(clean_url)
        path = parts.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                path,
                parts.query,
                "",
            )
        )

    def _outlinks(self, response):
        seen = set()
        out = []
        for raw in response.xpath("//a/@href").getall():
            if raw.startswith("#"):
                continue
            n = self.normalize_url(response.urljoin(raw))
            if n in seen or not self._followable_http(n):
                continue
            seen.add(n)
            out.append(n)
        return out

    def _enqueue_follows(self, links, depth):
        if depth >= self.max_depth:
            return
        for link in links:
            if link in self.visited_urls or link in self.scheduled_urls:
                continue
            self.scheduled_urls.add(link)
            yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1})

    async def start(self):
        for url in load_seed_urls("seed_urls.txt"):
            n = self.normalize_url(url)
            if n in self.scheduled_urls:
                continue
            if not self._suffix_policy_ok(n):
                if self.domain_suffixes:
                    self.logger.info("Skipping seed outside domain_suffixes: %s", n)
                continue
            self.scheduled_urls.add(n)
            yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})

    def download_page(self, response):
        normalized = self.normalize_url(response.url)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        last = urlsplit(normalized).path.strip("/").split("/")[-1] or "index"
        slug = (re.sub(r"[^\w.\-]", "_", last, flags=re.UNICODE).strip("_") or "page")[:120]
        filename = f"Page-{slug}-{digest}.html"
        path = folder / filename
        path.write_bytes(response.body)
        self.log(f"Saved file {filename}")

    def parse(self, response):
        if self.pages_crawled >= self.max_pages:
            raise CloseSpider("max_pages_reached")

        current = self.normalize_url(response.url)
        if not self._suffix_policy_ok(current):
            self.logger.info("Skipping response outside domain_suffixes: %s", current)
            return
        if current in self.visited_urls:
            self.log(f"Duplicate Page Found: {current}, skipping")
            return

        depth = response.meta.get("depth", 0)
        if depth > self.max_depth:
            return

        self.visited_urls.add(current)
        self.pages_crawled += 1

        outgoing = self._outlinks(response)
        item = WebcrawlerItem()
        item["url"] = current
        item["title"] = response.xpath("//title/text()").get()
        item["body"] = response.text
        item["crawled_at"] = datetime.now().isoformat()
        item["depth"] = depth
        item["outgoing_links"] = outgoing
        yield from self._enqueue_follows(outgoing, depth)
        self.download_page(response)
        yield item
