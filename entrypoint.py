from scrapy import cmdline
from LiePin import UpdateProxy
from LiePin import genrate_proxy
from LiePin import data5u
import time

# 获取IP的API接口
apiUrl = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=d460f14ed5ae426e8a7164005c61b9e7&orderno=YZ20195179329mb51zm&returnType=1&count=5"
# 获取IP时间间隔，建议为5秒
fetchSecond = 300
# 开始自动获取IP
genrate_proxy.GetIpThread(apiUrl, fetchSecond).start()
time.sleep(3)
cmdline.execute(['scrapy', 'crawl', 'lp'])
