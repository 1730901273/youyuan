# -*- coding: utf-8 -*-
import random
import scrapy
from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from youyuan.items import YouyuanItem

import re
import os

cur_path = os.path.abspath(os.path.dirname(__file__))
uafilepath = os.path.join(cur_path, 'data\\useragents.data')


# 随机生成User-Agent
def getRandomUA(uafilepath):
    with open(uafilepath, 'r') as f:
        ua = random.choice(f.readlines())
        ua = ua.strip('\n')
    return ua


# class YySpider(CrawlSpider):
class YySpider(RedisCrawlSpider):
    name = 'yy'
    allowed_domains = ['youyuan.com']
    # start_urls = ['http://www.youyuan.com/find/beijing/mm18-25/advance-0-0-0-0-0-0-0/p1/']
    redis_key = "yyspider:start_urls"

    # 请求头
    def get_headers(self):
        headers = {
            # "Host": "www.youyuan.com",
            # "Connection": "keep-alive",
            # "Upgrade-Insecure-Requests" : "1",
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            #               "Chrome/56.0.2924.87 Safari/537.36",
            "User-Agent": getRandomUA(uafilepath),
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, sdch",
            # "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            # "Referer": url,
            # "Referer": "http://www.youyuan.com/find/beijing/mm18-25/advance-0-0-0-0-0-0-0/p1/",
            # "Cookie": "gr_user_id=b609a4a5-8b03-4078-85b5-0bb0e617daf5; "
            #           "_hp2_id.2147584538=%7B%22userId%22%3A%225361264262655533%22%2C%22pageviewId%22%3A"
            #           "%222812157498870176%22%2C%22sessionId%22%3A%221376560908636027%22%2C%22identity%22%3Anull%2C"
            #           "%22trackerVersion%22%3A%223.0%22%7D; identity=123636274%40qq.com; remember_code=3zB55lODqf; "
            #           "acw_tc=AQAAAMOWGBUfUwgAU3Awtjx04lI+Gr0e; acw_sc=589c0d25fa257c17aedfa3127a7c3a0eac145db7; "
            #           "session=4f1aec94fd99840a562f39488480a9b2798824f9; "
            #           "Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1486565620,1486575689,1486603765,1486603844; "
            #           "Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1486624109; ",
            # "If-Modified-Since": "Thu, 09 Feb 2017 03:35:25 GMT"

        }
        return headers

    # 动态域范围获取
    # def __init__(self, *args, **kwargs):
    #     # Dynamically define the allowed domains list.
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = filter(None, domain.split(','))
    #     print(self.allowed_domains)
    #     super(YySpider, self).__init__(*args, **kwargs)

    # 设置请求头，发起请求
    def make_requests_from_url(self, url):
        # ul = re.findall(r"(.*/p)", url)
        # b = re.findall(r"/p(.*)/", url)
        # num = int(b[0]) - 1
        # ul = str(ul[0]) + str(num)+'/'
        return scrapy.Request(url,
                              headers=self.get_headers(),
                              dont_filter=True)

    # 第一级匹配规则：北京市18~25岁女性的每一页链接匹配规则
    page_links = LinkExtractor(allow=r"youyuan.com/find/sichuan/mm18-25/advance-0-0-0-0-0-0-0/p\d+/")
    # 第二级匹配规则：每个女性个人主页的匹配规则
    profile_links = LinkExtractor(allow=r"youyuan.com/\d+-profile/")

    rules = (
        Rule(page_links),
        Rule(profile_links, callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        item = YouyuanItem()
        # 网名
        item['username'] = self.get_username(response)
        # 年龄
        item['age'] = self.get_age(response)
        # 头像图片的链接
        item['header_url'] = self.get_header_url(response)
        # 相册图片的链接
        item['images_url'] = self.get_images_url(response)
        # 内心独白
        item['content'] = self.get_content(response)
        # 籍贯
        item['place_from'] = self.get_place_from(response)
        # 学历
        item['education'] = self.get_education(response)
        # 　兴趣爱好
        item['hobby'] = self.get_hobby(response)
        # 个人主页
        item['source_url'] = response.url
        # 数据来源网站
        item['sourec'] = "youyuan"

        yield item

    def get_username(self, response):
        username = response.xpath("//dl[@class='personal_cen']//div[@class='main']/strong/text()").extract()
        if len(username):
            username = username[0]
        else:
            username = "NULL"
        return username.strip()

    def get_age(self, response):
        age = response.xpath("//dl[@class='personal_cen']//dd/p/text()").extract()
        if len(age):
            age = re.findall(u"\d+岁", age[0])[0]
        else:
            age = "NULL"
        return age.strip()

    def get_header_url(self, response):
        header_url = response.xpath("//dl[@class='personal_cen']/dt/img/@src").extract()
        if len(header_url):
            header_url = header_url[0]
        else:
            header_url = "NULL"
        return header_url.strip()

    def get_images_url(self, response):
        images_url = response.xpath("//div[@class='ph_show']/ul/li/a/img/@src").extract()
        if len(images_url):
            # mysql数据库
            # images_url = ", ".join(images_url)
            # mongodb数据库
            images_url = images_url
        else:
            images_url = "NULL"
        return images_url

    def get_content(self, response):
        content = response.xpath("//div[@class='pre_data']/ul/li/p/text()").extract()
        if len(content):
            content = content[0]
        else:
            content = "NULL"
        return content.strip()

    def get_place_from(self, response):
        place_from = response.xpath("//div[@class='pre_data']/ul/li[2]//ol[1]/li[1]/span/text()").extract()
        if len(place_from):
            place_from = place_from[0]
        else:
            place_from = "NULL"
        return place_from.strip()

    def get_education(self, response):
        education = response.xpath("//div[@class='pre_data']/ul/li[3]//ol[2]/li[2]/span/text()").extract()
        if len(education):
            education = education[0]
        else:
            education = "NULL"
        return education.strip()

    def get_hobby(self, response):
        hobby = response.xpath("//dl[@class='personal_cen']//ol/li/text()").extract()
        if len(hobby):
            hobby = ",".join(hobby).replace(" ", "")
        else:
            hobby = "NULL"
        return hobby.strip()
