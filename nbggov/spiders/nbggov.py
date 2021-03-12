import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nbggov.items import Article


class NbggovSpider(scrapy.Spider):
    name = 'nbggov'
    start_urls = ['https://www.nbg.gov.ge/index.php?m=339']

    def parse(self, response):
        links = response.xpath('//a[@class="n_text"][2]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//table[@class="pagenary"]//td[last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//table[@id="news_id"]//td/div[1]//div[3]//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//b//text()[1]').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@id="_news_text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
