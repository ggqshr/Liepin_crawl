import random
from scrapy import signals
from .settings import IP_POOL




class MyproxiesSpiderMiddleware(object):

    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(IP_POOL)
        print("this is ip:" + thisip.split("://")[1])
        request.meta["proxy"] = thisip
