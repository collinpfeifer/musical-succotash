# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Therapist(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    phone_number = scrapy.Field()
    address = scrapy.Field()
    psychology_today_profile_link = scrapy.Field()
    credentials = scrapy.Field()
    session_fee = scrapy.Field()
    emails = scrapy.Field()
    personal_website = scrapy.Field()
