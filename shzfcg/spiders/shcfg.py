import scrapy
import json
from datetime import datetime, date, timedelta
import uuid
from urllib.parse import quote, unquote
import re
from bs4 import BeautifulSoup


class ShcfgSpider(scrapy.Spider):
    name = 'shcfg'
    allowed_domains = ['zfcg.sh.gov.cn']
    # start_urls = ['http://www.zfcg.sh.gov.cn/ZcyAnnouncement/ZcyAnnouncement2/ZcyAnnouncement3003/r2UvoCvvLg8e7YNiaDg7tw==.html?utm=sites_group_front.5397f2d7.0.0.8bf26a103adf11ebafc32b5866e11122']
    category_url = 'http://www.zfcg.sh.gov.cn/front/search/category'
    base_url = 'http://www.zfcg.sh.gov.cn'
    header = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    body = {
        "utm": "sites_group_front.7bab83d2.0.0.72ed89a03adf11eb8ed183573b4fc234",
        "categoryCode": "ZcyAnnouncement3003",
        "pageSize": 1,
        "pageNo": 1
    }

    def parse(self, response):
        print(response)
        print(response.headers)
        print(response.body)

    def get_cookie(self):
        wondersLog_zwdt_sdk = \
            {
                "persistedTime": 1607175344139,
                "userId": "",
                "superProperties": {},
                "updatedTime": 1607175345046,
                "sessionStartTime": 1607175345043,
                "sessionReferrer": "http://scjgj.sh.gov.cn/",
                "deviceId": "1a66bb1df94f6186bce4f173771eba7c-5055",
                "LASTEVENT": {
                    "eventId": "wondersLog_pv",
                    "time": 1607175345045
                },
                "sessionUuid": 8864599428283482,
                "costTime": {}
            }
        _zcy_log_client_uuid = uuid.uuid1()
        _tms_now = int(datetime.now().timestamp() * 1000)
        wondersLog_zwdt_sdk['persistedTime'] = wondersLog_zwdt_sdk['updatedTime'] = wondersLog_zwdt_sdk[
            'sessionStartTime'] = wondersLog_zwdt_sdk['LASTEVENT']['time'] = _tms_now
        print(wondersLog_zwdt_sdk)
        print(_zcy_log_client_uuid)
        return quote('wondersLog_zwdt_sdk={};_zcy_log_client_uuid={}'.format(json.dumps(wondersLog_zwdt_sdk),
                                                                             _zcy_log_client_uuid))

    def start_requests(self):
        cookie = self.get_cookie()
        self.header['Cookie'] = cookie
        yield scrapy.Request(url=self.category_url, method='POST', headers=self.header, body=json.dumps(self.body),
                             callback=self.parse_category)

    def parse_category(self, response):
        print(response)
        print(response.headers)
        print(response.body)
        body = json.loads(response.body)
        print(body)
        print(body['hits']['hits'])

        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': self.get_cookie()
        }

        if 'hits' in body and 'hits' in body['hits']:
            for hit in body['hits']['hits']:
                print(hit)
                print(hit['_source']['pathName'])
                print(hit['_source']['districtName'])
                print(hit['_source']['title'])
                print(hit['_source']['url'])
                url = self.base_url + hit['_source']['url']
                yield scrapy.Request(url=url, method='GET', headers=header, body=json.dumps(self.body),
                                     callback=self.parse_info)

    def parse_info(self, response):
        print(response)
        # print(response.headers)
        # print(response.body.decode('utf-8'))
        text = response.body.decode('utf-8')
        soup = BeautifulSoup(text, 'html.parser')
        obj = soup.find('input', attrs={"name": "articleDetail"})
        content = obj.__str__()
        budgetprice = highprice = winningprice = 0
        budgetprice = self.get_price(['预算金额：'], content)
        highprice = self.get_price(['最高限价（如有）：'], content)
        winningprice = self.get_price(['中标（成交）金额：', '中标金额：', '成交金额：'], content)
        

    def get_price(self, heads, text):
        #text = re.sub(r'<.*?>', '', text)
        #print(text)

        li_head = ['(?<={})'.format(head) for head in heads]
        str_head = "|".join(li_head)
        print(str_head)

        str_regexp = r'({})(\s*\d*(\.\d+)?\s*)(.\S*)'.format(str_head)

        print(str_regexp)
        p = re.compile(str_regexp)
        m = p.search(text)
        print(m)
        if not m:
            return -1
        print('m={},0={}'.format(m, m.group(0)))
        print('1={},2={},3={},4={}'.format(m.group(1), m.group(2), m.group(3), m.group(4)))

        price = float(m.group(2).strip()) if m.group(2) and m.group(2).strip() else 0.0

        if m.group(4) and not '万元' in m.group(4):
            price = price / 10000
        # print(price)
        return price
