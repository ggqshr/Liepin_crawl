# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request, Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from LiePin.settings import USER_AGENT_POOL
import random
from LiePin import LiepinItem
from functools import partial
import base64
from LiePin.data5u import IPPOOL


def extrat(response, xpath):
    return response.xpath(xpath).extract()


headers = {
    "Host": "www.liepin.com",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "User-Agent": random.choice(USER_AGENT_POOL),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Referer": 'https://www.liepin.com/zhaopin/?init=-1&headckid=ebb4af279a07d4be&fromSearchBtn=2&sfrom=click-pc_homepage-centre_searchbox-search_new&ckid=ebb4af279a07d4be&degradeFlag=0&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=7cd3a89b67e7261f0646fe4114c38c34&d_curPage=0&d_pageSize=40&d_headId=7cd3a89b67e7261f0646fe4114c38c34&curPage=1',
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
def random_agent(request: Request):
    request.headers = headers
    thisip = random.choice(IPPOOL)
    request.meta["proxy"] = "http://" + thisip
    return request


class LpredisSpider(RedisCrawlSpider):
    name = 'lpredis'
    allowed_domains = ['liepin.com']
    redis_key = 'lpredis:start_urls'
    redis_batch_size = 64
    regSpace = re.compile(r'([\s\r\n\t])+')

    rules = (
        Rule(LinkExtractor(allow=r'https://www.liepin.com/zhaopin.*'), follow=True, process_request=random_agent),
        Rule(LinkExtractor(allow=r'^https://www.liepin.com/job.*'), follow=False, process_request=random_agent,
             callback="parse_item")
    )

    def parse_item(self, response):
        _extrat = partial(extrat, response)
        item = LiepinItem()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item['link'] = response.url
        item['job_name'] = _extrat("//div[@class='title-info']/h1/@title")[0]
        item['company_name'] = _extrat("//div[@class='title-info']/h3/a/@title")[0]
        item['post_time'] = _extrat('//p[@class="basic-infor"]/time/@title')
        item['salary'] = self.replace_all_n(_extrat('//p[@class="job-item-title"]/text()'))
        item['place'] = _extrat('//p[@class="basic-infor"]/span/a/text()')

        info_text = _extrat('//div[@class="job-qualifications"]//span/text()')
        item['education'] = info_text[0]
        item['experience'] = info_text[1]

        item['advantage'] = "_".join(_extrat("//ul[@class='comp-tag-list clearfix']//li/span/text()"))

        item['id'] = base64.b32encode((item['job_name'] + item['company_name']).encode("utf-8")).decode("utf-8")

        item['job_content'] = response.xpath('//div[@class="content content-word"]')[0].xpath("./text()").extract()
        item['job_content'] = self.replace_all_n(item['job_content'])
        item['company_address'] = response.xpath('//ul[@class="new-compintro"]/li[3]/text()').extract()
        item['company_size'] = response.xpath('//ul[@class="new-compintro"]/li[2]/text()').extract()
        item['company_industry'] = response.xpath('//ul[@class="new-compintro"]/li[1]/a/text()').extract()

        yield item

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            if type(text) == str:
                rel = re.sub(self.regSpace, "", text)
                return rel
            elif type(text) == list:
                return "".join([re.sub(self.regSpace, "", t) for t in text])
        except TypeError as e:
            return "空"
