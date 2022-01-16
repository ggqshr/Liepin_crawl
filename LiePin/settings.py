# -*- coding: utf-8 -*-

# Scrapy settings for LiePin project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from logging.config import dictConfig, fileConfig

import yaml
from proxy_pool_redis import XunProxyPool,KuaiProxyPool
from logging import INFO, DEBUG
import pickle
from scrapy.utils.log import configure_logging
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import os
from pathlib import Path

BOT_NAME = 'LiePin'

SPIDER_MODULES = ['LiePin.spiders']
NEWSPIDER_MODULE = 'LiePin.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'LiePin.middlewares.LiepinSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'LiePin.middlewares.LiepinDownloaderMiddleware': 543,
    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 125,
    "LiePin.MyproxiesSpiderMiddleware.MyproxiesSpiderMiddleware": 125
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'LiePin.entension.send_mail.SendMail': 500,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'LiePin.pipelines.LiepinPipeline': 300,
    # 'scrapy_redis.pipelines.RedisPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 2
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

COOKIES_STR = 'ADHOC_MEMBERSHIP_CLIENT_ID1.0=74123651-55ca-1f13-cbed-235d2ad5b8e0; __uuid=1556938836439.76; abtest=0; _fecdn_=1; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1556938838,1557119211,1557140738,1557141780; fe_all_localcookie_sessionid=22547-39953-1557141811159; __tlog=1557141779811.55%7C00000000%7CR000000075%7Cs_o_001%7Cs_o_001; char_captcha=8CFADB68C0A844057FD1A4C8D35C27B6; _mscid=00000000; _uuid=8FA573ABFFA8441814388EB4F51F6DF6; JSESSIONID=49C2508F699F44C795B4EA5D9BD96E6B; __session_seq=22; __uv_seq=6; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1557188220'
LOG_LEVEL = INFO

MONGODB_HOST = "gateway"
MONGODB_PORT = 10021

MODE = "YAO"  # or YAO

IP_POOL = None  # ProxyClass().load_proxy()

USER_AGENT_POOL = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
]

# # 换用scrapy-redis的去重器
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# # 换用scrapy-redis的调度器
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"

REDIS_HOST = "redis"
REDIS_PORT = 6379

SCHEDULER_PERSIST = False

if not os.path.exists("./logs"):
    os.mkdir('./logs')

configure_logging(install_root_handler=False)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        TimedRotatingFileHandler(filename='logs/LiePin.log', encoding='utf-8', when="D", interval=1,backupCount=3)],
    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)

apiUrl = "http://dps.kdlapi.com/api/getdps/?orderid=914233167437767&num=3&pt=1&dedup=1&format=json&sep=1"
ip_pool = KuaiProxyPool(api_url=apiUrl,name='liepin',redis_host=REDIS_HOST,redis_port=REDIS_PORT,redis_password="b7310",scan_timeout_ip=True,log_level=logging.DEBUG,scan_time_span=100)
RETRY_ENABLED = False

# 和邮件相关
MYEXT_ENABLED = True
MAIL_HOST = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USER = '942490944@qq.com'
MAIL_PASS = 'ijmbixectujobeei'

with open(Path(__file__).parent.parent.joinpath("lpcity_data.data"), 'rb') as f:
    city_code_list = pickle.load(f)

CLOSESPIDER_TIMEOUT = 169200

DOWNLOAD_TIMEOUT = 30

REDIRECT_ENABLED = False

MONGODB_USER = "jason#619"
MONGODB_PASSWORD = "jason#619"

DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"
