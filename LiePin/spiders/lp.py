# -*- coding: utf-8 -*-
import random

import scrapy
from scrapy import Request, Selector
from LiePin.settings import COOKIES_STR
import base64
from LiePin import LiepinItem
from functools import partial
import requests
import re
from LiePin.settings import USER_AGENT_POOL
from LiePin.data5u import IPPOOL


def extrat(response, xpath):
    return response.xpath(xpath).extract()


class LpSpider(scrapy.Spider):
    name = 'lp'
    allowed_domains = ['liepin.com']
    headers = {
        "Host": "www.liepin.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "User-Agent": random.choice(USER_AGENT_POOL),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Referer": 'https://www.liepin.com/zhaopin/?init=-1&headckid=ebb4af279a07d4be&fromSearchBtn=2&sfrom=click-pc_homepage-centre_searchbox-search_new&ckid=ebb4af279a07d4be&degradeFlag=0&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=7cd3a89b67e7261f0646fe4114c38c34&d_curPage=0&d_pageSize=40&d_headId=7cd3a89b67e7261f0646fe4114c38c34&curPage=1',
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    cookies_str = COOKIES_STR
    regSpace = re.compile(r'([\s\r\n\t])+')

    def start_requests(self):
        base_url = [
            'https://www.liepin.com/zhaopin/?init=-1&headckid=10309442b4fc4250&fromSearchBtn=2&pubTime=1&dqs=&ckid=48be21f35417fec6&degradeFlag=0&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EV6MwPcZ2ne9zYObRj7X8Rg&d_sfrom=search_fp_nvbar&d_ckId=5bbcb19abb610f06d82310563dd69691&d_curPage=1000&d_pageSize=40&d_headId=7cd3a89b67e7261f0646fe4114c38c34&curPage={curr_page}',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&ckid=70442a9a34fb5da7&subIndustry=&industryType=industry_01&industries=040&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~JJrjc9QTKuvQj0H6ILUEAw&d_sfrom=search_fp&d_ckId=e1117d6da60c34dc12b33d548dfe2bf0&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&ckid=f7ba3efd536b30a9&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_01&industries=420&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~1p1Hf6Iytm4nd3ac31P45g&d_sfrom=search_fp&d_ckId=03b97691bfab774ad24300bfe746300a&d_curPage=1&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&ckid=9fa025d3bd362e5c&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_01&industries=010&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~g7FNUaAoUFq1nVroUHCUFA&d_sfrom=search_fp&d_ckId=4e7478e1734d08d4db372895c2c6205d&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&ckid=148ed37b18edd8b9&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_01&industries=030&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~Uu4d3oMo-zE-ddoy0_BJog&d_sfrom=search_fp&d_ckId=5dad380afcb3b576a0163444e915f495&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&ckid=fc4d3c1e6a680bb9&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_02&industries=050&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=665000becb0679e42d5f1d8f68da48c2&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=afde076ddda7734f&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_02&industries=060&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~zvU2C1lgLGbpL8vtBhrYig&d_sfrom=search_fp&d_ckId=e78bd0eb288f0b40b6bf57303afffa01&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=727416ce5c22215e&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_02&industries=020&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~Ka9crqvuxzVr3ADmhsqUmg&d_sfrom=search_fp&d_ckId=b02413be266582a95c35a8e6e2553bef&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=216875804a0a0dec&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_03&industries=080&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=3505a7b596af9dad6deee203c645df4e&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=23a98cbc05615759&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_03&industries=100&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~2hQDspysfS9PNVzRr9BB3g&d_sfrom=search_fp&d_ckId=defa50161d9d5438e0b8aaa710132698&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=02d2f93a30447da0&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_03&industries=090&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~wyzB-35qIDxDek8aW8IKmg&d_sfrom=search_fp&d_ckId=680c5e0fc0db35c5d3cd56a85e5003a5&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=14bbff74f6325ff8&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_04&industries=130&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=24027e58090cbe00b6b1e9271d25e66c&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=f495a16d51836e9f&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_04&industries=140&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~cCtSQGb_L0fBsFByoQBjJg&d_sfrom=search_fp&d_ckId=564d73efec3b269e1a87d4d42d9fbafa&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=309b768ee54afc98&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_04&industries=150&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~bf0LjWfMU8ILfz37schPHQ&d_sfrom=search_fp&d_ckId=ff1ce5b6535b69627ec6cce8f1a023d8&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=051e38f181416cd1&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_04&industries=430&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~Al0RgotvGQ-kRA59YliAuQ&d_sfrom=search_fp&d_ckId=595386aba0b7b2fcbffb1414842c4289&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=9608b9a7febd628c&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_04&industries=500&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~dT5I7aUUbZl4N07c49jaQg&d_sfrom=search_fp&d_ckId=3a93df66ba5333bc1ab9e8af61bc6e99&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=f1837ed55424c4a4&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=190&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=e7cf651750f37744a595d321931ac0ab&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=60dea4ff776902c1&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=240&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~y1AwrmoR7ov7wg0Mmb11eg&d_sfrom=search_fp&d_ckId=4945a67a2e2f57a3c4a9c5b8ae27362b&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=ae84ee6ec9a8d62a&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=200&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~bBoXrsQK-aQsjy_hof7xvQ&d_sfrom=search_fp&d_ckId=c5f49984af5b6a06c74989be369e9cfa&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=7ee677d8ad38f4ce&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=210&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~MM8xwTkd6S3ugIAXpx6yyA&d_sfrom=search_fp&d_ckId=3ad8942160a8ba6a3a34425a2426a1bd&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=b87885be05a77374&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=220&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~ahkg8I3yT7p_05KmFrrkSw&d_sfrom=search_fp&d_ckId=3700c28dd39fbb7ac8f7da241c6494fb&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=a3cb03ed179e9eb2&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=460&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~9jRPMRYY7Z-SX2jl0XTW-A&d_sfrom=search_fp&d_ckId=7d2a2fe552802f0b8218cdd74fe29a2a&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=ad15cb8db007962c&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_05&industries=470&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~s-bGK8mKRqxi_zr3rg5qFg&d_sfrom=search_fp&d_ckId=88ef76b9b077d7f705261bbafaa847bf&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=18682ae9d0ae4837&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_06&industries=350&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=5c1b8e12267c46b64575e9df0a5fd8c7&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=ac010b373e04bc34&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_06&industries=360&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~YO21lsV0H0wUK91fAm7NzA&d_sfrom=search_fp&d_ckId=7a48164fc3455e86dc923adccdbf2b85&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=631d97db0ddb99aa&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_06&industries=180&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~RakY85OjQbeuxDaZd_PreQ&d_sfrom=search_fp&d_ckId=a6d7b611e384d0dcfd919d6195517e91&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=e510e697fc4485b0&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_06&industries=370&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~wwZSTNrJN6-1-gi9q9eRCg&d_sfrom=search_fp&d_ckId=1dbba7b65d6cba101e838cd6a3fbd55c&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=9f5308266b4bfb56&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_06&industries=340&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~QYQ5I704jRxpVSn3D8BP_g&d_sfrom=search_fp&d_ckId=7c6be2e5f4044d8c8bea486b8799bad4&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=239390e6899eba86&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_10&industries=270&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=90fa81049875bfc9804d9de3691de252&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=b8cd6ba3bfa404d1&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_10&industries=280&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~GmwGHdR2O_yp6JCUevAbVQ&d_sfrom=search_fp&d_ckId=6f4a856e67e6504984b13ca91750d563&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=3317a0f0f47411db&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_10&industries=290&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~LkVbK6FcXY1sJXvihtkUSA&d_sfrom=search_fp&d_ckId=a6922fc98ae87604c4ce7c053647e8bc&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=0de55c24070bb80c&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_11&industries=330&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=ccf085204287f17b57db81241536e881&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=e88ec8ba82a48bce&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_11&industries=310&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~gb6pCPG4uYV84MT07dpdeQ&d_sfrom=search_fp&d_ckId=62df11fa3ff5d2f7c3f21aa01d7ff389&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=fc21823feb802e8f&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_11&industries=320&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~-JHUxRED-PDFAMlKKstnkg&d_sfrom=search_fp&d_ckId=61641c6a6fd20fda65cc77154656775f&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=fe51f6b246414728&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_11&industries=300&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~ly8ToWQ5ocVScrEmT209LQ&d_sfrom=search_fp&d_ckId=fa2cab4952e5b86f6e2ddf8f3b479571&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=2ba52341eb4a9422&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_11&industries=490&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~iFMUI06xzUk_KSHxFS-srQ&d_sfrom=search_fp&d_ckId=4ba2c9fc83499f54e6be0730d5dbf7fd&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=9b10f9479dfdbe39&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=120&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=ad6cf0f7a5449d1eba21f762c7ff9e62&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=212033c1a7304e03&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=110&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~2Hh7lWkG4Cpzz2QIvzOkLQ&d_sfrom=search_fp&d_ckId=d340df65c7f20636ba5d66a4901066db&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=7746c4fbdf352c28&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=440&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~HCv6d9WDCZeI8zKqpLgLQA&d_sfrom=search_fp&d_ckId=20742802187d6b3029731d84f47aaad3&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=79797d563a3c8838&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=450&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~JJh_8aYgr8ZlT4UmvYduew&d_sfrom=search_fp&d_ckId=0fbc4ffc34cda7969ce855f5285c6ffa&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=2987a902fcdefd73&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=230&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~wqBTNweJ1yQMamjgmdK3ww&d_sfrom=search_fp&d_ckId=e6a398d43d854b752637d92a46970578&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=b60ab293994e5d1e&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=260&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~KBrv6TjSGdHZhrowEbg70A&d_sfrom=search_fp&d_ckId=83f6a7e3ab829cfd2123679a7e9048b0&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=813a0030dac1f96d&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_07&industries=510&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~JdU9BlPJ1R0duINTYYgi_w&d_sfrom=search_fp&d_ckId=21977df3438e399d8e4d20bf97923b15&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=942c788e5ac062c5&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_08&industries=070&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=ba1ab5d5cf7d44a868b4f2e9e4f89124&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=e11613e294d909f8&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_08&industries=170&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~JXvpnxg7eZ6GFs7p-osX2Q&d_sfrom=search_fp&d_ckId=f3fb55489c97f99e2dca19171e9cd51b&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=9a90e8fbdb1cfd93&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_08&industries=380&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~0as6CwNJPqZPkJ5sZ9vjrA&d_sfrom=search_fp&d_ckId=af7d0afb8b49c121da1da41bf2793458&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=5dca20fa8b87de6b&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_09&industries=250&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=b6c44f9d3367dffdd2a3492c4354cbbe&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=fd27690e53dbfc15&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_09&industries=160&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~M3t9P9tjvizO-Enfpl5DXg&d_sfrom=search_fp&d_ckId=da6d3e8aac092c0ba0427024f7284ba3&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=96ea93de0144a9b0&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_09&industries=480&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~aFqvwV-hkfEgE6dzsrcN6g&d_sfrom=search_fp&d_ckId=7b3d996f019fbd01006ddc91fd56c3a8&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=0cbf35e16878cb04&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_12&industries=390&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_fp&d_ckId=7461319ba6fa03100a977533628c700c&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=cd630fee37b5fa17&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_12&industries=410&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~S3BhLEBCVHn14N5rs6Btkw&d_sfrom=search_fp&d_ckId=3067091fc5a60be9c0a8dbf725c85627&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1',
            'https://www.liepin.com/zhaopin/?init=-1&headckid=4455a4b08412aed8&flushckid=1&fromSearchBtn=2&dqs=&ckid=b702f14b50c87838&degradeFlag=0&subIndustry=&curPage=1&industryType=industry_12&industries=400&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&siTag=1B2M2Y8AsgTpgAmY7PhCfg~Ah8KnpyRVP7cwAAdP6OyEw&d_sfrom=search_fp&d_ckId=f0cf37fe4c928b425e6fc9abc43da59f&d_curPage=0&d_pageSize=40&d_headId=c51883a4d74dd1e26f2043eeacb316fd&curPage={curr_page}&pubTime=1']
        for p in base_url:
            for page in range(0, 200):
                yield Request(
                    url=p.format(curr_page=page),
                    headers=self.headers,
                    cookies=self.cookies_dict,
                    callback=self.parse,
                    # meta={"proxy": "http://" + random.choice(IPPOOL)}
                )

    def parse(self, response):

        _extrat = partial(extrat, response)
        item = LiepinItem()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item['link'] = _extrat('//div[@class="job-info"]/h3/a/@href')
        item['post_time'] = _extrat('//time/@title')
        item['job_name'] = [self.replace_all_n(tt) for tt in _extrat('//div[@class="job-info"]/h3/a/text()')]
        salary_place_education_experience_list = list(
            map(lambda x: x.split("_"), _extrat('//p[@class="condition clearfix"]/@title')))
        item['salary'] = [i[0] for i in salary_place_education_experience_list]
        item['place'] = [i[1] for i in salary_place_education_experience_list]
        item['education'] = [i[2] for i in salary_place_education_experience_list]
        item['experience'] = [i[3] for i in salary_place_education_experience_list]
        item['company_name'] = _extrat('//p[@class="company-name"]/a/text()')
        item['advantage'] = response.xpath('//p[@class="temptation clearfix"]')
        item['advantage'] = ["_".join(node.xpath(".//span/text()").extract()) for node in item['advantage']]
        if item['advantage'] != 40:
            item['advantage'].append(["领导好"])
        item['id'] = [base64.b32encode((n + c).encode("utf-8")).decode("utf-8") for n, c in
                      zip(item['job_name'], item['company_name'])]
        try:
            all_data = [{key: item[key][index] for key in item.keys()} for index in range(len(item['id']))]
        except IndexError as e:
            all_data = [{key: item[key][index] for key in item.keys()} for index in
                        range(min([len(v) for v in item.values()]))]

        for link in all_data:
            parse_other = partial(self._parse_other, LiepinItem(link))
            if re.findall(r"^/", link['link']) != []:
                link['link'] = "https://www.liepin.com" + link['link']
            yield Request(
                url=link['link'],
                headers=self.headers,
                callback=parse_other,
                dont_filter=True,
            )

    def _parse_other(self, item, response):
        item['job_content'] = response.xpath('//div[@class="content content-word"]')[0].xpath("./text()").extract()
        item['job_content'] = self.replace_all_n(item['job_content'])
        item['company_address'] = response.xpath('//ul[@class="new-compintro"]/li[3]/text()').extract()
        item['company_size'] = response.xpath('//ul[@class="new-compintro"]/li[2]/text()').extract()
        item['company_industry'] = response.xpath('//ul[@class="new-compintro"]/li[1]/a/text()').extract()
        yield item

    @property
    def cookies_dict(self):
        str_list = self.cookies_str.split(";")
        result = {}
        for s in str_list:
            split_result = s.split("=", 1)
            result[split_result[0].strip()] = split_result[1].strip()
        return result

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            if type(text) == str:
                rel = re.sub(self.regSpace, "", text)
                return rel
            elif type(text) == list:
                return "".join([re.sub(self.regSpace, "", t) for t in text])
        except TypeError as e:
            return "空"
