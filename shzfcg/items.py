# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShzfcgCategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    publishDate = scrapy.Field()
    pathName = scrapy.Field()
    districtName = scrapy.Field()
    type = scrapy.Field()
    budgetprice = scrapy.Field()
    highprice = scrapy.Field()
    winningprice = scrapy.Field()
