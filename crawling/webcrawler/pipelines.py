# Enable via ITEM_PIPELINES in settings.py when you need post-processing.
# https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class WebcrawlerPipeline:
    def process_item(self, item, spider):
        return item
