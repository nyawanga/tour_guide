# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EatoutItem(scrapy.Item):
    # define the fields for your item here like:
    restraunt_name = scrapy.Field()
    location = scrapy.Field()
    cuisine = scrapy.Field()
    telephone = scrapy.Field()
    description = scrapy.Field()
    website = scrapy.Field()
    facebook = scrapy.Field()
    facilities = scrapy.Field()
    operation_hours = scrapy.Field()

