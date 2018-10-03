from bs4 import BeautifulSoup as bs
import html5lib
import re
from datetime import datetime as dt
import json

import scrapy
from vets.items import VetsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from lxml import html

class Vetenerians(CrawlSpider):
    name = 'vets'
    baseurl = 'http://bizbookkenya.com'
    next_page_xpath = '//div[@id="listing-paginator"]'
    start_urls = ['http://bizbookkenya.com/listing/veterinary-doctors',
                ]

    rules = (
         Rule(LinkExtractor(allow=(), restrict_xpaths= [next_page_xpath,] #rest$
                            ), callback = 'parse_next_page', follow = True
               ),)

    def parse_next_page(self, response):
        vet_list = response.selector.xpath('//li[@class="listing-pane"]//@href').extract()    #all links in the page

        for vet in vet_list:
            url = "{}{}".format(self.baseurl, vet)
            yield scrapy.Request(url, callback = self.parse_vets)
#            yield {'url': url}

    def parse_vets(self, response):
        items = VetsItem()
        main_table = response.selector.xpath('//div[@class="layout"]/section')
        titles = main_table.xpath('h4/text()').extract()
        details = main_table.xpath('p/text()').extract()
        for key, value in dict(zip(titles, details)).items():              #iterate through the dictionary and assign items
            key_name = self.rename_details_title(key)
            items[key_name] = value

        biz_activities = main_table.xpath('//p/a/text()').extract()              #get the business activiteis
        items['business_activity'] = set(biz_activities)                       #reassign the items business activies items
        yield items

    def rename_details_title(self, details):
        if re.search(r"company", details.lower() ):
            return 'company'
        elif re.search(r"address", details.lower() ):
            return  "address"
        elif re.search(r"box", details.lower() ):
            return "po_box"
        elif re.search(r"phone", details.lower() ):
            return "telephone"
        elif re.search(r"fax", details.lower() ):
            return "fax"
        elif re.search(r"business", details.lower() ):
            return "business_activity"
        else:
            return "unknown"

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
