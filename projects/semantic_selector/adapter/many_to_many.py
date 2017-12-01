from abc import abstractmethod
import numpy as np
from gensim import corpora
from semantic_selector.adapter.one_to_one import Adapter, get_attribute

class ManyToManyAdapter(Adapter):
    pass

class TrainingAdapter(ManyToManyAdapter):
    def __init__(self, options):
        (self.x_train,
         self.y_train,
         self.x_test,
         self.y_test,
         self.max_num_input_tags,
         self.dictionary,
         self.all_topics) = self.generate_training_data(options)

    # TODO
    def pad(self, vector, shape):
        pass

    def make_dictionary(self, records):
        word_vecs = self.convert_to_word_vecs(records)
        return corpora.Dictionary(word_vecs)

    def make_all_topics(self, records):
        topic_vecs = self.convert_to_topic_vecs(records)
        return list(set(topic_vecs))

    def make_pages(self, records):
        pages = []
        previous_url = None
        current_page = []
        max_num_input_tags = 0
        for record in records:
            url = get_attribute(record, 'url')
            if (previous_url != url) and (current_page is not None):
                if max_num_input_tags < len(current_page):
                    max_num_input_tags = len(current_page)
                    pages.append(current_page)
                    current_page = []
            current_page.append(record)
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
            numpy_vecs = self.pad(numpy_vecs, (max_num_input_tags, dict_size))
            x = np.append(x, np.array([numpy_vecs]), axis=0)

            topic_vecs = self.convert_to_word_vecs(page)
            numpy_topic_vecs = self.adjust_x_format(all_topics, topic_vecs)
            numpy_topic_vecs = self.pad(numpy_topic_vecs,
                                        (max_num_input_tags, topic_size))
            y = np.append(y, np.array([numpy_topic_vecs]), axis=0)
        return (x, y)

    @abstractmethod
    def generate_training_data(self, options):
        pass

class JSONTrainingAdapter(TrainingAdapter):
    def generate_training_data(self, options):
        train = options['samples']['train']
        test = options['samples']['test']

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
