# -*- coding: utf-8 -*-
import scrapy
import xlrd
from lxml import etree
import urllib.parse
from baidunews.items import BaidunewsItem
import json
import re
from baidunews import config

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['news.baidu.com']
    start_urls = 'http://news.baidu.com/ns?word={keyword}&tn=news&from=news&cl=2&rn=20&ct=0&clk=sortbytime'

    def start_requests(self):
        wb=xlrd.open_workbook(config.FILENAME)
        sheet = wb.sheet_by_index(0)
        nrows = sheet.nrows
        for i in range(1,nrows+1):
            company = sheet.cell(i, 0).value
            keyword = '(' + company + ')工程质量问题'
            keyword=urllib.parse.quote(keyword)
            yield scrapy.Request(self.start_urls.format(keyword=keyword), callback=self.parse_page, meta={
                'company': company
            })

    def parse_page(self, response):
        Selector = etree.HTML(response.text)
        href = Selector.xpath('//h3[@class="c-title"]/a/@href')
        times = Selector.xpath('//p[@class="c-author"]/text()')
        times = [x.strip() for x in times if x.strip() != '']

        for i in range(0, len(times)):
            title = Selector.xpath('//div['+str(i+1)+']/h3[@class="c-title"]/a//text()')
            title = ''.join(title).strip()
            time = times[i].strip()
            time = time.split()[1]
            year = time.split('年')[0]
            if re.match('.*前',year):
                pass
            else:
                year = int(year)
                if (year < 2014):
                    break;
            
            
            yield scrapy.Request(href[i], callback=self.parse_detail, meta={
                'company': response.meta['company'],
                'pub_time': time,
                'title': title,
                'href':href[i]
            }, dont_filter=True)
            
        next_url = Selector.xpath('//*[@id="page"]/a/@href')
        if (len(next_url) == 0):
            pass
        else:
            next_url = next_url[-1]
            next_url = 'http://news.baidu.com' + next_url
            yield scrapy.Request(next_url, callback=self.parse_page, meta={
                'company': response.meta['company'],
            })
        

    def parse_detail(self, response):
        Selector = etree.HTML(response.text)
        item = BaidunewsItem()
        item['company'] = response.meta['company']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        content=self.parse_content(Selector,response)
        item['content'] = content
        item['href'] = response.meta['href']
        yield item


    def parse_content(self,Selector,response):
        content = Selector.xpath('//*[@id="endText"]/p/text()')
        if len(content) == 0:
            content = Selector.xpath('//div//section/text()')
        if len(content) == 0:
            content = Selector.xpath('/html/body/div[5]/div[1]/div[5]/p/text()')
        if len(content) == 0:
            allData = re.findall('var allData = (.*});', response.text)
            if len(allData) != 0:
                allData=allData[0]
                j=json.loads(allData)
                data = j['docData']['contentData']['contentList'][0]['data']
                data_selector = etree.HTML(data)
                content = data_selector.xpath('//p//text()')
        if len(content) == 0:
            content = Selector.xpath('//div//p//text()')
        if len(content) == 0:
            content = Selector.xpath('//div[@class="content"]//text()')
        if len(content) == 0:
            content=Selector.xpath('//*[@id="contents"]//text()')
        if len(content) == 0:
            content=Selector.xpath('//div[@id="tdcontent"]//text()')
        if len(content) == 0:
            content=Selector.xpath('//div[@class="newDetail"]/div/text()')
        if len(content) == 0:
            content=Selector.xpath('//div[@class="article-body"]/text()')
        if len(content) == 0:
            content=Selector.xpath('//div[@id="__content"]/text()')
        if len(content) == 0:
            content=Selector.xpath('//*[@id="oImg"]/p/text()')
        if len(content) == 0:
            content=Selector.xpath('//div[@class="txt_txt"]//text()')
        # if len(content) == 0:
        #     print(response.meta['href'])
        #     input()
        content=[x.strip() for x in content]
        content=''.join(content).strip()
        content = re.sub(r'[\n\r\t\u3000\xa0\']', '', content)
        return content