from bs4 import BeautifulSoup as bs
import html5lib
import re
from datetime import datetime as dt
import json

import scrapy
from safaribookings.items import SafaribookingsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from lxml import html

class TourOperators(CrawlSpider):
    name = 'touroperators'
    baseurl = 'https://www.safaribookings.com/p'
    next_page_xpath = '//div/a[@class= "btn btn--white btn--next"]'
    start_rls = ['https://www.safaribookings.com/operators/kenya/page/2/',
                  'https://www.safaribookings.com/operators/kenya/page/3/'
                ]

    rules = (
        Rule(LinkExtractor(allow=(), restrict_xpaths= [next_page_xpath,] #restrict_css = (".page-numbers", )
                          ), callback = 'parse_next_page', follow = True
             ),)

    def parse_next_page(self, response):
        operators = response.selector.xpath("//span[starts-with(@class, 'favorite-save hide show-ti')]/@data-id").extract()
        #yield {'operator': operators}
        for data_id in operators:
            url = "{}{}".format(self.baseurl, data_id)
#            yield scrapy.Request(url, callback = self.parse_operator)
            yield {'url': url}

    def parse_operator(self, response):
        items = SafaribookingsItem()
        items['operator_name']= response.selector.xpath("//div[@class= 'row']//h1[@itemprop='name']/span/text()").extract()[0]
        items['profile']= response.selector.xpath('//div/a[@rel = "nofollow"][contains(@href, "/profile")]/@href').extract_first()
        items['contact']= response.selector.xpath('//a[@title = "Contact"][contains(@href, "operator-contact")]/@href').extract_first()
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
