import os
import pickle
from abc import ABCMeta, abstractmethod


class BaseEstimator(metaclass=ABCMeta):
    def __init__(self):
        self.adapter = None
        self.dictionary = None
        self.all_topics = None
        self.topics_filename = "/topics.pickle"
        self.dictionary_filename = "/dictionary.pickle"

    def set_adapter(self, adapter):
        self.adapter = adapter
        self.dictionary = adapter.dictionary
        self.all_topics = adapter.all_topics

    def load(self, path):
        self.load_model(path)
        with open(path + self.topics_filename, "rb") as f:
            self.all_topics = pickle.load(f)
            self.adapter.all_topics = self.all_topics
        with open(path + self.dictionary_filename, "rb") as f:
            self.dictionary = pickle.load(f)
            self.adapter.dictionary = self.dictionary

    def save(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.save_model(path)
        with open(path + self.topics_filename, "wb") as f:
            pickle.dump(self.all_topics, f)
        with open(path + self.dictionary_filename, "wb") as f:
            self.dictionary.save(f)

    # Note: y_test is topic id array, not one hot vector
    def calc_accuracy(self, x_test, y_test, meta_test, verbose=False):
        sample_n = 0
        correct_n = 0
        for (x, y, m) in zip(x_test, y_test, meta_test):
            prediction = self.predict_x(x)
            if (prediction == y):
                correct_n += 1
            else:
                if verbose:
                    prob_vec = self.predict_x_with_prob_vec(x)
                    if prob_vec is not None:
                        print(m)
                        self.print_probalitity(prob_vec)
            sample_n += 1

        if verbose:
            print("Accuracy Per Url")
            sample_url_n = {}
            correct_url_n = {}
            acc_url = {}
            for (x, y, m) in zip(x_test, y_test, meta_test):
                url = m.url
                if url not in sample_url_n:
                    sample_url_n[url] = 0
                if url not in correct_url_n:
                    correct_url_n[url] = 0
                prediction = self.predict_x(x)
                if (prediction == y):
                    correct_url_n[url] += 1
                sample_url_n[url] += 1
            for url in sample_url_n:
                acc_url[url] = float(correct_url_n[url]) / sample_url_n[url]
            for url, acc in sorted(acc_url.items(), key=lambda x: -x[1]):
                print("    {:110}: {:1.5f}({}/{})".format(url.split('?')[0],
                                                          acc,
                                                          correct_url_n[url],
                                                          sample_url_n[url]))

            print("Accuracy Per Topic")
            sample_tp_n = {}
            correct_tp_n = {}
            acc_tp = {}
            for (x, y, m) in zip(x_test, y_test, meta_test):
                tp = m.topic
                if tp not in sample_tp_n:
                    sample_tp_n[tp] = 0
                if tp not in correct_tp_n:
                    correct_tp_n[tp] = 0
                prediction = self.predict_x(x)
                if (prediction == y):
                    correct_tp_n[tp] += 1
                sample_tp_n[tp] += 1
            for tp in sample_tp_n:
                acc_tp[tp] = float(correct_tp_n[tp]) / sample_tp_n[tp]
            for tp, acc in sorted(acc_tp.items(), key=lambda x: -x[1]):
                print("    {:110}: {:1.5f}({}/{})".format(tp.split('?')[0],
                                                          acc,
                                                          correct_tp_n[tp],
                                                          sample_tp_n[tp]))

        return (float(correct_n) / float(sample_n))

    def print_probalitity(self, prob_vec):
        for (i, p) in enumerate(prob_vec):
            print("    {:25}: {:1.5f}".format(self.all_topics[i], p))
        print()

    @abstractmethod
    def train(self, options=None):
        pass

    @abstractmethod
    def predict(self):
        pass

    # x: element vector e.g. [0, 1, 0, ... , 1, 0]
    # output: topic id e.g. 7
    @abstractmethod
    def predict_x(self, x):
        pass

    @abstractmethod
    def predict_with_prob_vec(self):
        pass

    @abstractmethod
    def predict_x_with_prob_vec(self, x):
        pass

    @abstractmethod
    def save_model(self, path):
        pass

    @abstractmethod
    def load_model(self, path):
        pass
