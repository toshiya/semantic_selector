import os
import pickle
from abc import ABCMeta, abstractmethod


class BaseEstimator(metaclass=ABCMeta):
    def __init__(self):
        self.adapter = None
        self.dictionary = None
        self.all_topics = None

    def set_adapter(self, adapter):
        self.adapter = adapter
        self.dictionary = adapter.dictionary
        self.all_topics = adapter.all_topics
        self.topics_filename = "/topics.pickle"
        self.dictionary_filename = "/dictionary.pickle"

    def load(self, path):
        self.load_model(path)
        with open(path + self.topics_filename, "rb") as f:
            self.all_topics = pickle.load(f)
        with open(path + self.dictionary_filename, "rb") as f:
            self.dictionary = pickle.load(f)

    def save(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.save_model(path)
        with open(path + self.topics_filename, "wb") as f:
            pickle.dump(self.all_topics, f)
        with open(path + self.dictionary_filename, "wb") as f:
            self.dictionary.save(f)

    # Note: y_test is topic id array, not one hot vector
    def calc_accuracy(self, x_test, y_test):
        sample_n = 0
        correct_n = 0
        for (x, y) in zip(x_test, y_test):
            prediction = self.predict(x)
            if (prediction == y):
                correct_n += 1
            sample_n += 1
        return (float(correct_n) / float(sample_n))

    @abstractmethod
    def train(self, options=None):
        pass

    # x: element vector e.g. [0, 1, 0, ... , 1, 0]
    # output: topic id e.g. 7
    @abstractmethod
    def predict(self, x):
        pass

    @abstractmethod
    def save_model(self, path):
        pass

    @abstractmethod
    def load_model(self, path):
        pass
