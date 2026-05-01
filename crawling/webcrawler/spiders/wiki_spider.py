from pathlib import Path
from webcrawler.items import WebcrawlerItem
import scrapy
from datetime import datetime

folder = Path("pages")
folder.mkdir(parents=True, exist_ok=True)

def load_seed_urls(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


class Spider_Wiki_Scraper(scrapy.Spider):
    name = "wiki"
    allowed_domains = ["wikipedia.org"]

    #Loop through all seed_urls
    async def start(self):
        seed_urls = load_seed_urls("seed_urls.txt")
        for url in seed_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"depth": 0})

    #Get HTML of pages and parse them
    def parse(self, response):
        depth = response.meta.get("depth", 0) #default fallback to 0 if depth is not set

        page_item = WebcrawlerItem()

        page_item["url"] = response.url
        page_item["title"] = response.xpath("//title/text()").get()
        page_item["body"] = response.xpath("//p//text()").getall()
        page_item["crawled_at"] = datetime.now().isoformat()
        page_item["depth"] = depth
        raw_links = response.xpath("//a/@href").getall()
        absolute_links = [response.urljoin(l) for l in raw_links if not l.startswith("#")]
        page_item["outgoing_links"] = absolute_links


        #based on my knolwedge scrappy the Scrappy has its own Queue system and it will handle the scheduling of requests. So we just need to yield new requests and Scrapy will take care of the rest.
        for link in absolute_links:
            #add some logic for dedepublication 
            # looking in settings.py to change the Depth limit to do full test
            yield scrapy.Request(url=link, callback=self.parse, meta={"depth": depth + 1}) #increase depth for outgoing links and puts it in the Queue

        yield page_item
