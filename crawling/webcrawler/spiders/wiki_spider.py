from pathlib import Path
from webcrawler.items import WebcrawlerItem
import scrapy
from scrapy.exceptions import CloseSpider
from datetime import datetime

folder = Path("pages")
folder.mkdir(parents=True, exist_ok=True)

BLOCKED_NAMESPACES = [
    "Special:", "Wikipedia:", "Help:", "Talk:", "User:",
    "User_talk:", "Wikipedia_talk:", "File:", "File_talk:",
    "Category:", "Category_talk:", "Portal:", "Draft:",
    "Template:", "Template_talk:", "Module:", "MOS:"
]

def is_valid_wiki_article(url):
    if "en.wikipedia.org" not in url:
        return False
    if "/wiki/" not in url:
        return False
    path = url.split("/wiki/")[-1]
    if not path or path.startswith("#"):
        return False
    for ns in BLOCKED_NAMESPACES:
        if path.startswith(ns):
            return False
    return True

def load_seed_urls(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


class Spider_Wiki_Scraper(scrapy.Spider):
    name = "wiki"

    #Loop through all seed_urls
    async def start(self):
        seed_urls = load_seed_urls("seed_urls.txt")
        self.all_ids = set()
        self._closing = False
        for url in seed_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})
    
    def _pages_storage_mb(self):
        return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file()) / (1024 * 1024)

    def _threshold_reached(self):
        threshold = self.settings.getfloat("STORAGE_THRESHOLD_MB", 500.0)
        used = self._pages_storage_mb()
        if used >= threshold:
            self.log(f"Storage limit reached: {used:.1f} MB / {threshold} MB. Stopping crawler.")
            return True
        return False


    def download_page(self, response):
        page = response.url.split("/")[-1]
        filename = f"Page-{page}.html"
        filepath = folder/filename
        Path(filepath).write_bytes(response.body)
        self.log(f"Saved file {filename}")

    def sanity_check_dupe(self, page_id):
        if page_id in self.all_ids:
            return True
        return False

    #Get HTML of pages and parse them
    def parse(self, response):
        if self._closing:
            return
        if self._threshold_reached():
            self._closing = True
            raise CloseSpider("storage_threshold_reached")

        page_id = response.css('meta[name="pageId"]::attr(content)').get()
        if page_id is None:
            page_id = response.url
        if self.sanity_check_dupe(page_id):
            self.log(f"Duplicate Page Found: {page_id}, Do not add to list")
            return
        self.all_ids.add(page_id)
        depth = response.meta.get("depth", 0) #default fallback to 0 if depth is not set
        page_item = WebcrawlerItem()

        page_item["url"] = response.url
        page_item["title"] = response.xpath("//title/text()").get()
        page_item["body"] = response.text
        page_item["crawled_at"] = datetime.now().isoformat()
        page_item["depth"] = depth

        #Domain Filtering and Link Extraction
        raw_links = response.xpath("//a/@href").getall()
        absolute_links = [response.urljoin(l) for l in raw_links if not l.startswith("#")]
        crawl_links = [l for l in absolute_links if is_valid_wiki_article(l)]
        page_item["outgoing_links"] = crawl_links

        for link in crawl_links:
            yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1})

        # add a download funciton here to save the page content to disk
        self.download_page(response)
        yield page_item
