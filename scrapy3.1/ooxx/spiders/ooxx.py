import hashlib
import re

import execjs
import requests
import scrapy
from scrapy import Request

from ooxx.items import ooxxItem


class ooxx(scrapy.Spider):
    name='ooxx'
    #域中不需要添加http：//否则域会变成网址（urls）
    #域以外的网址会被过滤掉
    allowed_domains=['jandan.net']
    #start_urls中的s不要去掉
    start_urls=['http://jandan.net/ooxx']
    #第一个函数名字需为parse，否则callback会表示没有定义，原因不明
    def parse(self,response):
        '获得煎蛋网oxxx首页的页码'
        page_number=re.findall(r'<span class="current-comment-page">\[(\d\d)\]</span>', response.body.decode())[0]
        for i in range(2):
            #获得的页码为字符串类型，需要转换
            number=int(page_number)-i
            url_site='http://jandan.net/ooxx/page-'+str(number)+'#comments'
            yield Request(url=url_site,callback=self.parse2)

    def parse2(self,response):
        #获取每张图片被点赞的次数，以此作为图片排序的顺序
        #注意匹配的字符串中有空格o(╥﹏╥)o
        #转换为int型，方便比较大小
        oo_number=[int(i) for i in re.findall(r'OO</a> \[<span>(\d+)</span>\]', response.body.decode())]
        oo_number_sort=sorted(oo_number,reverse=True)
        oo_numbers={}
        for i in range(len(oo_number)):
            oo_numbers[oo_number_sort[i]]=i+1
        count1,count2=0,0
        #网站中有一些的点赞数对应着两张图片，这就需要做额外的处理
        #使用finditer而不使用findall的原因是findall返回一个list而finditer返回一个MatchObject类型的iterator，因此可以利用此MatchObject类型来对各图片的hash值位置进行定位
        img_hashs=re.finditer(r'<span class="img-hash">(\S+)</span>',response.body.decode())
        #正则匹配后的js的地址有两个，取包含jandan_load_img函数的最后一个js文件
        js_url = 'http:' + re.findall(r'<script src="(//cdn.jandan.net/static/min/\w+\.\d+\.js)"></script>', response.body.decode())[-1]
        _r = self.get_r(js_url)
        jud=[]
        for img_hash in img_hashs:       
            #group()代表整个正则的匹配，1表示取第一个分组
            img_url=self.get_imgurl(img_hash.group(1),_r)
            item=ooxxItem()
            #对返回的列表进行索引，[-1]为选取倒数第一项
            item['folder_name']=response.url.split('/')[-1].split('#')[0]
            jud.append(img_hash.start())
            if  count1 and (jud[count1]-jud[count1-1])<1000:
                count2-=1 
            item['img_name']=str(oo_numbers[oo_number[count2]])+'_'+img_url.split('/')[-1]
            count2+=1   
            count1+=1
            item['img_url']='http:' + img_url
            yield item
            #也可以：
            #items=[]
            #for item in items:
            #yield item

    def get_r(self,js_url):
        '获得js函数中所需的字符串'
        js = requests.get(js_url).text
        _r = re.findall(r'c=\w+\(e,"(\w+)"\)', js)[0]
        return _r

    def get_js(self): 
        '读取js函数'
        with open(r"C:\Users\Administrator\Desktop\ooxx.js", 'r', encoding='UTF-8') as f:
            line = f.readline()  
            htmlstr = ''  
            while line:  
                htmlstr = htmlstr + line  
                line = f.readline()  
        return htmlstr  

    def get_imgurl(self, img_hash, r):
        '解密获取图片链接'
        jsstr = self.get_js()  
        ctx = execjs.compile(jsstr)  
        #注意得到的图片地址需要将末尾的'\x00'去掉
        return ctx.call('ooxx',img_hash,r,0).strip('\x00')
