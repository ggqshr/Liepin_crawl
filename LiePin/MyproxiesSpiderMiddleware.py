import random
from scrapy import signals
import LiePin.data5u as data


class MyproxiesSpiderMiddleware(object):

    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(data.IPPOOL)
        request.meta["proxy"] = "http://" + thisip
