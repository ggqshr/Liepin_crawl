import random
from scrapy import signals
from .data5u import IPPOOL


class MyproxiesSpiderMiddleware(object):

    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(IPPOOL)
        print("当前使用IP是：" + thisip)
        request.meta["proxy"] = "http://" + thisip
