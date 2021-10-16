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
from datetime import datetime


def extrat(response, xpath):
    return response.xpath(xpath).extract()

industry_code = [
    # 互联网的
    "1$040","1$420","1$010","1$030",
    # 电子
    "2$050","2$060","2$020",
    # 房地产
    "3$080""3$090""3$100",
    # 金融
    "4$130","4$140","4$150","4$430","4$500",
    # 消费品
    "5$190","5$240","5$200","5$210","5$220","5$460","5$470",
    # 汽车
    "6$350","6$360","6$180","6$340","6$370",
    # 服务
    "7$110","7$120","7$440","7$450","7$230","7$260","7$510",
    # 广告
    "8$070","8$170","8$380",
    # 交通
    "9$250","9$160","9$480",
    # 制药
    "10$270","10$280","10$290",
    # 能源
    "11$300","11$310","11$320","11$330","11$490",
    # 政府
    "12$390","12$410","12$400",
]

replace_dq_pattern = re.compile("(dq=)\d+")
replace_current_page_pattern = re.compile("(currentPage=)\d+")

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
        base_url = "https://www.liepin.com/zhaopin/?init=-1&headckid=468f33e95eee9659&flushckid=1&fromSearchBtn=2&dq={city}&ckid=8ee212dfe04606d9&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EF5FSJAXvyHmQyODXqGxdVw&d_sfrom=search_fp&d_ckId=bee571934d780d9bcbd9a225720f8093&d_curPage=0&d_pageSize=40&d_headId=aeda655e5fe8976cbd21f04db0a14233&pubTime=1"
        for city in city_code_list.values():
            yield Request(
                url=base_url.format(city=city),
                headers=self.headers,
                cookies=self.cookies_dict,
                callback=self.parse_by_industry,
                # meta={"proxy": "http://" + random.choice(IPPOOL)}
            )
    def judge_current_page_data_number(self,response)-> bool:
        items = response.xpath('//div[@class="job-list-item"]')
        return len(items) == 40

    def replace_url(self,pattern,url,target_code):
        return re.sub(pattern,"\g<1>%s" % target_code,url)

    @catch_reach_max
    def parse_by_industry(self, response):
        """
        对原始的url按照不同的行业进行爬取，为了爬取更多的数据
        :param response:
        :return:
        """
        need_to_query = self.judge_current_page_data_number(response)
        if need_to_query:  # 如果结果很多，就按照不同专业爬取
            all_industry_url_list = ["%s&industry=%s" % (response.url, code) for code in industry_code]
            all_industry_url_list.append(response.url)
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
        need_to_query = self.judge_current_page_data_number(response)
        if need_to_query:
            all_area = response.xpath('//div[text() = "区域"]/..//li[@data-key="dq"]/@data-code').getall()
            if all_area == []:
                yield Request(  
                    url=response.url,
                    headers=self.headers,
                    cookies=self.cookies_dict,
                    callback=self.parse,
                    priority=3,
                )
            else:
                for code in all_area:
                    yield Request(
                        url=self.replace_url(replace_dq_pattern,response.url,code.strip()),
                        headers=self.headers,
                        cookies=self.cookies_dict,
                        callback=self.parse_by_money,
                    )
                yield Request(
                    url=response.url,
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
        need_to_query = self.judge_current_page_data_number(response)
        if need_to_query:
            all_money = response.xpath('//li[@data-key="salary"]/@data-code').getall()
            all_money = set(all_money)
            for code in all_money:
                yield Request(
                    url="%s&salary=%s" % (response.url,code),
                    headers=self.headers,
                    cookies=self.cookies_dict,
                    callback=self.parse,
                    priority=3,
                )
            yield Request(
                url=response.url,
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
        all_job_item = response.xpath('//div[@class="job-list-item"]')
        now_time = datetime.now().strftime("%Y年%m月%d日")
        for job_item in all_job_item:
            item = LiepinItem()
            item['link'] = job_item.xpath('.//a[@data-nick="job-detail-job-info"]/@href').get()
            item['post_time'] = now_time
            item['job_name'] = job_item.xpath('.//div[@class="job-title-box"]/div[1]/@title').get()
            item['salary'] = job_item.xpath('.//span[@class="job-salary"]/text()').get()
            item['place'] = job_item.xpath('.//div[@class="job-dq-box"]/span[@class="ellipsis-1"]/text()').get()
            jobs_info = job_item.xpath('.//div[@class="job-labels-box"]//span')
            if len(jobs_info) == 3:
                item['experience'] = job_item.xpath('.//div[@class="job-labels-box"]/span[2]/text()').get()
                item['education'] = job_item.xpath('.//div[@class="job-labels-box"]/span[3]/text()').get()
            elif len(jobs_info) == 2:
                item['experience'] = job_item.xpath('.//div[@class="job-labels-box"]/span[1]/text()').get()
                item['education'] = job_item.xpath('.//div[@class="job-labels-box"]/span[2]/text()').get()
            elif len(jobs_info) == 1:
                this_text = job_item.xpath('.//div[@class="job-labels-box"]/span[1]/text()').get()
                if re.search("(学历|年|经验)",this_text) is not None:
                    item['experience'] = this_text
                else:
                    item['education'] = this_text
            item['company_name'] = job_item.xpath('.//span[@class="company-name ellipsis-1"]/text()').get()

            all_text = job_item.xpath('.//div[@class="company-tags-box ellipsis-1"]//span/text()').getall()
            this_industry = ""
            this_size = ""
            if len(all_text) == 3:
                this_industry = all_text[0]
                this_size = all_text[2]
            elif len(all_text) == 2:
                this_industry = all_text[0]
                if "人" in all_text[1]:
                    this_size = all_text[1]
            elif len(all_text) == 1:
                if "人" in all_text[0]:
                    this_size = all_text[0]
                else:
                    this_industry = all_text[0]
            item['company_industry'] = this_industry
            item['company_size'] = this_size

            item['id'] = base64.b32encode((item['job_name']+item['company_name']+item['post_time']).encode("utf-8")).decode("utf-8")

            yield Request(
                url=item['link'],
                headers=self.headers,
                callback=self._parse_other,
                dont_filter=True,
                priority=4,
                meta={"item": LiepinItem(item)}
            )
        # 如果下一页存在，就继续爬取下一页
        next_page_flag = response.xpath('//li[@title="下一页"]/@class').get()  # 获得下一页的a标签
        if next_page_flag is not None and "ant-pagination-disabled" not in next_page_flag:
            current_page = response.xpath('//li[@title="下一页"]/a/@data-currentpage').get()
            next_page = int(current_page) + 1
            yield Request(
                url=self.replace_url(replace_current_page_pattern,response.url,next_page),
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

        item['job_content'] = response.xpath('string(//section[@class="job-intro-container"])').get()
        item['job_content'] = self.replace_all_n(item['job_content'])
        item['company_address'] = response.xpath('//div[@class="company-info-container"]//span[text()="职位地址："]/../span[2]/text()').get()
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
