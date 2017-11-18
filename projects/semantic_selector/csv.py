# -*- coding: utf-8 -*-
import os
import csv


class CanonicalTopicTable(object):
    def __init__(self):
        self.canonical_topic_table = self.__read_canonical_topics()

    def get(self):
        return self.canonical_topic_table

    def __read_canonical_topics(self):
        canonical_topic_table = {}
        file_path = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(file_path, '../docs/canonicalTopics.csv')) \
                as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            for row in reader:
                canonical_topic_table[row[0]] = row[1]
        return canonical_topic_table
