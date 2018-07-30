import re

import requests
import scrapy
from scrapy import Request

from ooxx.items import ooxxItem


class ooxx(scrapy.Spider):
    name='ooxx'
    #域中不需要添加http：//否则域会变成网址（urls）
    #域以外的网址会被过滤掉
    allowed_domains=['jandan.net']

    def start_requests(self):
        url='http://jandan.net/ooxx'
        yield Request(url=url, callback=self.parse1)

    def parse1(self,response):
        '获得煎蛋网oxxx首页的页码'
        page_number=re.findall(r'<span class="current-comment-page">\[(\d\d)\]</span>', response.body.decode())[0]
        for i in range(1):
            #获得的页码为字符串类型，需要转换
            number=int(page_number)-i
            url_site='http://jandan.net/ooxx/page-'+str(number)+'#comments'
            yield Request(url=url_site, meta={'Firefox': True}, callback=self.parse2)

    def parse2(self,response):
        #获取每张图片被点赞的次数，以此作为图片排序的顺序
        oo_number=[int(i) for i in response.xpath('//span[@class="tucao-like-container"]/span/text()').extract()]
        oo_number_sort=sorted(oo_number,reverse=True)
        oo_numbers={}
        for i in range(len(oo_number)):
            oo_numbers[oo_number_sort[i]]=i+1
        count1,count2=0,0
        #网站中有一些的点赞数对应着两张图片，这就需要做额外的处理
        #使用finditer而不使用findall的原因是findall返回一个list而finditer返回一个MatchObject类型的iterator，因此可以利用此MatchObject类型来对各图片的hash值位置进行定位
        #注意加载完js后的网页中已经没有img_hashs，不能再以此值来定位
        img_urls = response.xpath('//div[@class="text"]//img/@src').extract()
        img_hashs=re.finditer(r'<li id="comment-(\d+)">',response.body.decode())
        jud,image_url=[],[]
        for img_hash in img_hashs: 
            item=ooxxItem()
            item['folder_name']=response.url.split('/')[-1].split('#')[0]
            jud.append(img_hash.start())
            if  count1 and (jud[count1]-jud[count1-1])<1000:
                count2-=1 
            item['img_name']=str(oo_numbers[oo_number[count2]])+'_'+img_urls[count1].split('/')[-1]
            image_url.append(img_urls[count1])
            count2+=1   
            count1+=1
            item['img_url']=image_url
            yield item
