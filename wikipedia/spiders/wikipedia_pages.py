from scrapy.spiders import Spider
from scrapy.http import Request

from wikipedia.items import WikipediaItem
from bs4 import BeautifulSoup

import re

class PagesSpider(Spider):
	name = "wikipedia_pages"
	start_urls = [
		"https://en.wikipedia.org/wiki/United_States",
		"https://en.wikipedia.org/wiki/Meme",
		"https://en.wikipedia.org/wiki/Game_of_Thrones"
	]

	allowed_domains = ["wikipedia.org"]

	visited_urls = set()
	body_link_selector = '(//div[@id="mw-content-text"]/p/a/@href)[position() < 100]'
	allowed_re = re.compile('https://en\.wikipedia\.org/wiki/'
							'(?!((File|Talk|Category|Portal|Special|'
							'Template|Template_talk|Wikipedia|Help|Draft):|Main_Page)).+')

	def parse(self, response):
		item = WikipediaItem()
		soup = BeautifulSoup(response.body, "lxml")

		item['url'] = response.url     
		item['name'] = soup.find("h1", {"id": "firstHeading"}).string
		item['description'] = BeautifulSoup(response.xpath('//div[@id="mw-content-text"]/p[1]').extract_first(), "lxml").text[:255] + "..."
		item['links'] = [y for y in [response.urljoin(x) for x in response.xpath(self.body_link_selector).extract() if x[0] != "#"] if self.allowed_re.match(y)]
		yield item

		self.visited_urls.add(response.url)
		print(len(self.visited_urls))
		

		for link in item['links']:
			if not link in self.visited_urls:
				yield Request(link, callback = self.parse)
				