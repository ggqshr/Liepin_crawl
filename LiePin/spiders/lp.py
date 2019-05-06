# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, Selector
from LiePin.settings import COOKIES_STR
import base64
from LiePin import LiepinItem
from functools import partial
import requests
import re


def extrat(response, xpath):
    return response.xpath(xpath).extract()


class LpSpider(scrapy.Spider):
    name = 'lp'
    allowed_domains = ['liepin.com']
    headers = {
        "Host": "www.liepin.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Referer": 'https://www.liepin.com/zhaopin/?init=-1&headckid=ebb4af279a07d4be&fromSearchBtn=2&sfrom=click-pc_homepage-centre_searchbox-search_new&ckid=ebb4af279a07d4be&degradeFlag=0&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=7cd3a89b67e7261f0646fe4114c38c34&d_curPage=0&d_pageSize=40&d_headId=7cd3a89b67e7261f0646fe4114c38c34&curPage=1',
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    cookies_str = COOKIES_STR
    regSpace = re.compile(r'([\s\r\n\t])+')

    def start_requests(self):
        base_url = 'https://www.liepin.com/zhaopin/?init=-1&headckid=10309442b4fc4250&fromSearchBtn=2&pubTime=1&dqs=&ckid=48be21f35417fec6&degradeFlag=0&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EV6MwPcZ2ne9zYObRj7X8Rg&d_sfrom=search_fp_nvbar&d_ckId=5bbcb19abb610f06d82310563dd69691&d_curPage=1000&d_pageSize=40&d_headId=7cd3a89b67e7261f0646fe4114c38c34&curPage={curr_page}'
        for page in range(0, 1000):
            yield Request(
                url=base_url.format(curr_page=page),
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse,
            )

    def parse(self, response):

        _extrat = partial(extrat, response)
        item = LiepinItem()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item['link'] = _extrat('//div[@class="job-info"]/h3/a/@href')
        item['post_time'] = _extrat('//time/@title')
        item['job_name'] = _extrat('//div[@class="job-info"]/h3/a/text()')
        salary_place_education_experience_list = list(
            map(lambda x: x.split("_"), _extrat('//p[@class="condition clearfix"]/@title')))
        item['salary'] = [i[0] for i in salary_place_education_experience_list]
        item['place'] = [i[1] for i in salary_place_education_experience_list]
        item['education'] = [i[2] for i in salary_place_education_experience_list]
        item['experience'] = [i[3] for i in salary_place_education_experience_list]
        item['company_name'] = _extrat('//p[@class="company-name"]/a/text()')
        item['advantage'] = response.xpath('//p[@class="temptation clearfix"]')
        item['advantage'] = ["_".join(node.xpath(".//span/text()").extract()) for node in item['advantage']]
        if item['advantage'] != 40:
            item['advantage'].append(["领导好"])
        item['id'] = [base64.b32encode((n + c).encode("utf-8")).decode("utf-8") for n, c in
                      zip(item['job_name'], item['company_name'])]
        all_data = [{key: item[key][index] for key in item.keys()} for index in range(len(item['id']))]

        for link in all_data:
            parse_other = partial(self._parse_other, LiepinItem(link))
            yield Request(
                url=link['link'],
                headers=self.headers,
                callback=parse_other,
                dont_filter=True
            )

    def _parse_other(self, item, response):
        item['job_content'] = response.xpath('//div[@class="content content-word"]')[0].xpath("./text()").extract()
        item['company_address'] = response.xpath('//ul[@class="new-compintro"]/li[3]/text()').extract()
        item['company_size'] = response.xpath('//ul[@class="new-compintro"]/li[2]/text()').extract()
        item['company_industry'] = response.xpath('//ul[@class="new-compintro"]/li[1]/a/text()').extract()
        yield item

    @property
    def cookies_dict(self):
        str_list = self.cookies_str.split(";")
        result = {}
        for s in str_list:
            split_result = s.split("=", 1)
            result[split_result[0].strip()] = split_result[1].strip()
        return result

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            rel = re.sub(self.regSpace, "", text)
            return rel
        except TypeError as e:
            return "空"
