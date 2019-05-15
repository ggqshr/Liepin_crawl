from scrapy import cmdline
from LiePin import UpdateProxy
from LiePin import genrate_proxy
from LiePin import data5u
import time

# 获取IP的API接口
apiUrl = "http://api.ip.data5u.com/api/get.shtml?order=e0dc70ee5d127a3f6c7f1013c5b28dd2&num=100&carrier=0&protocol=0&an1=1&an2=2&an3=3&sp1=1&sp2=2&sort=1&system=1&distinct=0&rettype=1&seprator=%0A"
# 获取IP时间间隔，建议为5秒
fetchSecond = 5
# 开始自动获取IP
# genrate_proxy.GetIpThread(apiUrl, fetchSecond).start()
# time.sleep(3)
cmdline.execute(['scrapy', 'crawl', 'lp'])
