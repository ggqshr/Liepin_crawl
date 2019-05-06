# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from .settings import REDIS_PORT, REDIS_HOST, MODE, MONGODB_HOST, MONGODB_PORT
import redis as r
LOCAL = "127.0.0.1"


class LiepinPipeline(object):
    def __init__(self):
        self.client = r.Redis(REDIS_HOST if MODE == 'LOCAL' else LOCAL, port=REDIS_PORT)
        self.conn = MongoClient(MONGODB_HOST if MODE == 'LOCAL' else LOCAL, MONGODB_PORT)
        if MODE == 'LOCAL':
            self.conn.admin.authenticate("ggqshr", "root")
        self.mongo = self.conn.LiePin.LiePin

    def process_item(self, item, spider):
        all_data = [{key: item[key][index] for key in item.keys()} for index in range(len(item['id']))]
        for data in all_data:
            if self.client.sadd("lie_pin_id_set", data['id']) == 0:
                return item
            self.mongo.insert_one(data)
        return item
