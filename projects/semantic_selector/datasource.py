# -*- coding: utf-8 -*-
import os
import mysql.connector
import random
import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine


class Inputs(declarative_base()):
    __tablename__ = 'inputs'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    html = Column(String)
    parent_html = Column(String)
    label = Column(String)

    def __repr__(self):
        return "<Input(url='%s', html='%s', label='%s')" % (
                self.url, self.html, self.label)


class InputTags(object):
    class __InputTags:
        def __init__(self, exclude_threshold):
            random.seed(int(time.time()))
            self.engine = create_engine(
                    'mysql+mysqlconnector://root:@localhost/register_form',
                    echo=False)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            self.exclude_threshold = exclude_threshold

        def fetch_data(self, ratio_test_data):
            training_data = []
            test_data = []
            sql = '''
            select * from inputs
                     where label IN
                     (select label from inputs
                                   group by label
                                   having count(1) > :threshold)
                     order by id
'''
            vals = {'threshold': self.exclude_threshold}
            for r in self.session.execute(sql, vals):
                rand = random.randint(0, 100)
                if (rand < 100 * ratio_test_data):
                    test_data.append(r)
                else:
                    training_data.append(r)
            return (training_data, test_data)

    instance = None

    def __init__(self, exclude_threshold=10):
        if not InputTags.instance:
            InputTags.instance = InputTags.__InputTags(exclude_threshold)

    def __getattr__(self, name):
        return getattr(self.instance, name)


if __name__ == "__main__":
    print("datasource")
