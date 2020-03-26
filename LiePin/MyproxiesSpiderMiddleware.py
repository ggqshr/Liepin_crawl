import random

import requests
from scrapy import signals
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import IgnoreRequest
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
        try:
            this_res_proxy = request.meta['proxy'].replace("http://", "")
            if response.status == 404:
                raise IgnoreRequest
            # 用来输出状态码
            if response.status != 200:
                spider.logger.debug(f'{response.status},{response.url}')
            if response.status in [302]:
                ip_pool.report_bad_net_ip(this_res_proxy)
                request.meta['proxy'] = "http://" + ip_pool.get_ip()
                return request
            if response.status in [403, 408, 502, 503]:
                ip_pool.report_baned_ip(this_res_proxy)
                request.meta['proxy'] = "http://" + ip_pool.get_ip()
                return request
            return response
        except ReachMaxException as e:
            spider.logger.info("reach max in lp")
            res = Response(url=request.url,request=request)
            res.meta['reach_max'] = True
            return res

    def process_exception(self, request, exception, spider):
        if isinstance(exception,
                      (ConnectionRefusedError, TCPTimedOutError, TimeoutError, ConnectionLost, ResponseNeverReceived,
                       TunnelError)):
            this_bad_ip = request.meta['proxy'].replace("http://", "")
            ip_pool.report_bad_net_ip(this_bad_ip)
        spider.logger.debug(f"{type(exception)} {exception},{request.url}")
        thisip = ip_pool.get_ip()
        request.meta['proxy'] = "http://" + thisip
        return request
