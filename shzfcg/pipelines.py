# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, Table, MetaData, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, date, timedelta
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import insert
from items import ShzfcgCategoryItem
from datetime import datetime, date, timedelta
import copy


class Bid(object):
    def __init__(self, title, time, supplier, agent, area, county, href, type, budgetprice, highprice, winningprice):
        self.title = title
        self.time = time
        self.supplier = supplier
        self.agent = agent
        self.area = area
        self.county = county
        self.href = href
        self.type = type
        self.budgetprice = budgetprice
        self.highprice = highprice
        self.winningprice = winningprice
        self.createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ShzfcgPipeline:
    def bid_upsert(self, bid):
        insert_stmt = insert(self.t_bid).values(
            id=bid.id,
            title=bid.title,
            time=bid.time,
            supplier=bid.supplier,
            agent=bid.agent,
            area=bid.area,
            county=bid.county,
            href=bid.href,
            type=bid.type,
            budgetprice=bid.budgetprice,
            highprice=bid.highprice,
            winningprice=bid.winningprice,
            createtime=bid.createtime)

        on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
            title=insert_stmt.inserted.title,
            time=insert_stmt.inserted.time,
            supplier=insert_stmt.inserted.supplier,
            agent=insert_stmt.inserted.agent,
            area=insert_stmt.inserted.area,
            county=insert_stmt.inserted.county,
            type=insert_stmt.inserted.type,
            budgetprice=insert_stmt.inserted.budgetprice,
            highprice=insert_stmt.inserted.highprice,
            winningprice=insert_stmt.inserted.winningprice,
            createtime=insert_stmt.inserted.createtime,
            status='U')
        self.conn.execute(on_duplicate_key_stmt)

    def __init__(self, engine):
        self.conn = engine.connect()
        metadata = MetaData()
        self.t_bid = Table('bid', metadata,
                           Column('id', Integer, primary_key=True, autoincrement=True),
                           Column('title', Text()),
                           Column('time', DateTime()),
                           Column('supplier', Text()),
                           Column('agent', Text()),
                           Column('area', Text()),
                           Column('county', Text()),
                           Column('href', String(255)),
                           Column('type', Text()),
                           Column('budgetprice', DECIMAL()),
                           Column('highprice', DECIMAL()),
                           Column('winningprice', DECIMAL()),
                           Column('createtime', DateTime()),
                           UniqueConstraint('href', 'time', name='idx_href_time')
                           )
        mapper(Bid, self.t_bid)
        metadata.create_all(engine)

    @classmethod
    def from_settings(cls, settings):
        print(settings['MYSQL_DB'])
        engine = create_engine(settings['MYSQL_DB'], encoding='utf-8', echo=True)
        return cls(engine)

    def process_item(self, item, spider):
        categoryItem = copy.deepcopy(item)
        if isinstance(categoryItem, ShzfcgCategoryItem):
            time = datetime.fromtimestamp(item["publishDate"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            bid = Bid(title=item["title"], href=item["url"], time=time, supplier=item['supplier'],
                      agent="", area='上海', county=item["districtName"], type=item['type'],
                      budgetprice=item['budgetprice'], highprice=item['highprice'], winningprice=item['winningprice'])
            self.bid_upsert(bid)
        return item
