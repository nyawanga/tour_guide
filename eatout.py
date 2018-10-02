from bs4 import BeautifulSoup as bs
import html5lib
import re
from datetime import datetime as dt
import json

import scrapy
#from safaribookings.items import SafaribookingsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from lxml import html

class TourOperators(scrapy.Spider):
    name = 'eatout'
    baseurl = 'https://www.safaribookings.com/p'
    next_page_xpath = '//ul[@class="pagination"]/li//@href'
    start_urls = ['https://eatout.co.ke/restaurants',
#                  'https://eatout.co.ke/restaurants?page=2'
                ]

    def parse(self, response):
        self.parse_next_page(response)

        next_page = response.selector.xpath('//ul[@class="pagination"]/li//@href').extract()[-1]
       # yield {'next': next_page}
        if next_page:
            yield scrapy.Request(next_page, callback= self.parse)

    def parse_next_page(self, response):
        restraunts = response.selector.xpath("//div/h4[@class='media-heading ']/a/@href").extract()
        names = response.selector.xpath("//div/h4[@class='media-heading ']/a/text()").extract()

        for link in restraunts:
#            yield scrapy.Request(url, callback = self.parse_restraunt)
            yield {'url': url}

    def parse_restraunt(self, response):
 #       items = SafaribookingsItem()
        items = {}
        loc = response.selector.xpath("//span[@class='address']/span/text()").extract()    #get the address
        items['location'] = re.sub("\s{2,}", " ", "".join((i for i in loc)).strip() )      #join the address and replace space character
        items['cuisine'] = response.selector.xpath("//p[@class='rest-details-cuisine no-link-color']/a/span/text()").extract()
        items['telephone'] = response.selector.xpath("//p/a[@itemprop='telephone']/text()").extract()
        items['description'] = response.selector.xpath("//div[@itemprop='description']/p/text()").extract_first()
        first_table = response.selector.xpath("//div[@class='row']")[0]
        cusine_xpath = first_table.xpath('//ul/li/h5')
        items['website'] = cusine_xpath.xpath('following-sibling::ul//a[@itemprop="url"]/@href').extract_first()
        items['facebook'] = cusine_xpath.xpath('following-sibling::ul//a[@target="_blank"]/@href').extract_first()
        facility = first_table.xpath('//div[@class="col-md-12"]//span/text()').extract()
        items['facilities'] = re.sub("\s{2,}", " ", "".join((i.strip() for i in facility)))
        days = sec_table.xpath('//tbody/tr/td/text()').re(r"[a-zA-Z]+")
        vals = sec_table.xpath('//tbody/tr/td/text()').re(r"[^a-zA-Z]+")
        hours = [re.sub("\xa0", "", i.strip()) for i in vals[:len(days)]]
        items['operation_hours'] = dict(zip(days, hours))
        yield items

    def parse_contact(self, response):
        res = requests.get(response)
        soup = bs(res.content, 'html5lib')
        contact_block = soup.find('div', {'class':'detail__content__block row'})
        try:
            contacts = contact_block.find_all('div')
            for contact in contacts:
                heading = contact.find('h5').text
            return heading
        except AttributeError as e:
            contacts = contact_block.find('div')
            heading = contacts.find('h5').text
            return heading
