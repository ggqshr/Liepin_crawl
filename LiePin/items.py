# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LiepinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 总的Xpath//ul[@class="sojob-list"]/li，应该共有40个，每个对应一个job信息
    id = scrapy.Field()  # 由工作名+公司名 生成的base32编码
    link = scrapy.Field()  # .//div[@class="job-info"]/h3/a/@href
    post_time = scrapy.Field()  # .//time/@title
    job_name = scrapy.Field()  # .//div[@class="job-info"]/h3/a/text()
    salary = scrapy.Field()  # .//p[@class="condition clearfix"]/@title 按照_进行分割的第一个字段
    place = scrapy.Field()  # .//p[@class="condition clearfix"]/@title 按照_进行分割的第二个字段
    education = scrapy.Field()  # .//p[@class="condition clearfix"]/@title 按照_进行分割的第三个字段
    experience = scrapy.Field()  # .//p[@class="condition clearfix"]/@title 按照_进行分割的第四个字段
    advantage = scrapy.Field()  # .//p[@class="temptation clearfix"]//span/text()
    company_name = scrapy.Field()  # .//p[@class="company-name"]/a/text()
    # 深一层页面
    company_address = scrapy.Field()
    company_size = scrapy.Field()
    job_content = scrapy.Field()
    company_industry = scrapy.Field()
