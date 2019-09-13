import requests
from scrapy import cmdline
from LiePin import UpdateProxy
from LiePin import genrate_proxy
from LiePin import data5u
import time
from LiePin.settings import apiUrl
import LiePin.data5u as data

# 获取IP的API接口
apiUrl = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=2eeedc14918546f087abcddafd5ee37d&orderno=YZ20195179329mb51zm&returnType=1&count=5"
# 获取IP时间间隔，建议为5秒
# fetchSecond = 300
# # 开始自动获取IP
# genrate_proxy.GetIpThread(apiUrl, fetchSecond).start()
# time.sleep(3)
res = requests.get(apiUrl).content.decode()
# 按照\n分割获取到的IP
data.IPPOOL = res.strip().split('\r\n')
time.sleep(3)
cmdline.execute(['scrapy', 'crawl', 'lp'])
