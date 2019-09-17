import random

import requests
from scrapy import signals
from scrapy.http import Response
from twisted.internet.error import TCPTimedOutError, ConnectionRefusedError, TimeoutError, ConnectionLost
from twisted.web.client import ResponseNeverReceived
from collections import Counter

import LiePin.data5u as data
from proxy_pool.ip_pool import ReachMaxException
from .settings import apiUrl, ip_pool


class MyproxiesSpiderMiddleware(object):

    def __init__(self, ):
        self.reset_set = False
        self.bad_ip_set = set()
        self.bad_code_count = 0
        self.timeOutCount = 0
        self.time_out_ip = []

    def process_request(self, request, spider):
        request.meta["proxy"] = "http://" + ip_pool.get_ip()

    def process_response(self, request, response: Response, spider):
        this_res_proxy = request.meta['proxy'].replace("http://", "")
        # 用来输出状态码
        if response.status != 200:
            spider.logger.info(f'{response.status},{response.url}')
        # 如果ip已被封禁，就采取措施
        if response.status == 403:
            ip_pool.report_baned_ip(this_res_proxy)
            thisip = ip_pool.get_ip()
            request.meta['proxy'] = "http://" + thisip
            return request

        if response.status == 408 or response.status == 502 or response.status == 503:
            ip_pool.report_bad_net_ip(this_res_proxy)
            request.meta['proxy'] = "http://" + ip_pool.get_ip()
            return request
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, ReachMaxException):
            spider.crawler.engine.close_spider(spider, f"reach day max number!!")
            return
        if isinstance(exception,
                      (ConnectionRefusedError, TCPTimedOutError, TimeoutError, ConnectionLost, ResponseNeverReceived)):
            this_bad_ip = request.meta['proxy'].replace("http://", "")
            ip_pool.report_bad_net_ip(this_bad_ip)
        spider.logger.debug(f"{type(exception)} {exception},{request.url}")
        thisip = ip_pool.get_ip()
        request.meta['proxy'] = "http://" + thisip
        return request
