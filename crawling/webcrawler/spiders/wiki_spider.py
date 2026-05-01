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
            yield scrapy.Request(url=url, callback=self.parse)

    #Get HTML of pages and parse them
    def parse(self, response) -> WebcrawlerItem:
        
        page_item = WebcrawlerItem()

        page_item["url"] = response.url
        page_item["title"] = response.xpath("//title/text()").get()
        page_item["body"] = response.xpath("//body//text()").getall()
        #page_item["creation_date"] = response.headers.get("Date", "").decode("utf-8")
        page_item["crawled_at"] = datetime.now().isoformat()
        page_item["depth"] = depth+1
        page_item["outgoing_links"] = response.xpath("//a/@href").getall()

        return page_item
