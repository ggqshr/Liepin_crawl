# -*- coding: utf-8 -*-

# Scrapy settings for LiePin project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.log import INFO

BOT_NAME = 'LiePin'

SPIDER_MODULES = ['LiePin.spiders']
NEWSPIDER_MODULE = 'LiePin.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

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
    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
    "LiePin.MyproxiesSpiderMiddleware.MyproxiesSpiderMiddleware": 125
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'LiePin.pipelines.LiepinPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
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

REDIS_HOST = "116.56.140.202"
REDIS_PORT = 6379

MONGODB_HOST = "116.56.140.202"
MONGODB_PORT = 27017

MODE = "LOCAL"  # or YAO

IP_POOL = [
    {"ipaddr": "14.20.235.211:808"},
    {"ipaddr": "115.171.202.66:9000"},
    {"ipaddr": "119.57.108.109:53281"},
    {"ipaddr": "123.139.56.238:9999"},
    {"ipaddr": "218.66.253.146:8800"},
    {"ipaddr": "222.74.61.98:53281"},
    {"ipaddr": "119.57.108.109:53281"}
]
