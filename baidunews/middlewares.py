from scrapy import signals
from fake_useragent import UserAgent
import random

class UADownloaderMiddleware(object):
    def __init__(self, crawler):
        super(UADownloaderMiddleware,self).__init__()
        self.ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        return s
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random

        return None
