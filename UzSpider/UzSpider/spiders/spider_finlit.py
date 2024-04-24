import scrapy
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
from scrapy import Request
from .selenium import get_urls

# Get URLs based on writing system ('lat', 'krl', 'rus')
lang = 'lat'
urls = get_urls(lang)


class Article(scrapy.Item):
    """Defines the structure of an article item."""
    url = scrapy.Field()  # URL of the article
    title = scrapy.Field()  # Title of the article
    text = scrapy.Field()  # Text of the article
    access_date = scrapy.Field()  # Date when the article was accessed
    creation_date = scrapy.Field()  # Date when the article was created


class ArticleLoader(ItemLoader):
    """A custom Scrapy ItemLoader for loading information about an article."""

    # Use TakeFirst output processor as the default output processor
    default_output_processor = TakeFirst()

    # Define input and output processors for the title field
    title_in = MapCompose(remove_tags, str.strip)
    title_out = TakeFirst()

    # Define input and output processors for the text field
    text_in = MapCompose(remove_tags, lambda x: x.strip('\n'), str.strip)
    text_out = Join('\n')


class SpiderFinlitSpider(scrapy.Spider):
    """Main spider responsible for crawling the website and extracting article data."""
    name = "spider_finlit"
    allowed_domains = ["finlit.uz"]

    def __init__(self, ws=lang, **kwargs):
        """
        Initialize the spider with a default writing system and generate start URLs.

        Args:
            ws (str): Writing system ('lat', 'krl', 'rus').
        """
        self.ws = ws
        self.start_urls = ['https://finlit.uz' + i for i in urls]
        super().__init__(**kwargs)

    def start_requests(self):
        """
        Generate requests for each start URL.
        Yields:
            Request: Request for each start URL.
        """
        for url in self.start_urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        """
        Parse the response from each URL and extract article data.

        Args:
            response (Response): Scrapy response object.

        Yields:
            Article: Extracted article data.
        """
        article = ArticleLoader(item=Article(), response=response)
        article.add_value('url', response.url)
        article.add_css('title', 'h1.h1.my-2.mb-3::text')
        article.add_css('text', 'div.news-detail-text p::text')
        article.add_value('access_date', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        date_texts = response.css('div.tags.tag-text.px-0.justify-content-start::text').getall()
        creation_date = [i.strip() for i in date_texts if i.strip()]

        article.add_value('creation_date', creation_date)

        yield article.load_item()
