import scrapy
import json
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import uuid
from urllib.parse import quote, unquote
import re
from bs4 import BeautifulSoup
from items import ShzfcgCategoryItem

cgtype = {
    '单一来源公示': 'ZcyAnnouncement1',
    '采购公告': 'ZcyAnnouncement2',
    '更正公告': 'ZcyAnnouncement3',
    '采购结果公告': 'ZcyAnnouncement4',
    '采购合同公告': 'ZcyAnnouncement5',
    '终止公告': 'ZcyAnnouncement6'
}

cgsubtype = {
    '单一来源公示': 'ZcyAnnouncement3012',
    '公开招标公告': 'ZcyAnnouncement3001',
    '竞争性谈判公告': 'ZcyAnnouncement3002',
    '竞争性磋商公告': 'ZcyAnnouncement3011',
    '询价公告': 'ZcyAnnouncement3003',
    '邀请招标资格预审公告': 'ZcyAnnouncement3008',
    '邀请招标资格入围公告': 'ZcyAnnouncement3009',
    '更正公告': 'ZcyAnnouncement3005',
    '其他更正公告': 'ZcyAnnouncement3019',
    '中标（成交）结果公告': 'ZcyAnnouncement3004',
    '废标公告': 'ZcyAnnouncement3007',
    '采购合同公告': 'ZcyAnnouncement3010',
    '终止公告': 'ZcyAnnouncement3015',
}


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
    begin = '2018-01-01'
    end = '2021-01-01'
    cur_begin = end
    cur_end = end
    cur_type = '竞争性磋商公告'
    cur_total = -1
    cur_pageSize = 15
    cur_pageNo = 1
    cur_count = 0

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
        #print(wondersLog_zwdt_sdk)
        #print(_zcy_log_client_uuid)
        self.header['Cookie'] = quote(
            'wondersLog_zwdt_sdk={};_zcy_log_client_uuid={}'.format(json.dumps(wondersLog_zwdt_sdk),
                                                                    _zcy_log_client_uuid))

    def get_body(self):
        self.get_cookie()
        body = {
            "utm": "sites_group_front.7bab83d2.0.0.72ed89a03adf11eb8ed183573b4fc234",
            "categoryCode": cgsubtype[self.cur_type],
            "publishDateBegin": self.cur_begin,
            "publishDateEnd": self.cur_end,
            "pageSize": self.cur_pageSize,
            "pageNo": self.cur_pageNo
        }
        return body

    def start_requests(self):
        body = self.get_body()
        yield scrapy.Request(url=self.category_url, method='POST', headers=self.header, body=json.dumps(body),
                             callback=self.parse_category, errback=self.error_category)

    def parse_category(self, response):
        self.log(self.crawler.stats.get_stats())
        self.log(response)
        #print(response.headers)
        #print(response.body)
        body = json.loads(response.body)
        #print(body)
        #print(body['hits']['hits'])

        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': self.get_cookie()
        }

        if 'hits' in body and 'hits' in body['hits']:
            self.cur_total = body['hits']['total']
            for hit in body['hits']['hits']:
                print(hit)
                url = self.base_url + hit['_source']['url']
                item = {
                    'title': hit['_source']['title'],
                    'publishDate': hit['_source']['publishDate'],
                    'url': url,
                    'pathName': hit['_source']['pathName'],
                    'districtName': hit['_source']['districtName'],
                    'type': hit['_source']['pathName']
                }
                yield scrapy.Request(url=url, method='GET', headers=header,
                                     callback=self.parse_info, meta=item, errback=self.error_info)
            self.cur_pageNo += 1
            dt_cur_begin = datetime.strptime(self.cur_begin, '%Y-%m-%d')
            dt_begin = datetime.strptime(self.begin, '%Y-%m-%d')

            if self.cur_total > (self.cur_pageNo-1) * self.cur_pageSize or (self.cur_total == -1):
                self.log('(记录)当前读取{}/{}，页数{}/{}，日期{}-{}，继续更新'.format(self.cur_count, self.cur_total, self.cur_pageNo,
                                                                   (int(self.cur_total / self.cur_pageSize) + 1), self.cur_begin, self.cur_end))
                body = self.get_body()
                yield scrapy.Request(url=self.category_url, method='POST', headers=self.header, body=json.dumps(body),
                                     callback=self.parse_category, errback=self.error_category)
            elif self.cur_total < (self.cur_pageNo-1) * self.cur_pageSize and dt_cur_begin > dt_begin:
                self.cur_begin = (dt_cur_begin + relativedelta(months=-1)).strftime('%Y-%m-%d')
                self.cur_end = dt_cur_begin.strftime('%Y-%m-%d')
                self.cur_total = -1
                self.cur_pageNo = 1
                self.cur_count = 0
                self.log('(记录)重置搜索条件{} - {}'.format(self.cur_begin, self.cur_end))
                body = self.get_body()
                yield scrapy.Request(url=self.category_url, method='POST', headers=self.header, body=json.dumps(body),
                                     callback=self.parse_category, errback=self.error_category)



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
        highprice = self.get_price(['最高限价：', '最高限价（如有）：'], content)
        winningprice = self.get_price(['中标（成交）金额：', '中标金额：', '成交金额：'], content)

        item = ShzfcgCategoryItem()
        item['title'] = response.meta['title']
        item['publishDate'] = response.meta['publishDate']
        item['url'] = response.meta['url']
        item['pathName'] = response.meta['pathName']
        item['districtName'] = response.meta['districtName']
        item['type'] = response.meta['type']
        item['budgetprice'] = budgetprice
        item['highprice'] = highprice
        item['winningprice'] = winningprice

        self.cur_count += 1
        yield item

    def get_price(self, heads, text):
        # text = re.sub(r'<.*?>', '', text)
        # print(text)

        li_head = ['(?<={})'.format(head) for head in heads]
        str_head = "|".join(li_head)
        # print(str_head)

        str_regexp = r'({})(\s*\d*(\.\d+)?\s*)(.\S*)'.format(str_head)

        # print(str_regexp)
        p = re.compile(str_regexp)
        m = p.search(text)
        # print(m)
        if not m:
            return -1
        self.log('m={},0={}'.format(m, m.group(0)))
        self.log('1={},2={},3={},4={}'.format(m.group(1), m.group(2), m.group(3), m.group(4)))

        price = float(m.group(2).strip()) if m.group(2) and m.group(2).strip() else 0.0

        if m.group(4) and not '万元' in m.group(4):
            price = price / 10000
        # print(price)
        return price

    def error_category(self, failure):
        self.logger.error(repr(failure))

    def error_info(self, failure):
        self.logger.error(repr(failure))
