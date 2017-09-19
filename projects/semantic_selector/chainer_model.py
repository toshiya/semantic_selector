# -*- coding: utf-8 -*-

# References:
# * https://github.com/chainer/chainer/blob/master/examples/mnist/train_mnist.py
# * https://github.com/ichiroex/chainer-ffnn/blob/master/train.py

import numpy as np
from gensim import corpora, matutils, models, similarities
from sklearn.linear_model import LogisticRegression
from semantic_selector import tokenizer
from semantic_selector import datasource

import os
import shutil
import six
import pickle
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Chain, Variable, optimizers, serializers
from chainer import training
from chainer.training import extensions
from chainer.datasets import tuple_dataset

BATCH_SIZE = int(os.getenv('BATCH_SIZE', '200'))
N_EPOCH    = int(os.getenv('N_EPOCH',    '100'))
N_UNITS_1  = int(os.getenv('N_UNITS_1',  '800'))
N_UNITS_2  = int(os.getenv('N_UNITS_2',  '200'))
DROPOUT    = int(os.getenv('DROPOUT',    '1'))
RELU       = int(os.getenv('RELU',       '1'))

class Model(Chain):
    def __init__(self, in_units, out_units, n_units_1 = N_UNITS_1, n_units_2 = N_UNITS_2):
        super(Model, self).__init__(
            l1=L.Linear(in_units, n_units_1),
            l2=L.Linear(n_units_1, n_units_2),
            l3=L.Linear(n_units_2, out_units),
            )
        self.dropout = DROPOUT
        self.relu    = RELU

    def __call__(self, x):
        h1 = self.l1(x)

        if self.relu == 1:
            h1 = F.relu(h1)
        else:
            h1 = F.sigmoid(h1)

        if self.dropout == 1:
            h1 = F.dropout(h1, 0.5)

        h2 = self.l2(h1)

        if self.relu == 1:
            h2 = F.relu(h2)
        else:
            h2 = F.sigmoid(h2)

        if self.dropout == 1:
            h2 = F.dropout(h2, 0.5)

        return self.l3(h2)

class ChainerModel(object):

    def __init__(self, training, tests):
        if os.getenv('LOAD_MODEL'):
            self.__load_model(os.getenv('LOAD_MODEL'))
        else:
            (self.word_vecs,
             self.label_ids,
             self.label_types) = self.__convert_training(training)
            self.tests = tests
            self.__prepare_data()
            self.__prepare_model()
            self.__train_model()
            self.__save_model()

    def describe(self):
        return "Layer 1: %d, Layer 2: %d, Generations: %d, Batch size: %d" % (N_UNITS_1, N_UNITS_2, N_EPOCH, BATCH_SIZE)

    def __prepare_data(self):
        dictionary = corpora.Dictionary(self.word_vecs)
        # dictionary.save_as_text("words.txt")

        self.in_units = len(dictionary)
        self.out_units = len(self.label_types)

        train_data = []
        for word_vec in self.word_vecs:
            bow = dictionary.doc2bow(word_vec)
            vec = matutils.corpus2dense([bow], self.in_units).T[0]
            train_data.append(np.array(vec).astype(np.float32))
        self.training = tuple_dataset.TupleDataset(train_data,
                                                   np.array(self.label_ids).astype(np.int32))

        self.n = len(self.training)
        self.dictionary = dictionary

        if len(self.tests) > 0:
            self.tests = self.__convert_tests(self.tests)

    def __prepare_model(self, n_units_1 = N_UNITS_1, n_units_2 = N_UNITS_2):
        self.model = Model(self.in_units, self.out_units, n_units_1, n_units_2)
        self.classifier = L.Classifier(self.model)

    def __train_model(self):
        model = self.classifier
        optimizer = optimizers.Adam()
        optimizer.setup(model)

        train_iter = chainer.iterators.SerialIterator(self.training, BATCH_SIZE)
        test_iter =  chainer.iterators.SerialIterator(self.tests, BATCH_SIZE,
                                                      repeat=False, shuffle=False)

        updater = training.StandardUpdater(train_iter, optimizer)
        trainer = training.Trainer(updater, (N_EPOCH, 'epoch'), out='result')

        trainer.extend(extensions.Evaluator(test_iter, model))
        trainer.extend(extensions.dump_graph('main/loss'))
        trainer.extend(extensions.LogReport())

        if extensions.PlotReport.available():
            trainer.extend(
                extensions.PlotReport(['main/loss', 'validation/main/loss'],
                                      'epoch', file_name='loss.png'))
            trainer.extend(
                extensions.PlotReport(
                    ['main/accuracy', 'validation/main/accuracy'],
                    'epoch', file_name='accuracy.png'))
        trainer.extend(extensions.PrintReport(
            ['epoch', 'main/loss', 'validation/main/loss',
             'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))
        trainer.extend(extensions.ProgressBar())

        trainer.run()

        stem = '%s%d_%d.png' % (self.myname(), N_UNITS_1, N_UNITS_2)
        shutil.move('result/loss.png', 'result/loss_%s' % stem)
        shutil.move('result/accuracy.png', 'result/accuracy_%s' % stem)

    def myname(self):
        name = ""
        if self.classifier.predictor.dropout == 1:
            name += "dropout_"
        if self.classifier.predictor.relu == 1:
            name += "relu_"
        else:
            name += "sigmoid_"
        return name


    def __save_model(self):
        print('save the model')
        f = open('model.meta', 'wb')
        pickle.dump([
            self.dictionary,
            self.n,
            self.in_units,
            self.out_units,
            self.label_types,
            N_UNITS_1,
            N_UNITS_2,
            self.classifier.predictor.dropout,
            self.classifier.predictor.relu,
        ], f)
        f.close
        chainer.serializers.save_hdf5("model.hdf5", self.classifier)

    def __load_model(self, filename):
        print('load the model')
        f = open(filename + '.meta', 'rb')
        self.dictionary, self.n, self.in_units, self.out_units, self.label_types, n_units_1, n_units_2, dropout, relu = pickle.load(f)
        f.close
        self.__prepare_model(n_units_1, n_units_2)
        self.classifier.predictor.dropout = dropout
        self.classifier.predictor.relu    = relu
        chainer.serializers.load_hdf5(filename + '.hdf5', self.classifier)

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

    def __convert_tests(self, tests):
        data = []
        labels = []
        for r in tests:
            input_tag_tokenizer = tokenizer.InputTagTokenizer()
            tokens = input_tag_tokenizer.get_attrs_value(r.html)
            bow = self.dictionary.doc2bow(tokens)
            vec = matutils.corpus2dense([bow], self.in_units).T[0]
            if r.label not in self.label_types:
                continue # skip labels undefined in training data
            label_id = self.label_types.index(r.label)
            data.append(np.array(vec).astype(np.float32))
            labels.append(np.int32(label_id))
        return tuple_dataset.TupleDataset(data, labels)

    def inference_html(self, target_tag):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        tokens = input_tag_tokenizer.get_attrs_value(target_tag)
        bow = self.dictionary.doc2bow(tokens)
        vec = matutils.corpus2dense([bow], self.in_units).T[0]
        x = chainer.Variable(np.asarray(np.array([vec]).astype(np.float32)))
        with chainer.using_config('train', False):
            y = self.classifier.predictor(x)
        i = np.argmax(y.data, axis=1).tolist()[0]
        return self._label_name_from_id(i)

    def _label_name_from_id(self, label_id):
        return self.label_types[label_id]

if __name__ == "__main__":
    print("machine learning model")
