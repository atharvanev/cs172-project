import hashlib
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urldefrag, urlsplit, urlunsplit

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

    def __init__(self, max_pages=50, max_depth=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.pages_crawled = 0
        self.visited_urls = set()
        self.scheduled_urls = set()

    def normalize_url(self, url):
        clean_url, _fragment = urldefrag(url)
        parts = urlsplit(clean_url)
        normalized_path = parts.path or "/"
        if normalized_path != "/" and normalized_path.endswith("/"):
            normalized_path = normalized_path.rstrip("/")
        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                normalized_path,
                parts.query,
                "",
            )
        )

    #Loop through all seed_urls
    async def start(self):
        seed_urls = load_seed_urls("seed_urls.txt")
        for url in seed_urls:
            normalized_seed = self.normalize_url(url)
            if normalized_seed in self.scheduled_urls:
                continue
            self.scheduled_urls.add(normalized_seed)
            yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})
    
    def download_page(self, response):
        normalized = self.normalize_url(response.url)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        last_segment = (urlsplit(normalized).path.strip("/").split("/")[-1] or "index")
        slug = re.sub(r"[^\w.\-]", "_", last_segment, flags=re.UNICODE).strip("_")
        if not slug:
            slug = "page"
        slug = slug[:120]
        filename = f"Page-{slug}-{digest}.html"
        filepath = folder / filename
        filepath.write_bytes(response.body)
        self.log(f"Saved file {filename}")

    #Get HTML of pages and parse them
    def parse(self, response):
        if self.pages_crawled >= self.max_pages:
            raise CloseSpider("max_pages_reached")

        normalized_current = self.normalize_url(response.url)
        if normalized_current in self.visited_urls:
            self.log(f"Duplicate Page Found: {normalized_current}, skipping")
            return

        depth = response.meta.get("depth", 0) #default fallback to 0 if depth is not set
        if depth > self.max_depth:
            return

        self.visited_urls.add(normalized_current)
        self.pages_crawled += 1
        page_item = WebcrawlerItem()

        page_item["url"] = normalized_current
        page_item["title"] = response.xpath("//title/text()").get()
        page_item["body"] = response.text
        page_item["crawled_at"] = datetime.now().isoformat()
        page_item["depth"] = depth
        raw_links = response.xpath("//a/@href").getall()
        absolute_links = [response.urljoin(link) for link in raw_links if not link.startswith("#")]
        normalized_links = []
        seen_links = set()
        for link in absolute_links:
            normalized_link = self.normalize_url(link)
            if normalized_link in seen_links:
                continue
            seen_links.add(normalized_link)
            normalized_links.append(normalized_link)
        page_item["outgoing_links"] = normalized_links

        #based on my knolwedge, the Scrappy has its own Queue system and it will handle the scheduling of requests. So we just need to yield new requests and Scrapy will take care of the rest.
        for link in normalized_links:
        #     #add some logic for dedepublication 
        #     # looking in settings.py to change the Depth limit to do full test
            if depth < self.max_depth:
                if link in self.visited_urls or link in self.scheduled_urls:
                    continue
                self.scheduled_urls.add(link)
                yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1}) #increase depth for outgoing links and puts it in the Queue

        # add a download funciton here to save the page content to disk
        self.download_page(response)
        yield page_item
