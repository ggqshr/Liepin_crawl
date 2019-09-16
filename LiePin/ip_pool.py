import requests
import json
import logging
import time
import random
import threading

REQUEST_SUCCESS = 0
REQUEST_TOO_QUICK = 1
REQUEST_REACH_MAX = 2


class IpPool(object):
    def __init__(self, api_url, ):
        self.api_url = api_url
        self.ip_pool = set()
        self.bad_net_ip_count = dict()
        logging.basicConfig()
        self.cond = threading.Condition()
        self.lock = threading.Lock()

    def _request_ip(self):
        res = requests.get(self.api_url).content.decode()  # 请求ip
        res = json.loads(res)  # 解析成字典
        if res['ERRORCODE'] == "0":
            with self.cond:
                logging.info("请求新的代理IP")
                ip_port_list = res['RESULT']
                self.ip_pool = set([f"{ll['ip']}:{ll['port']}" for ll in ip_port_list])
                self.cond.notify_all()
                return REQUEST_SUCCESS
        elif res['ERRORCODE'] in ["10036", "10038", "10055"]:
            logging.info("提取频率过高")
            return REQUEST_TOO_QUICK
        elif res["ERRORCODE"] is "10032":
            logging.info("已达上限!!")
            return REQUEST_REACH_MAX

    def _has_ip(self):
        return len(self.ip_pool) != 0

    def get_ip(self):
        """
        从池中拿去一个IP,如果当前没有IP就wait，直到新的IP已经产生
        :return:
        """
        with self.cond:
            self.cond.wait_for(self._has_ip)
            return random.choice(self.ip_pool)

    def report_baned_ip(self, ip):
        self.ip_pool.discard(ip)
        if len(self.ip_pool) == 0 and self.lock.acquire(blocking=False):
            self.lock.release()