from scrapy import cmdline
from LiePin import UpdateProxy

UpdateProxy.update_proxy()
cmdline.execute(['scrapy', 'crawl', 'lp'])
