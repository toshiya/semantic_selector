# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import numpy as np
from gensim import corpora, matutils
from semantic_selector.mysql import InputTable
from semantic_selector.tokenizer import InputTagTokenizer


class Adapter(metaclass=ABCMeta):
    def convert_to_word_vecs(self, records, with_topic=False):
        """ Note: record must have attributes of html
        """
        input_tag_tokenizer = InputTagTokenizer()
        word_vecs = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
        return word_vecs

    def convert_to_topic_vecs(self, records, with_topic=False):
        """
        Note: record must have attributes of canonical_topic
        """
        topic_vecs = []
        for r in records:
            topic_vecs.append(r.canonical_topic)
        return topic_vecs

    def adjust_x_format(self, dictionary, word_vecs):
        bows = [dictionary.doc2bow(v) for v in word_vecs]
        x = matutils.corpus2dense(bows, len(dictionary.keys())).T
        return x

    def adjust_y_format(self, all_topics, topic_vecs):
        y = [all_topics.index(l) for l in topic_vecs]
        y = np.asarray(y, dtype='int')

        # Note:
        # https://github.com/fchollet/keras/blob/master/keras/utils/np_utils.py
        n = y.shape[0]
        categorical = np.zeros((n, len(all_topics)))
        categorical[np.arange(n), y] = 1
        output_shape = y.shape + (len(all_topics),)
        categorical = np.reshape(categorical, output_shape)
        return categorical


class InferenceAdapter(Adapter):
    def __init__(self, options):
        self.x_infer = self.generate_infered_data(options)

    @abstractmethod
    def generate_infered_data(self, options):
        pass


class TrainingAdapter(Adapter):
    def __init__(self, options):
        (self.x_train,
         self.y_train,
         self.x_test,
         self.y_test,
         self.dictionary,
         self.all_topics) = self.generate_training_data(options)

    @abstractmethod
    def generate_training_data(self, options):
        pass


class JSONInferenceAdapter(InferenceAdapter):
    def generate_infered_data(self, options):
        record = options['record']
        dictionary = options['dictionary']
        word_vecs = self.convert_to_word_vecs([record])
        return self.adjust_x_format(dictionary, word_vecs)


class MySQLTrainingAdapter(TrainingAdapter):
    def generate_training_data(self, options):
        """
        set self.dictionary, self.lable_types and
        generate train_x(y) and test_x(y)
        """
        input_table = InputTable(options['threashold'])
        (training, test) = input_table.fetch_data(options['ratio_test'],
                                                  options['seed'])

        word_vecs_train = self.convert_to_word_vecs(training)
        topic_vecs_train = self.convert_to_topic_vecs(training)
        word_vecs_test = self.convert_to_word_vecs(test)
        topic_vecs_test = self.convert_to_topic_vecs(test)

        # use dictionary and topic_types of training set
        dictionary = corpora.Dictionary(word_vecs_train)
        all_topics = list(set(topic_vecs_train))

        x_train = self.adjust_x_format(dictionary, word_vecs_train)
        y_train = self.adjust_y_format(all_topics, topic_vecs_train)
        x_test = self.adjust_x_format(dictionary, word_vecs_test)
        y_test = self.adjust_y_format(all_topics, topic_vecs_test)
        return (x_train, y_train, x_test, y_test, dictionary, all_topics)
