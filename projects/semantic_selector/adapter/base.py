# -*- coding: utf-8 -*-
from abc import ABCMeta
import numpy as np
from gensim import matutils
from semantic_selector.tokenizer import InputTagTokenizer


class Adapter(metaclass=ABCMeta):
    def convert_to_word_vecs(self, records):
        """
        Note: record must have attributes of html
        """
        input_tag_tokenizer = InputTagTokenizer()
        word_vecs = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
        return word_vecs

    def convert_to_topic_vecs(self, records):
        """
        Note: record must have attributes of canonical_topic
        """
        topic_vecs = []
        for r in records:
            topic_vecs.append(r.canonical_topic)
        return topic_vecs

    def to_bow_element_vectors(self, dictionary, word_vecs):
        bows = [dictionary.doc2bow(v) for v in word_vecs]
        return matutils.corpus2dense(bows, len(dictionary.keys())).T

    def to_one_hot_topic_vectors(self, all_topics, topic_vecs):
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
