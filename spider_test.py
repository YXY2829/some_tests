#coding:utf-8
from peewee import *
from lxml import etree
import requests
import re
import gevent
import time

db = MySQLDatabase('iplaysoft', user='root', passwd='rootroot')

class Info(Model):
    title = CharField()
    link = CharField()
    about = CharField()
    date = DateField()

    class Meta:
        database = db

db.connect()
db.create_table(Info)

def run_spider(url):
    """run spider and store"""
    print('-----%s-----'%url)
    content = requests.get(url).content
    html = etree.HTML(content)

    entries = html.xpath('//div[@class="entry" or @class="entry entry-cpt" or @class="entry entry-first"]')
    for entry in entries:
        title_info = entry.find('.//h2[@class="entry-title"]/a')
        title = title_info.text
        print(title)

        link = title_info.get('href')
        print(link)

        about = entry.find('.//div[@class="entry-cat"]')
        about = [inf.text for inf in about if inf.text != '' and inf.text is not None]
        about = ','.join(about)
        print(about)

        dates = entry.xpath('.//div[@class="entry-cat"]/text()')
        date = re.search(r'\d+-\d+-\d+',dates[-1]).group()
        print(date)

        Info.create(title=title, link=link, date=date, about=about)

urls = ('http://www.iplaysoft.com/page/%s'% i for i in range(1,100))
# start = time.time()
# for url in urls:
#     run_spider(url)
# print('time---------',time.time() - start)
# time.sleep(5)
start = time.time()
threads = [gevent.spawn(run_spider, url) for url in urls]
gevent.joinall(threads)
print('time---------',time.time() - start)

db.close()
