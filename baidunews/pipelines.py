# -*- coding: utf-8 -*-
from baidunews import config
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BaidunewsPipeline(object):
    def __init__(self, *args, **kwargs):
        self.client = pymysql.connect(host='localhost', user=config.MYSQL_NAME,
                                      password=config.MYSQL_PASSWORD, port=3306, db=config.DATABASE_NAME)
        self.cur = self.client.cursor()
        self.cur.execute(
            'CREATE TABLE IF NOT EXISTS {} (href VARCHAR(100) PRIMARY KEY , title VARCHAR(60),pub_time VARCHAR(20), company VARCHAR(20),content LONGTEXT)'.format(config.TABLE))
        return super().__init__(*args, **kwargs)

    def process_item(self, item, spider):
        sql = "INSERT INTO {table}(href,title,pub_time,company,content) VALUES('{href}','{title}','{pub_time}','{company}','{content}') ON DUPLICATE KEY UPDATE title='{title}',pub_time='{pub_time}',company='{company}',content='{content}'".format(
            table=config.TABLE, href=item['href'], title=item['title'], pub_time=item['pub_time'], company=item['company'], content=item['content'])
        try:
            if self.cur.execute(sql):
                self.client.commit()
        except:
            print(sql)
            print('************************************************************fail to commit*********************************************')
            self.client.rollback()
        return item
