from pathlib import Path
from webcrawler.items import WebcrawlerItem
import scrapy
from datetime import datetime
from scrapy.exceptions import CloseSpider

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

    #Loop through all seed_urls
    async def start(self):
        seed_urls = load_seed_urls("seed_urls.txt")
        self.all_ids = []
        for url in seed_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})
    
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
        if self.pages_crawled >= self.max_pages:
            raise CloseSpider("max_pages_reached")

        page_id = response.css('meta[name="pageId"]::attr(content)').get()
        if self.sanity_check_dupe(page_id):
            self.log(f"Duplicate Page Found: {page_id}, Do not add to list")
            return
        
        depth = response.meta.get("depth", 0) #default fallback to 0 if depth is not set
        if depth > self.max_depth:
            return

        self.pages_crawled += 1
        page_item = WebcrawlerItem()

        page_item["url"] = response.url
        page_item["title"] = response.xpath("//title/text()").get()
        page_item["body"] = response.text
        page_item["crawled_at"] = datetime.now().isoformat()
        page_item["depth"] = depth
        raw_links = response.xpath("//a/@href").getall()
        absolute_links = [response.urljoin(l) for l in raw_links if not l.startswith("#")]
        page_item["outgoing_links"] = absolute_links

        #based on my knolwedge, the Scrappy has its own Queue system and it will handle the scheduling of requests. So we just need to yield new requests and Scrapy will take care of the rest.
        for link in absolute_links:
        #     #add some logic for dedepublication 
        #     # looking in settings.py to change the Depth limit to do full test
            if depth < self.max_depth:
                yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1}) #increase depth for outgoing links and puts it in the Queue

        # add a download funciton here to save the page content to disk
        self.download_page(response)
        yield page_item
