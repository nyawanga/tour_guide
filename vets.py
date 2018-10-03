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

class Vetenerians(CrawlSpider):
    name = 'vets'
    next_page_xpath = '//div[@id="listing-paginator"]'
    start_urls = ['http://bizbookkenya.com/listing/veterinary-doctors',
                ]

    rules = (
         Rule(LinkExtractor(allow=(), restrict_xpaths= [next_page_xpath,] #rest$
                            ), callback = 'parse_next_page', follow = True
               ),)

#    def parse(self, response):
#        self.parse_next_page(response)

#        next_page = response.selector.xpath('//ul[@class="pagination"]/li//@href').extract()[-1]
#       # yield {'next': next_page}
#        if next_page:
#            yield scrapy.Request(next_page, callback= self.parse)

    def parse_next_page(self, response):
        vet_list = response.selector.xpath('//li[@class="listing-pane"]//@href').extract()    #all links in the page

        for url in vet_list:
#            yield scrapy.Request(url, callback = self.parse_restraunt)
            yield {'url': url}

    def parse_vet(self, response):
        items = {}
        main_table = response.selector.xpath('//div[@class="layout"]/section')
        titles = main_table.xpath('h2/text()').extract()
        details = main_table.xpath('p/text()').extract()
        for key, value in dict(zip(titles, details)):                            #iterate through the dictionary and assign items
            items[key] = value

        biz_activities = main_table.xpath('//p/a/text()').extract()              #get the business activiteis
        items['Business Activities'] = set(biz_activities)                       #reassign the items business activies items
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
