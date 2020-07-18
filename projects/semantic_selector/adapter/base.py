# -*- coding: utf-8 -*-
from abc import ABCMeta
import numpy as np
from gensim import matutils
from semantic_selector.tokenizer import InputTagTokenizer


def get_attribute(e, key):
    try:
        if isinstance(e, dict):
            return e[key]
        else:
            return getattr(e, key)
    except KeyError as e:
        return None
    except AttributeError as e:
        return None


class MetaInfo(object):
    def __init__(self, record):
        self.url = get_attribute(record, 'url')
        self.html = get_attribute(record, 'html')
        self.topic = get_attribute(record, 'canonical_topic')

    def __repr__(self):
        return "url:{}\nhtml:{}\ntopic:{}".format(self.url,
                                                  self.html,
                                                  self.topic)


class Adapter(metaclass=ABCMeta):
    def __init__(self):
        self.dictionary = None
        self.all_topics = None
        self.const_nourl = "nourl"
        self.inference = False

    def convert_to_word_vecs(self, records):
        input_tag_tokenizer = InputTagTokenizer()
        url_to_word_vecs = {}
        for r in records:
            url = get_attribute(r, 'url')
            if url is None:
                url = self.const_nourl

            html = get_attribute(r, 'html')
            if html is None:
                raise "record must have html strings."

            label_html = get_attribute(r, 'label_html')
            if label_html is not None:
                html += " " + label_html

            if url not in url_to_word_vecs:
                url_to_word_vecs[url] = []

            word_vec = input_tag_tokenizer.get_attrs_value(html,
                                                           self.inference)
            url_to_word_vecs[url].append(word_vec)

        word_vecs = []
        for url in sorted(url_to_word_vecs):
            word_vecs.append(url_to_word_vecs[url])
        return word_vecs

    def convert_to_topic_vecs(self, records):
        url_to_topic_vecs = {}
        for r in records:
            url = get_attribute(r, 'url')
            if url is None:
                url = self.const_nourl

            canonical_topic = get_attribute(r, 'canonical_topic')
            if canonical_topic is None:
                raise "record must have canonical_topic"

            if url not in url_to_topic_vecs:
                url_to_topic_vecs[url] = []

            url_to_topic_vecs[url].append(canonical_topic)

        topic_vecs = []
        for url in sorted(url_to_topic_vecs):
            topic_vecs.append(url_to_topic_vecs[url])
        return topic_vecs

    def convert_to_meta_vecs(self, records):
        url_to_meta_vecs = {}
        for r in records:
            url = get_attribute(r, 'url')
            if url is None:
                url = self.const_nourl

            if url not in url_to_meta_vecs:
                url_to_meta_vecs[url] = []

            url_to_meta_vecs[url].append(MetaInfo(r))

        meta_vecs = []
        for url in sorted(url_to_meta_vecs):
            meta_vecs.append(url_to_meta_vecs[url])
        return meta_vecs

    def to_bow_element_vectors(self, word_vecs):
        ret = []
        for vecs_in_page in word_vecs:
            dictionary = self.dictionary
            bows = [dictionary.doc2bow(v) for v in vecs_in_page]
            ret.append(matutils.corpus2dense(bows, len(dictionary.keys())).T)
        return ret

    def to_one_hot_topic_vectors(self, topic_vecs):
        all_topics = self.all_topics

        ret = []
        for vecs_in_page in topic_vecs:
            y = [all_topics.index(ll) for ll in vecs_in_page]
            y = np.asarray(y, dtype='int')

            # Note:
            # https://github.com/fchollet/keras/blob/master/keras/utils/np_utils.py
            n = y.shape[0]
            categorical = np.zeros((n, len(all_topics)))
            categorical[np.arange(n), y] = 1
            output_shape = y.shape + (len(all_topics),)
            categorical = np.reshape(categorical, output_shape)
            ret.append(categorical)
        return ret
