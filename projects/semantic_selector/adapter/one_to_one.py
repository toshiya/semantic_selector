# -*- coding: utf-8 -*-
import numpy as np
from keras.utils import to_categorical
from gensim import corpora, matutils
from semantic_selector.mysql import InputTable
from semantic_selector.tokenizer import InputTagTokenizer


# TODO
#class JSONToNNFullyConnect(object):

class MySQLToNNFullyConnectAdapter(object):
    def __init__(self, threashold, ratio, seed):
        (training, tests) = InputTable(threashold).fetch_data(ratio, seed)
        self.__prepare_for_training(training, tests)

    def __prepare_for_training(self, training, tests):
        """
        set self.dictionary, self.lable_types and
        generate train_x(y) and test_x(y)
        """
        (word_vecs_train,
         topics_train) = self.__convert_to_word_vecs(training, with_topic=True)
        (word_vecs_test,
         topics_test) = self.__convert_to_word_vecs(tests, with_topic=True)

        # use dictionary and topic_types of training set
        self.dictionary = corpora.Dictionary(word_vecs_train)
        self.topic_types = list(set(topics_train))

        (self.x_train,
         self.y_train) = self.__adjust_format(word_vecs_train, topics_train)
        (self.x_test,
         self.y_test) = self.__adjust_format(word_vecs_test, topics_test)

    def __convert_to_word_vecs(self, records, with_topic=False):
        input_tag_tokenizer = InputTagTokenizer()
        word_vecs = []
        topics = []
        test_topics = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            if with_topic:
                # Note: use canonical topic instead of raw topic in mysql
                topics.append(r.canonical_topic)
        return (word_vecs, topics)

    def __adjust_format(self, word_vecs, topics=None):
        bows = [self.dictionary.doc2bow(v) for v in word_vecs]
        x = matutils.corpus2dense(bows, len(self.dictionary.keys())).T

        y = None
        if topics is not None:
            y = [self.topic_types.index(l) for l in topics]
            y = np.asarray(y, dtype=np.float32)
            y = to_categorical(y, len(self.topic_types))
        return (x, y)
