# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
from __future__ import annotations

from typing import Any, Iterable

from scrapy import Request, Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Response
from scrapy.spidermiddlewares.base import BaseSpiderMiddleware


class WebcrawlerSpiderMiddleware(BaseSpiderMiddleware):
    """Uses ``BaseSpiderMiddleware`` (Scrapy 2.13+) for ``process_start`` / output plumbing.

    Override ``get_processed_request`` / ``get_processed_item`` for per-object logic.
    Enable in ``settings.py`` via ``SPIDER_MIDDLEWARES`` (pick order vs.
    ``SPIDER_MIDDLEWARES_BASE`` — see docs).
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> WebcrawlerSpiderMiddleware:
        mw = super().from_crawler(crawler)
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s", spider.name)

    def process_spider_input(self, response: Response, spider: Spider | None = None) -> None:
        return None

    def process_spider_exception(
        self,
        response: Response,
        exception: BaseException,
        spider: Spider | None = None,
    ) -> Iterable[Any] | None:
        return None

    def get_processed_request(self, request: Request, response: Response | None) -> Request | None:
        self.crawler.stats.inc_value("webcrawler/spider_mw_requests")
        return request

    def get_processed_item(self, item: Any, response: Response | None) -> Any:
        self.crawler.stats.inc_value("webcrawler/spider_mw_items")
        return item


class WebcrawlerDownloaderMiddleware:
    """Downloader hooks; inactive until listed under ``DOWNLOADER_MIDDLEWARES``."""

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> WebcrawlerDownloaderMiddleware:
        return cls()

    def process_request(self, request: Request, spider: Spider) -> Request | Response | None:
        return None

    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        return response

    def process_exception(
        self, request: Request, exception: BaseException, spider: Spider
    ) -> Request | Response | None:
        return None
