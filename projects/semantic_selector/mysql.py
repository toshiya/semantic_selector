# -*- coding: utf-8 -*-
import os
import mysql.connector
import time
import re
import numpy as np
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, func
from sqlalchemy.ext.hybrid import hybrid_property
from semantic_selector.csv import CanonicalTopicTable


class Input(declarative_base()):
    __tablename__ = 'inputs'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    html = Column(String)
    label_html = Column(String)
    parent_html = Column(String)
    topic = Column(String)
    canonical_table = CanonicalTopicTable().get()

    @hybrid_property
    def canonical_topic(self):
        if self.topic in Input.canonical_table:
            return self.canonical_table[self.topic]
        else:
            return 'unknown'

    def __repr__(self): return "<Input(url='%s', html='%s', topic='%s')>" % (
                self.url, self.html, self.topic)


class InputTable(object):
    def __init__(self, exclude_threshold, connect_info=None):
        if connect_info is None:
            self.connect_info = \
                'mysql+mysqlconnector://root:@localhost/register_form'
        else:
            self.connect_info = connect_info
        self.exclude_threshold = exclude_threshold
        self.session = None
        self.exclude_urls = [
            'miu.ismedia.jp',
            'www.ticket.kintetsu.co.jp',
            'www.charge-net.co.jp',
        ]

    def fetch_data(self):
        data = self.query()
        result = []
        for d in data:
            exclude = False
            for pattern in self.exclude_urls:
                if re.search(pattern, d.url):
                    exclude = True
            if d.canonical_topic == 'exclude':
                exclude = True

            if not exclude:
                result.append(d)

        return result

    def __get_session(self):
        if self.session is None:
            engine = create_engine(
                    self.connect_info,
                    echo=False)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        return self.session

    def query(self):
        session = self.__get_session()
        sub = session.query(Input.topic) \
                     .group_by(Input.topic) \
                     .having(func.count(1) > self.exclude_threshold)
        query = session.query(Input) \
                       .filter(Input.topic.in_(sub))
        return query.all()


if __name__ == "__main__":
    print("datasource")
