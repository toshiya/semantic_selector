import os
import csv
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
    def calc_accuracy(self, x_test, y_test, meta_test, verbose=0):
        sample_n = 0
        ans_n = 0
        pred_n = 0
        correct_n = 0
        correct_u_n = 0
        unknown_n = 0
        for (x, y, m) in zip(x_test, y_test, meta_test):
            ans = m.topic
            pred = self.all_topics[self.predict_x(x)]
            if ans == pred:
                correct_u_n += 1
                if ans != 'unknown':
                    correct_n += 1
            else:
                if verbose >= 3:
                    prob_vec = self.predict_x_with_prob_vec(x)
                    if prob_vec is not None:
                        print(m)
                        self.print_probalitity(prob_vec)
            if ans != 'unknown':
                ans_n += 1
            else:
                unknown_n += 1
            if pred != 'unknown':
                pred_n += 1
            sample_n += 1

        total_recall = float(correct_n) / ans_n
        total_precision = float(correct_n) / pred_n
        fmeasure = (2*total_recall*total_precision) / \
                   (total_recall + total_precision)
        print("Recall(correct_n/ans_n)    : {:1.5f}({:3d}/{:3d})"
              .format(total_recall, correct_n, ans_n))
        print("Precision(correct_n/pred_n): {:1.5f}({:3d}/{:3d})"
              .format(total_precision, correct_n, pred_n))
        print("F Measure                  : {:1.5f}".format(fmeasure))
        print("ration of unknown samples: {:1.5f}({:3d}/{:3d})".format(
              float(unknown_n)/sample_n,
              unknown_n,
              sample_n))

        if verbose >= 2:
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

        if verbose >= 1:
            print("Per Topic :Recall(correct_n/ans_n)"
                  " Precision(correct_n/pred_n)"
                  " F-Measure")
            ans_tp_n = self.zero_table()
            pred_tp_n = self.zero_table()
            correct_tp_n = self.zero_table()
            recall_tp = {}
            precision_tp = {}
            fmeasure_tp = {}
            for (x, y, m) in zip(x_test, y_test, meta_test):
                ans = m.topic
                pred = self.all_topics[self.predict_x(x)]

                if ans == pred:
                    correct_tp_n[ans] += 1
                ans_tp_n[ans] += 1
                pred_tp_n[pred] += 1

            for tp in ans_tp_n:
                if ans_tp_n[tp] > 0:
                    recall_tp[tp] = float(correct_tp_n[tp]) / ans_tp_n[tp]
                else:
                    recall_tp[tp] = 0
            for tp in pred_tp_n:
                if pred_tp_n[tp] > 0:
                    precision_tp[tp] = float(correct_tp_n[tp]) / pred_tp_n[tp]
                else:
                    precision_tp[tp] = 0
                if recall_tp[tp] + precision_tp[tp] > 0:
                    fmeasure_tp[tp] = (2*recall_tp[tp]*precision_tp[tp] /
                                       (recall_tp[tp] + precision_tp[tp]))
                else:
                    fmeasure_tp[tp] = 0

            for tp, _ in sorted(fmeasure_tp.items(), key=lambda x: -x[1]):
                print_format = "    {:30}: {:1.5f}({:3d}/{:3d})"\
                               " {:1.5f}({:3d}/{:3d})"\
                               " {:1.5f}"
                print(print_format.format(tp.split('?')[0],
                                          recall_tp[tp],
                                          correct_tp_n[tp],
                                          ans_tp_n[tp],
                                          precision_tp[tp],
                                          correct_tp_n[tp],
                                          pred_tp_n[tp],
                                          fmeasure_tp[tp]))

            with open('per_topic.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['Topic Name',
                                 'Recall',
                                 'Precision',
                                 'FMeasure'])
                for tp, _ in sorted(recall_tp.items(), key=lambda x: -x[1]):
                    writer.writerow([tp,
                                     recall_tp[tp],
                                     precision_tp[tp],
                                     fmeasure_tp[tp]])

        return (float(correct_u_n) / float(sample_n))

    def print_probalitity(self, prob_vec):
        for (i, p) in enumerate(prob_vec):
            print("    {:25}: {:1.5f}".format(self.all_topics[i], p))
        print()

    def zero_table(self):
        r = {}
        for k in self.all_topics:
            r[k] = 0
        return r

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
