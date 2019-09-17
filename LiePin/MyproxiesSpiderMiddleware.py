import random

import requests
from scrapy import signals
from scrapy.http import Response
from twisted.internet.error import TCPTimedOutError, ConnectionRefusedError, TimeoutError, ConnectionLost
from twisted.web.client import ResponseNeverReceived
from collections import Counter

import LiePin.data5u as data
from LiePin.ip_pool import ReachMaxException
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
        """
        整体思想是使用锁来控制，但是不能在重置成功后立马释放锁，因为请求队列中还有请求在使用重置ip池之前的ip，
        这些请求在释放了锁之后，也可以进入到if里，从而会出现异常
        现在的办法是使用一个计数器和一个标志位，在重置之后设置一下标志位，现在估计是在将队列中使用之前代理的请求消耗完后
        再释放锁，每一个403请求会让计数减少，而重置完之后的每一次200的请求会让计数器增加，现在是让计数器等于最大线程数的时候释放锁，
        就解决了之前的问题 perfect!
        :param request:
        :param response:
        :param spider:
        :return:
        """
        # 用来输出状态码
        if response.status != 200:
            spider.logger.info(f'{response.status},{response.url}')
        # 如果ip已被封禁，就采取措施
        if response.status == 403:
            ip_pool.report_baned_ip(request.meta['proxy'])
            thisip = ip_pool.get_ip()
            request.meta['proxy'] = "http://" + thisip
            return request

        if response.status == 408 or response.status == 502 or response.status == 503:
            ip_pool.report_bad_net_ip(request.meta['proxy'])
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
