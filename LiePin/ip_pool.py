import requests
import json
import logging
import time
import random

REQUEST_SUCCESS = 0
REQUEST_TOO_QUICK = 1
REQUEST_REACH_MAX = 2


class IpPool(object):
    def __init__(self, api_url, ):
        self.api_url = api_url
        self.ip_pool = set()
        self.bad_net_ip_count = dict()
        logging.basicConfig()

    def _request_ip(self):
        res = requests.get(self.api_url).content.decode()  # 请求ip
        res = json.loads(res)  # 解析成字典
        if res['ERRORCODE'] == "0":
            logging.info("请求新的代理IP")
            ip_port_list = res['RESULT']
            self.ip_pool = set([f"{ll['ip']}:{ll['port']}" for ll in ip_port_list])
            return REQUEST_SUCCESS
        elif res['ERRORCODE'] in ["10036", "10038", "10055"]:
            logging.info("提取频率过高")
            return REQUEST_TOO_QUICK
        elif res["ERRORCODE"] is "10032":
            logging.info("已达上限!!")
            return REQUEST_REACH_MAX

    def _get_ip(self):
        if len(self.ip_pool) != 0:
            return random.choice(self.ip_pool)
        else:
            logging.warning("当前IP池为空！！")
