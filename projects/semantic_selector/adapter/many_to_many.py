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
         self.max_tag_count,
         self.max_word_count,
         self.dictionary,
         self.topics) = self.make_training_data(raw_data, options)

    # shape must be 2 dimensional
    def pad(self, vec, shape, dtype):
        # pad extra feature with zero value
        for i in range(0, len(vec)):
            if len(vec[i]) < shape[1]:
                for j in range(0, shape[1] - len(vec[i])):
                    vec[i].append(0)

        # pad time series with zero vector
        for i in range(0, shape[0] - len(vec)):
            v = np.zeros((1, shape[1]), dtype=dtype)
            vec = np.append(vec, v, axis=0)
        return vec

    def make_dictionary(self, records):
        word_vecs = self.convert_to_word_vecs(records)
        return corpora.Dictionary(word_vecs)

    def make_topics(self, records):
        topic_vecs = self.convert_to_topic_vecs(records)
        topics = list(set(topic_vecs))
        # keep index 0 as mask
        topics.insert(0, 'mask')
        return topics

    def make_pages(self, records, options):
        if len(records) == 0:
            return ([], 0)
        pages = []
        previous_url = None
        current_page = []
        max_tag_count = 0
        for record in records:
            url = get_attribute(record, 'url')
            if (previous_url != url) and (len(current_page) != 0):
                if max_tag_count < len(current_page):
                    max_tag_count = len(current_page)
                pages.append(current_page)
                current_page = []
            current_page.append(record)
            previous_url = url
        pages.append(current_page)

        return (pages, max_tag_count)

    def convert_to_x_y(self,
                       pages,
                       max_tag_count,
                       dictionary,
                       topics):
        topic_count = len(topics)

        max_word_count = 0
        for page in pages:
            word_vecs = self.convert_to_word_vecs(page)
            for word_vec in word_vecs:
                if max_word_count < len(word_vec):
                    max_word_count = len(word_vec)

        x = np.empty((0, max_tag_count, max_word_count), dtype='float64')
        y = np.empty((0, max_tag_count, topic_count), dtype='float64')
        for page in pages:
            word_vecs = self.convert_to_word_vecs(page)
            word_id_vecs = self.adjust_x_format(dictionary, word_vecs)
            word_id_vecs = self.pad(word_id_vecs,
                                    (max_tag_count, max_word_count),
                                    'float64')
            x = np.append(x, np.array([word_id_vecs]), axis=0)

            topic_vecs = self.convert_to_topic_vecs(page)
            topic_one_hot_vecs = self.adjust_y_format(topics, topic_vecs)
            topic_one_hot_vecs = self.pad(topic_one_hot_vecs,
                                          (max_tag_count, topic_count),
                                          'float64')
            y = np.append(y, np.array([topic_one_hot_vecs]), axis=0)

        return (x, y, max_word_count)

    def make_training_data(self, raw_data, options):
        dictionary = self.make_dictionary(raw_data)
        topics = self.make_topics(raw_data)

        (pages, max_tag_count) = self.make_pages(raw_data, options)
        (x, y, max_word_count) = self.convert_to_x_y(pages,
                                                     max_tag_count,
                                                     dictionary,
                                                     topics)

        n = len(pages)
        np.random.seed(options['seed'])
        test_indices = np.random\
                         .permutation(n)[0:int(n * options['ratio_test'])]
        train_indices = np.arange(n)
        for i in test_indices:
            train_indices = np.delete(train_indices, i)

        print(train_indices)

        x_train = x[train_indices]
        y_train = y[train_indices]
        x_test = x[test_indices]
        y_test = y[test_indices]

        return (x_train, y_train, x_test, y_test,
                max_tag_count, max_word_count, dictionary, topics)

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
