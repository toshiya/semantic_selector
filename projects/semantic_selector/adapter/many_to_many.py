from abc import abstractmethod
import numpy as np
from gensim import corpora
from semantic_selector.mysql import InputTable
from semantic_selector.adapter.one_to_one import Adapter, get_attribute


class ManyToManyAdapter(Adapter):
    pass


class TrainingAdapter(ManyToManyAdapter):
    def __init__(self, options):
        raw_data = self.get_raw_data(options)
        (self.x_train,
         self.y_train,
         self.x_test,
         self.y_test,
         self.max_word_count,
         self.dictionary,
         self.topics) = self.make_training_data(raw_data, options)

    def pad(self, vec, feat_len, dtype):
        for i in range(0, len(vec)):
            if len(vec[i]) < feat_len:
                for j in range(0, feat_len - len(vec[i])):
                    vec[i].append(0)
        return vec

    def get_eos_word_vecs(self):
        return ["EOSEOSEOS"]

    def make_dictionary(self, records):
        word_vecs = self.convert_to_word_vecs(records)
        word_vecs.append(self.get_eos_word_vecs())
        return corpora.Dictionary(word_vecs)

    def make_topics(self, records):
        topic_vecs = self.convert_to_topic_vecs(records)
        topics = list(set(topic_vecs))
        # special labels
        topics.insert(0, 'mask')
        topics.append('eos')
        return topics

    def make_pages(self, records, options):
        if len(records) == 0:
            return ([], 0)
        pages = []
        previous_url = None
        current_page = []
        for record in records:
            url = get_attribute(record, 'url')
            if (previous_url != url) and (len(current_page) != 0):
                pages.append(current_page)
                current_page = []
            current_page.append(record)
            previous_url = url
        pages.append(current_page)

        return pages

    def convert_to_x_y(self,
                       pages,
                       dictionary,
                       topics,
                       options):

        max_word_count = 0
        for page in pages:
            word_vecs = self.convert_to_word_vecs(page)
            word_vecs.append(self.get_eos_word_vecs())
            for word_vec in word_vecs:
                if max_word_count < len(word_vec):
                    max_word_count = len(word_vec)

        topic_count = len(topics)
        x_train = np.empty((0, max_word_count), dtype='float64')
        y_train = np.empty((0, 1, topic_count), dtype='float64')
        x_test = np.empty((0, max_word_count), dtype='float64')
        y_test = np.empty((0, 1, topic_count), dtype='float64')

        n = len(pages)
        np.random.seed(options['seed'])
        test_indices = np.random\
                         .permutation(n)[0:int(n * options['ratio_test'])]

        for (i, page) in enumerate(pages):

            word_vecs = self.convert_to_word_vecs(page)
            topic_vecs = self.convert_to_topic_vecs(page)
            # append eos information
            word_vecs.append(self.get_eos_word_vecs())
            topic_vecs.append('eos')

            word_id_vecs = self.adjust_x_format(dictionary, word_vecs)
            word_id_vecs = self.pad(word_id_vecs, max_word_count, 'float64')
            word_id_vecs = np.array(word_id_vecs)
            topic_one_hot_vecs = self.adjust_y_format(topics, topic_vecs)
            topic_one_hot_vecs = np.array(topic_one_hot_vecs)\
                                   .reshape(topic_one_hot_vecs.shape[0],
                                            1,
                                            topic_one_hot_vecs.shape[1])

            if i in test_indices:
                x_test = np.append(x_test, word_id_vecs, axis=0)
                y_test = np.append(y_test, topic_one_hot_vecs, axis=0)
            else:
                x_train = np.append(x_train, word_id_vecs, axis=0)
                y_train = np.append(y_train, topic_one_hot_vecs, axis=0)

        return (x_train, y_train, x_test, y_test, max_word_count)

    def make_training_data(self, raw_data, options):
        dictionary = self.make_dictionary(raw_data)
        topics = self.make_topics(raw_data)

        pages = self.make_pages(raw_data, options)

        (x_train,
         y_train,
         x_test,
         y_test,
         max_word_count) = self.convert_to_x_y(pages,
                                               dictionary,
                                               topics,
                                               options)

        return (x_train, y_train, x_test, y_test,
                max_word_count, dictionary, topics)

    @abstractmethod
    def get_raw_data(self, options):
        pass


class JSONTrainingAdapter(TrainingAdapter):
    def get_raw_data(self, options):
        return options['samples']


class MySQLTrainingAdapter(TrainingAdapter):
    def get_raw_data(self, options):
        input_table = InputTable(options['threashold'])
        return input_table.fetch_data()
