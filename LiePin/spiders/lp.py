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
        "Referer": "https://www.liepin.com/zhaopin/?init=-1&headckid=10309442b4fc4250&fromSearchBtn=2&pubTime=1&dqs=&ckid=39d0f06b122df002&degradeFlag=0&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EV6MwPcZ2ne9zYObRj7X8Rg&d_sfrom=search_fp_nvbar&d_ckId=5bbcb19abb610f06d82310563dd69691&d_curPage=0&d_pageSize=40&d_headId=c7ab2f94211c65707db04468969afec4&curPage=99",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    cookies_str = COOKIES_STR
    regSpace = re.compile(r'([\s\r\n\t])+')

    def start_requests(self):
        base_url = 'https://www.liepin.com/zhaopin/?init=-1&headckid=10309442b4fc4250&fromSearchBtn=2&pubTime=1&dqs=&ckid=48be21f35417fec6&degradeFlag=0&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EV6MwPcZ2ne9zYObRj7X8Rg&d_sfrom=search_fp_nvbar&d_ckId=5bbcb19abb610f06d82310563dd69691&d_curPage=97&d_pageSize=40&d_headId=c7ab2f94211c65707db04468969afec4&curPage={curr_page}'
        for page in range(0, 100):
            yield Request(
                url=base_url.format(curr_page=page),
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse
            )

    def parse(self, response):

        _extrat = partial(extrat, response)
        item = LiepinItem()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item['link'] = _extrat('//div[@class="job-info"]/h3/a/@href')
        item['post_time'] = _extrat('//time/@title')
        item['job_name'] = _extrat('//div[@class="job-info"]/h3/a/text()')
        salary_place_education_experience = _extrat('//p[@class="condition clearfix"]/@title')
        item['salary'] = salary_place_education_experience[0]
        item['place'] = salary_place_education_experience[1]
        item['education'] = salary_place_education_experience[2]
        item['experience'] = salary_place_education_experience[3]
        item['company_name'] = _extrat('//p[@class="company-name"]/a/text()')
        # todo 将每个项进行解析并去掉\t等符号
        item['advantage'] = _extrat('//p[@class="temptation clearfix"]')
        item['id'] = [base64.b32encode((n + c).encode("utf-8")) for n, c in zip(item['job_name'], item['company_name'])]
        other_info = [self.parse_other(url) for url in item['link']]
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        for info in other_info:
            list1.append(info[0])
            list2.append(info[1])
            list3.append(info[2])
            list4.append(info[3])
        item['company_address'] = list1
        item['company_size'] = list2
        item['job_content'] = list3
        item['company_industry'] = list4
        yield item

    def parse_other(self, url):
        response = requests.get(url)
        select = Selector(response)
        job_content = select.xpath('//div[@class="content content-word"]')[0].xpath("./text()").extract()
        company_address = select.xpath('//ul[@class="new-compintro"]/li[3]/text()').extract()
        company_size = select.xpath('//ul[@class="new-compintro"]/li[2]/text()').extract()
        company_industry = select.xpath('//ul[@class="new-compintro"]/li[1]/a/text()').extract()
        return company_address, company_size, job_content, company_industry

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
