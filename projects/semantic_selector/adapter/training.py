from abc import abstractmethod
from gensim import corpora
from semantic_selector.mysql import InputTable
from .base import Adapter


class TrainingAdapter(Adapter):
    def __init__(self, options):
        super().__init__()
        (self.be_train,
         self.ot_train,
         self.be_test,
         self.ot_test) = self.generate_training_data(options)

    @abstractmethod
    def generate_training_data(self, options):
        pass


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
        wv_flatten = []
        for x in word_vecs_train:
            wv_flatten.extend(x)
        self.dictionary = corpora.Dictionary(wv_flatten)

        tp_flatten = []
        for x in topic_vecs_train:
            tp_flatten.extend(x)
        self.all_topics = list(set(tp_flatten))

        be_train = self.to_bow_element_vectors(word_vecs_train)
        ot_train = self.to_one_hot_topic_vectors(topic_vecs_train)
        be_test = self.to_bow_element_vectors(word_vecs_test)
        ot_test = self.to_one_hot_topic_vectors(topic_vecs_test)

        return (be_train, ot_train, be_test, ot_test)
