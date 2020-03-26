# -*- coding: utf-8 -*-
import base64
import random
import re
from functools import partial, wraps

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from LiePin import LiepinItem
from LiePin.settings import COOKIES_STR
from LiePin.settings import USER_AGENT_POOL
from LiePin.settings import city_code_list


def extrat(response, xpath):
    return response.xpath(xpath).extract()


def catch_reach_max(func):
    """
    再所有的回调执行前执行一段逻辑，检查是否今天的代理都用完了，如果用完了就关闭爬虫
    :param func:
    :return:
    """
    @wraps(func)
    def ww(*args, **kwargs):
        response = args[1]
        if "reach_max" in response.meta.keys():
            raise CloseSpider("reach_max_proxy")
        return func(*args)

    return ww


class LpSpider(scrapy.Spider):
    name = 'lp'
    allowed_domains = ['liepin.com']
    headers = {
        "Host": "www.liepin.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "User-Agent": random.choice(USER_AGENT_POOL),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    cookies_str = COOKIES_STR
    regSpace = re.compile(r'([\s\r\n\t])+')

    def start_requests(self):
        base_url = "https://www.liepin.com/zhaopin/?init=-1&headckid=468f33e95eee9659&flushckid=1&fromSearchBtn=2&dqs={city}&ckid=8ee212dfe04606d9&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EF5FSJAXvyHmQyODXqGxdVw&d_sfrom=search_fp&d_ckId=bee571934d780d9bcbd9a225720f8093&d_curPage=0&d_pageSize=40&d_headId=aeda655e5fe8976cbd21f04db0a14233"
        for city in city_code_list.values():
            yield Request(
                url=base_url.format(city=city),
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse_by_industry,
                # meta={"proxy": "http://" + random.choice(IPPOOL)}
            )

    @catch_reach_max
    def parse_by_industry(self, response):
        """
        对原始的url按照不同的行业进行爬取，为了爬取更多的数据
        :param response:
        :return:
        """
        result_count = response.xpath("//p[@class='result-count']/em/text()").extract_first()  # 获得当前结果的总数
        if result_count == "10000+":  # 如果结果很多，就按照不同专业爬取
            all_industry = response.xpath("//dd[@class='short-dd select-industry']/ul/li")  # 获取所有的大类别
            all_industry_url_list = []
            for industry in all_industry:
                url = industry.xpath(".//a/@href").extract()
                all_industry_url_list.extend(url)
            all_industry_url_list = ["https://www.liepin.com" + url for url in all_industry_url_list]
            for url in all_industry_url_list:
                yield Request(
                    url=url,
                    headers=self.headers,
                    cookies=self.cookies_dict,
                    callback=self.parse_by_city_area,
                )
        else:
            yield Request(
                url=response.url,
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse,
                priority=3,
            )

    @catch_reach_max
    def parse_by_city_area(self, response):
        """
        如果城市这一级别下还有许多数据，就按照城市的区来进行爬取
        :param response:
        :return:
        """
        result_count = response.xpath("//p[@class='result-count']/em/text()").extract_first()  # 获得当前结果的总数
        if result_count == "10000+":
            all_area = response.xpath("//dd[@data-param='dqs']//a")
            if all_area == []:
                yield Request(
                    url=response.url,
                    headers=self.headers,
                    cookies=self.cookies_dict,
                    callback=self.parse,
                    priority=3,
                )
            else:
                all_area_url = []
                for url in all_area:
                    this_url = url.xpath("./@href").extract_first()
                    all_area_url.append("https://www.liepin.com" + this_url)
                for url in all_area_url:
                    yield Request(
                        url=url,
                        headers=self.headers,
                        cookies=self.cookies_dict,
                        callback=self.parse_by_money,
                    )
        else:
            yield Request(
                url=response.url,
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse,
                priority=3,
            )

    @catch_reach_max
    def parse_by_money(self, response):
        """
        按照工资数进行爬取
        :param response:
        :return:
        """
        result_count = response.xpath("//p[@class='result-count']/em/text()").extract_first()  # 获得当前结果的总数
        if result_count == "10000+":
            all_money = response.xpath("//dd[@data-param='salary']/a")
            all_money_url = []
            for url in all_money:
                this_url = url.xpath("./@href").extract_first()
                all_money_url.append("https://www.liepin.com" + this_url)
            for page in range(0, 100):
                for url in all_money_url:
                    yield Request(
                        url=f"{url}&curPage={page}",
                        headers=self.headers,
                        cookies=self.cookies_dict,
                        callback=self.parse,
                        priority=3,
                    )
        else:
            yield Request(
                url=response.url,
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse,
                priority=3,
            )

    @catch_reach_max
    def parse(self, response):

        _extrat = partial(extrat, response)
        item = LiepinItem()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item['link'] = _extrat('//div[@class="job-info"]/h3/a/@href')
        item['post_time'] = _extrat('//time/@title')
        item['job_name'] = [self.replace_all_n(tt) for tt in _extrat('//div[@class="job-info"]/h3/a/text()')]
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
        item['id'] = [base64.b32encode((n + c + t).encode("utf-8")).decode("utf-8") for n, c, t in
                      zip(item['job_name'], item['company_name'], item['post_time'])]
        try:
            all_data = [{key: item[key][index] for key in item.keys()} for index in range(len(item['id']))]
        except IndexError as e:
            all_data = [{key: item[key][index] for key in item.keys()} for index in
                        range(min([len(v) for v in item.values()]))]

        for link in all_data:
            if re.findall(r"^/", link['link']) != []:
                link['link'] = "https://www.liepin.com" + link['link']
            yield Request(
                url=link['link'],
                headers=self.headers,
                callback=self._parse_other,
                dont_filter=True,
                priority=3,
                meta={"item": LiepinItem(link)}
            )
        # 如果下一页存在，就继续爬取下一页
        tag_a = response.xpath("//a[text()='下一页']")  # 获得下一页的a标签
        if not tag_a.xpath("./@class").extract():
            next_page_url = tag_a.xpath("./@href").extract_first()
            if next_page_url is None:
                return
            yield Request(
                url="https://www.liepin.com" + next_page_url,
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse,
                priority=2,
            )

    @catch_reach_max
    def _parse_other(self, response: Response):
        item = response.meta['item']
        if "该职位已暂停招聘" in response.text or "您访问的页面不存在或已删除" in response.text:
            yield item
        item['job_content'] = response.xpath('//div[@class="content content-word"]')[0].xpath("./text()").extract()
        item['job_content'] = self.replace_all_n(item['job_content'])
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
            if type(text) == str:
                rel = re.sub(self.regSpace, "", text)
                return rel
            elif type(text) == list:
                return "".join([re.sub(self.regSpace, "", t) for t in text])
        except TypeError as e:
            return "空"
