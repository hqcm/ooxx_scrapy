# -*- coding: utf-8 -*-

import os
# 导入这个包为了移动文件
import shutil

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
# 导入项目设置
from scrapy.utils.project import get_project_settings


class ooxxScrapyPipeline(ImagesPipeline):
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    img_store = get_project_settings().get('IMAGES_STORE')
    def get_media_requests(self, item,info):
        for image_url in item['img_url']:
            yield scrapy.Request(image_url)

    def item_completed(self,results,item,info):
        #创建图片存储路径
        #列表生成式,将results的值分别给x,ok,如果ok的值为True,那么就取x['path']最后形成一个一个list
        #结果results为一个二元组的list，每个元组包含(success, image_info_or_error)
        #success: boolean值，success=true表示成功下载 ，反之失败
        #image_info_or_error 是一个包含下列关键字的字典（如果成功为 True ）或者出问题时为 Twisted Failure
        #字典包含以下键值对url：原始URL path：本地存储路径 checksum：校验码。失败则包含一些出错信息
        img_paths=[x['path'] for ok,x in results if ok]
        print (img_paths)
        #判断图片是否下载成功，若不成功则抛出DropItem提示
        if not img_paths:
            raise DropItem('Item contains no images')
        # 定义分类保存的路径
        #采用shutil函数来改变图片保存的路径
        img_path = '%s%s' %(self.img_store, item['folder_name'])
        # 目录不存在则创建目录
        if os.path.exists(img_path) == False:
            os.mkdir(img_path)
        # 将文件从默认路径下移动到指定路径下
        #img_paths[0]总是取第一个图片的地址，有问题
        shutil.move(self.img_store + img_paths[0], img_path + '/' + item['img_name'])
        return item
