# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    depth = scrapy.Field()
    crawled_at = scrapy.Field()
    outgoing_links = scrapy.Field()
    pass


