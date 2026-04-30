from pathlib import Path

import scrapy

folder = Path("pages")
folder.mkdir(parents=True, exist_ok=True)

def load_seed_urls(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


class Spider_Wiki_Scraper(scrapy.Spider):
    name = "wiki"

    #Loop through all seed_urls
    async def start(self):
        seed_urls = load_seed_urls("seed_urls.txt")
        for url in seed_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    #Get HTML of pages and parse them
    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = f"Page-{page}.html"
        filepath = folder/filename
        Path(filepath).write_bytes(response.body)
        self.log(f"Saved file {filename}")