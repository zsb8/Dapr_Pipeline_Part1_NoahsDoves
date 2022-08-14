# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobpostingsItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    url = scrapy.Field()
    jobTitle = scrapy.Field()
    issuer = scrapy.Field()
    postedDate = scrapy.Field()
    expiryDate = scrapy.Field()
    location = scrapy.Field()
    street = scrapy.Field()
    regionLocality = scrapy.Field()
    postalCode = scrapy.Field()
    description = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    timestamp = scrapy.Field()

