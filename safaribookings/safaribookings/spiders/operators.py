from bs4 import BeautifulSoup as bs
import html5lib
import re
from datetime import datetime as dt
import json
import requests

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
    start_urls = ['https://www.safaribookings.com/operators/kenya/page/2/',
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
            yield scrapy.Request(url, callback = self.parse_operator)
            #yield {'url': url}

    def parse_operator(self, response):
        items = SafaribookingsItem()
        items['operator_name']= response.selector.xpath("//div[@class= 'row']//h1[@itemprop='name']/span/text()").extract_first()
        items['website'] = response.selector.xpath('//dd/a[@class="external"]/@href').extract_first()
        destinations = response.selector.xpath('//dd[@class="destinations hide show-t"]//@title').extract()
        items['destinations'] = list(set(destinations))
        profile_url = response.selector.xpath('//div/a[@rel = "nofollow"][contains(@href, "/profile")]/@href').extract_first()
        items['profile'] = self.parse_profile(profile_url)           #use the parse_profie function to get the profile text
        contact_url = response.selector.xpath('//a[@title = "Contact"][contains(@href, "operator-contact")]/@href').extract_first()
        items['contact'] = self.parse_contact(contact_url)           #use parse_contact function to the the contact information
        yield items

    def parse_contact(self, response):
        res = requests.get(response)
        soup = bs(res.content, 'html5lib')
        contacts = {}
        #try:
        contact_block = soup.find_all('div', {'class':'detail__content__block row'})
        try:
            if len(contact_block) > 1:
                for index, contact in enumerate(contact_block):
                    prefix = "contact_{}".format(index)
                    contacts[prefix] = re.sub("\s{2,}", " ", contact.get_text().strip())
                return contacts
            else:
                contact_block = soup.find('div', {'class':'detail__content__block row'})
                c_detail = contact_block.get_text().strip()                               #get contact
                final_contact = re.sub("\s{2,}", " ", c_detail)                           #remove white spaces
                prefix = "contact_{}".format(0)
                contacts[prefix] =  final_contact
                return contacts 

        except Exception as e:                                                        #in case it is only one contact address
            contact_block = soup.find('div', {'class':'detail__content__block row'})
            c_detail = contact_block.get_text().strip()                               #get contact
            final_contact = re.sub("\s{2,}", " ", c_detail)                           #remove white spaces
            prefix = "contact_{}".format(0)
            contacts[prefix] =  final_contact                                         #make it into a dictionary
            return contacts
        except Exception as e:                                                        #in case of uncaptured exceptions
            print("Got an exception as {}".format(e))

    def parse_profile(self, response):
        res= requests.get(response)
        soup = bs(res.content, 'html5lib')
#        content = soup.find('div', {'class': 'profile-tab'}).div.next_sibling.next_sibling.get_text().strip()
        contact = soup.find('div', {'class': 'profile-tab'}).get_text().strip()
        contact = re.sub("\s{2,}", " ", contact)
        return contact
