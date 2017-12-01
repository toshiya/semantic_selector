from abc import abstractmethod
import numpy as np
from gensim import corpora
from semantic_selector.mysql import InputTable
from semantic_selector.adapter.one_to_one import Adapter, get_attribute


class ManyToManyAdapter(Adapter):
    pass


class TrainingAdapter(ManyToManyAdapter):
    def __init__(self, options):
        (train, test) = self.get_raw_data(options)
        (self.x_train,
         self.y_train,
         self.x_test,
         self.y_test,
         self.max_num_input_tags,
         self.dictionary,
         self.all_topics) = self.make_training_data(train, test)

    # shape must be 2 dimensional
    def pad(self, vec, shape, dtype):
        for i in range(0, shape[0] - len(vec)):
            v = np.zeros((1, shape[1]), dtype=dtype)
            vec = np.append(vec, v, axis=0)
        return vec

    def make_dictionary(self, records):
        word_vecs = self.convert_to_word_vecs(records)
        return corpora.Dictionary(word_vecs)

    def make_all_topics(self, records):
        topic_vecs = self.convert_to_topic_vecs(records)
        return list(set(topic_vecs))

    def make_pages(self, records):
        if len(records) == 0:
            return ([], 0)
        pages = []
        previous_url = None
        current_page = []
        max_num_input_tags = 0
        for record in records:
            url = get_attribute(record, 'url')
            if (previous_url != url) and (len(current_page) != 0):
                if max_num_input_tags < len(current_page):
                    max_num_input_tags = len(current_page)
                pages.append(current_page)
                current_page = []
            current_page.append(record)
            previous_url = url
        pages.append(current_page)
        return (pages, max_num_input_tags)

    def convert_to_x_y(self, pages,
                       max_num_input_tags,
                       dictionary,
                       all_topics):
        dict_size = len(dictionary.keys())
        topic_size = len(all_topics)
        x = np.empty((0, max_num_input_tags, dict_size), dtype='float64')
        y = np.empty((0, max_num_input_tags, topic_size), dtype='float64')
        for page in pages:
            word_vecs = self.convert_to_word_vecs(page)
            numpy_vecs = self.adjust_x_format(dictionary, word_vecs)
            numpy_vecs = self.pad(numpy_vecs,
                                  (max_num_input_tags, dict_size),
                                  'float64')
            x = np.append(x, np.array([numpy_vecs]), axis=0)

            topic_vecs = self.convert_to_topic_vecs(page)
            numpy_topic_vecs = self.adjust_y_format(all_topics, topic_vecs)
            numpy_topic_vecs = self.pad(numpy_topic_vecs,
                                        (max_num_input_tags, topic_size),
                                        'float64')
            y = np.append(y, np.array([numpy_topic_vecs]), axis=0)
        return (x, y)

    def make_training_data(self, train, test):
        dictionary = self.make_dictionary(train)
        all_topics = self.make_all_topics(train)

        (pages_train, max_train) = self.make_pages(train)
        (pages_test, max_test) = self.make_pages(test)
        max_num_input_tags = max(max_train, max_test)

        (x_train, y_train) = self.convert_to_x_y(pages_train,
                                                 max_num_input_tags,
                                                 dictionary,
                                                 all_topics)

        (x_test, y_test) = self.convert_to_x_y(pages_test,
                                               max_num_input_tags,
                                               dictionary,
                                               all_topics)

        return (x_train, y_train, x_test, y_test,
                max_num_input_tags, dictionary, all_topics)

    @abstractmethod
    def get_raw_data(self, options):
        pass


class JSONTrainingAdapter(TrainingAdapter):
    def get_raw_data(self, options):
        train = options['samples']['train']
        test = options['samples']['test']
        return (train, test)


class MySQLTrainingAdapter(TrainingAdapter):
    def get_raw_data(self, options):
        input_table = InputTable(options['threashold'])
        (train, test) = input_table.fetch_data(options['ratio_test'],
                                               options['seed'])
        return (train, test)
