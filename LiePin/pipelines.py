# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

from pymongo import MongoClient
from .settings import REDIS_PORT, REDIS_HOST, MODE, MONGODB_HOST, MONGODB_PORT, MONGODB_PASSWORD, MONGODB_USER
from redisbloom.client import Client

LOCAL = "127.0.0.1"


class LiepinPipeline(object):
    def __init__(self):
        self.client = Client(host=REDIS_HOST,port=REDIS_PORT,password="b7310")
        if not self.client.exists("bf:liepin"):
            self.client.bfCreate("bf:liepin",0.00001,100000)
        self.conn = MongoClient(MONGODB_HOST if MODE != 'LOCAL' else LOCAL, MONGODB_PORT)
        self.conn.admin.authenticate(MONGODB_USER, MONGODB_PASSWORD)
        # if MODE == 'LOCAL':
        #     self.conn.admin.authenticate("ggqshr", "root")
        self.mongo = self.conn.LiePin.LiePin
        self.count = 0

    def process_item(self, item, spider):
        # if self.client.sadd("lie_pin_id_set", item['id']) == 0:
        #     return item
        self.mongo.insert_one(dict(item))
        self.count += 1
        return item

    def close_spider(self, spider):
        with open("result.log", "a") as f:
            f.writelines("{} crawl item {} \n".format(datetime.now().strftime("%Y.%m.%d"), self.count))
            f.flush()
