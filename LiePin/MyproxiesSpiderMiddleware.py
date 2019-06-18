import random

import requests
from scrapy import signals
from scrapy.http import Response

import LiePin.data5u as data
from .settings import apiUrl, lock

class MyproxiesSpiderMiddleware(object):

    def __init__(self, ip=''):
        self.ip = ip
        self.reset_set = False
        self.bad_ip_set = set()
        self.bad_code_count = 0

    def process_request(self, request, spider):
        thisip = random.choice(data.IPPOOL)
        request.meta["proxy"] = "http://" + thisip


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
            spider.logger.info(response.status)
        # 如果ip已被封禁，就采取措施
        if response.status == 403:
            # 如果已经重置过ip，在重置ip之前的所有的403请求都会让计数减少
            if self.reset_set:
                self.bad_code_count -= 1
            # 如果ip被封禁，就加入到set中
            self.bad_ip_set.add(request.meta['proxy'])

            # 如果当前set的长度达到和ip池大小相等，且没有加过锁，就重置ip池
            if (len(self.bad_ip_set) == 3 or len(self.bad_ip_set) >= 3) and lock.acquire(blocking=False):
                self.reset_set = True  # 改标记表明已经重置了ip

                # 重置Ip池
                res = requests.get(apiUrl).content.decode()
                # 按照\n分割获取到的IP
                data.IPPOOL = res.strip().split('\r\n')

                # 将被封禁的ipset清空，回复初始状态
                self.bad_ip_set.clear()
                spider.logger.info("reset ip pool!")

            # 如果还有ip可用，将当前的请求换一个代理，重新调度
            thisip = random.choice(data.IPPOOL)
            request.meta['proxy'] = "http://" + thisip
            return request
        # 这个状态表明在重置了ip池之后，请求成功的次数，只有达到一定次数，才将锁释放
        if response.status == 200 and self.reset_set:
            # 计数加一
            self.bad_code_count += 1
            if self.bad_code_count == 32:  # 此处的数应该和设置的最大线程数相等，（估计）
                # 回复初试状态
                lock.release()
                self.bad_code_count = 0
                self.reset_set = False

        if response.status == 408:
            self.bad_ip_set.add(request.meta['proxy'])
            thisip = random.choice(data.IPPOOL)
            request.meta['proxy'] = "http://" + thisip
            return request
        return response