import requests
from scrapy import Selector
from multiprocessing import Process, Queue
import threading
import random
import json
import time


def verify_one_proxy(old_queue, new_queue):
    while 1:
        proxy = old_queue.get()
        if proxy == 0: break
        try:
            if requests.get('http://www.baidu.com', proxies={proxy.split("://")[0]: proxy.split("://")[1]},
                            timeout=3).status_code == 200:
                print('success %s' % proxy)
                new_queue.put(proxy)
        except Exception as e:
            print('fail %s' % proxy)


class ProxyClass(object):
    """
    使用之前需要验证几次，多验证几次可以增加成功的数量，使用的时候只需要load就可以得到代理的列表
    """

    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)   Chrome/45.0.2454.101 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.open_base_url = "https://www.kuaidaili.com/free/intr/{page}/"
        self.Elite_base_url = "https://www.kuaidaili.com/free/inha/{page}/"
        self.page_range = list(range(1, 2))
        self.proxies = list()
        self.open_proxies()
        self.Elite_proxies()
        self.verify_pro = set()

    def open_proxies(self):
        """
        当使用这个属性的时候才会执行这个函数,用来抓取每天的免费代理
        :return:
        """
        for page in self.page_range:
            res = requests.get(self.open_base_url.format(page=str(page)), headers=self.headers)
            select = Selector(res)
            all_ip: list = select.xpath("//div[@id='list']//tr")[1:]  # 排除掉第一个，第一个是表的标题栏
            all_ip_port: list = [":".join(node.xpath("./td[position()<3]/text()").extract()) for node in
                                 all_ip]  # list of host:port
            protocal_host_port = ["://".join([protocal, host_ip]) for protocal, host_ip in
                                  zip(
                                      [node.xpath("./td[4]/text()").extract()[0].lower() for node in all_ip],
                                      all_ip_port
                                  )]
            self.proxies.extend(protocal_host_port)
            time.sleep(1)

    def Elite_proxies(self):
        for page in self.page_range:
            res = requests.get(self.Elite_base_url.format(page=str(page)), headers=self.headers)
            select = Selector(res)
            all_ip: list = select.xpath("//div[@id='list']//tr")[1:]  # 排除掉第一个，第一个是表的标题栏
            all_ip_port = [":".join(node.xpath("./td[position()<3]/text()").extract())
                           for node in all_ip]  # list of host:port
            protocal_host_port = [
                "://".join([protocal, host_ip]) for protocal, host_ip in
                zip(
                    [node.xpath("./td[4]/text()").extract()[0].lower() for node in all_ip],
                    all_ip_port
                )
            ]
            self.proxies.extend(protocal_host_port)
            time.sleep(1)

    def verify_proxies(self):
        old_queue = Queue()
        new_queue = Queue()
        print("verify ..")
        works = []
        for _ in range(120):
            works.append(threading.Thread(target=verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for o_prox in self.proxies:
            time.sleep(1)
            old_queue.put(o_prox)
        for _ in works:
            old_queue.put(0)
        for work in works:
            work.join()
        while 1:
            try:
                self.verify_pro.add(new_queue.get(timeout=1))
            except:
                break
        print('verify_proxies done!')

    def save2file(self):
        print("saving proxies ....")
        with open("proxy.log", "w") as f:
            s = "\t".join(self.verify_pro)
            f.writelines(s)

    def load_proxy(self):
        print("loading proxies ....")
        res_list = None
        with open("proxy.log", "r") as f:
            line = f.readline()
            res_list = line.split("\t")
        return res_list


def update_proxy():
    a = ProxyClass()
    a.verify_proxies()
    a.verify_proxies()
    a.save2file()