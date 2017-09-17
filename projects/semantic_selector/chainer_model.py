# -*- coding: utf-8 -*-

# References:
# * https://github.com/ichiroex/chainer-ffnn/blob/master/train.py

import numpy as np
from gensim import corpora, matutils, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import tokenizer
from semantic_selector import datasource

import os
import six
import pickle
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Chain, Variable, optimizers, serializers

BATCH_SIZE = 100
N_EPOCH   = int(os.getenv('N_EPOCH', '200'))
N_UNITS_1 = int(os.getenv('N_UNITS_1', '800'))
N_UNITS_2 = int(os.getenv('N_UNITS_2', '200'))

class Model(Chain):
    def __init__(self, in_units, out_units):
        super(Model, self).__init__(
            l1=L.Linear(in_units, N_UNITS_1),
            l2=L.Linear(N_UNITS_1, N_UNITS_2),
            l3=L.Linear(N_UNITS_2, out_units),
            )
    def __call__(self, x):
        h1 = F.sigmoid(self.l1(x))
        h2 = F.sigmoid(self.l2(h1))
        return self.l3(h2)

class ChainerModel(object):

    def __init__(self, training):
        if os.getenv('LOAD_SEMANTIC_KUN'):
            self.__load_model()
        else:
            (self.word_vecs,
             self.label_ids,
             self.label_types) = self.__convert_training(training)
            self.__prepare_model()
            self.__train_model()
            self.__save_model()

    def describe(self):
        return "Layer 1: %d, Layer 2: %d, Generations: %d, Batch size: %d" % (N_UNITS_1, N_UNITS_2, BATCH_SIZE, N_EPOCH)

    def __prepare_model(self):
        dictionary = corpora.Dictionary(self.word_vecs)
        dictionary.save_as_text("words.txt")

        self.in_units = len(dictionary)
        self.out_units = len(self.label_types)

        source = []
        for word_vec in self.word_vecs:
            bow = dictionary.doc2bow(word_vec)
            vec = matutils.corpus2dense([bow], self.in_units).T[0]
            source.append(vec)
        target = self.label_ids

        self.n = len(source)
        self.source = np.array(source).astype(np.float32)
        self.target = np.array(target).astype(np.int32)
        self.dictionary = dictionary
        self.model = Model(self.in_units, self.out_units)

    def __train_model(self):
        optimizer = optimizers.Adam()
        optimizer.setup(self.model)

        for epoch in six.moves.range(1, N_EPOCH + 1):
            print('epoch', epoch)

            perm = np.random.permutation(self.n)
            sum_train_loss     = 0.0
            sum_train_accuracy = 0.0
            for i in six.moves.range(0, self.n, BATCH_SIZE):
                x = chainer.Variable(np.asarray(self.source[perm[i:i + BATCH_SIZE]])) #source
                t = chainer.Variable(np.asarray(self.target[perm[i:i + BATCH_SIZE]])) #target

                self.model.zerograds()
                y = self.model(x)
                loss = F.softmax_cross_entropy(y, t)
                acc = F.accuracy(y, t)
                sum_train_loss += loss.data * len(t)
                sum_train_accuracy += acc.data * len(t)
                loss.backward()
                optimizer.update()

            print('train mean loss={}, accuracy={}'.format(
                sum_train_loss / self.n, sum_train_accuracy / self.n))

    def __save_model(self):
        print('save the model')
        f = open('semantic-kun.pkl', 'wb')
        pickle.dump([
            self.dictionary,
            self.n,
            self.in_units,
            self.label_types,
            self.model,
        ], f)
        f.close

    def __load_model(self):
        print('load the model')
        f = open('semantic-kun.pkl', 'rb')
        self.dictionary, self.n, self.in_units, self.label_types, self.model = pickle.load(f)
        f.close

    def __convert_training(self, training):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        word_vecs = []
        labels = []
        test_labels = []
        for r in training:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            labels.append(r.label)

        label_types = list(set(labels))
        label_ids = [label_types.index(x) for x in labels]

        return (word_vecs, label_ids, label_types)

    def inference_html(self, target_tag):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        tokens = input_tag_tokenizer.get_attrs_value(target_tag)
        bow = self.dictionary.doc2bow(tokens)
        vec = matutils.corpus2dense([bow], self.in_units).T[0]
        x = chainer.Variable(np.asarray(np.array([vec]).astype(np.float32)))
        self.model.zerograds()
        y = F.softmax(self.model(x)).data[0].tolist()
        i = y.index(max(y))
        return self._label_name_from_id(i)

    def _label_name_from_id(self, label_id):
        return self.label_types[label_id]

if __name__ == "__main__":
    print("machine learning model")
