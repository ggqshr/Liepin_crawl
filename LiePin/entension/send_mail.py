import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.xlib.pydispatch import dispatcher
import scrapy.spiders
from scrapy.mail import MailSender

logger = logging.getLogger(__name__)


class SendMail(object):
    def __init__(self, sender):
        dispatcher.connect(self.close, signals.spider_closed)
        self.sender = sender

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        mail_host = crawler.settings.get('MAIL_HOST')  # 发送邮件的服务器
        mail_port = crawler.settings.get('MAIL_PORT')  # 邮件发送者
        mail_user = crawler.settings.get('MAIL_USER')  # 邮件发送者
        mail_pass = crawler.settings.get('MAIL_PASS')  # 发送邮箱的密码不是你注册时的密码，而是授权码！！！切记！

        sender = MailSender(mail_host, mail_user, mail_user, mail_pass, mail_port, False,
                            True)  # 由于这里邮件的发送者和邮件账户是同一个就都写了mail_user了
        h = cls(sender)
        return h

    def close(self, spider: scrapy.spiders, reason):
        body = f"{spider.name} 已经关闭，原因是{reason},以下是结束的信息\n{spider.crawler.stats._stats}"
        return self.sender.send(to="942490944@qq.com", subject=f"{spider.name} 爬虫关闭提醒", body=body)
