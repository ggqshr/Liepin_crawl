from scrapy import cmdline
from LiePin import ProxyClass

a = ProxyClass()
a.verify_proxies()
a.verify_proxies()
a.save2file()
cmdline.execute(['scrapy', 'crawl', 'lp'])
