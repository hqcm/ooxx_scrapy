# -*- coding: utf-8 -*-

import requests
import os
from scrapy.utils.project import get_project_settings
class ooxxScrapyPipeline(object):
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

     def process_item(self, item, spider):
        img_url=item['img_url']
        img_store = get_project_settings().get('IMAGES_STORE')
        #不借助ImagesPipeline，将每个页面的图放入同一个文件夹
        #子文件夹路径
        file_path=img_store+item['folder_name']
        #图片路径
        img_path=file_path+'/'+item['img_name']
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        image=requests.get(img_url)
        with open(img_path,'wb') as f:
            f.write(image.content)
        return item
