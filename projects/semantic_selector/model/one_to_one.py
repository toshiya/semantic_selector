import os
import pickle
from abc import ABCMeta, abstractmethod
import numpy as np
from gensim import models
from sklearn.linear_model import LogisticRegression
from keras.losses import categorical_crossentropy
from keras.optimizers import Adadelta
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout


class OneToOneModel(metaclass=ABCMeta):
    # y_test should be the form of topic_id vectors
    # not one hot vector
    def calc_accuracy(self, x_test, y_test):
        sample_n = 0
        correct_n = 0
        for (x, y) in zip(x_test, y_test):
            prediction = self.predict(x)
            if (prediction == y):
                correct_n += 1
            sample_n += 1
        return (float(correct_n) / float(sample_n))

    # return topic_id
    @abstractmethod
    def predict(self):
        pass


class NNFullyConnectedModel(OneToOneModel):

    def __init__(self):
        self.batch_size = 200
        self.model = None
        self.dictionary = None
        self.all_topics = None

    def load(self):
        self.model = load_model("models/nn_fc_model.h5")
        with open("models/topics.pickle", "rb") as f:
            self.all_topics = pickle.load(f)
        with open("models/inputs.dict", "rb") as f:
            self.dictionary = pickle.load(f)

    def save(self):
        if not os.path.exists("models"):
            os.makedirs("models")
        self.model.save("models/nn_fc_model.h5")
        with open("models/topics.pickle", "wb") as f:
            pickle.dump(self.all_topics, f)
        with open("models/inputs.dict", "wb") as f:
            self.dictionary.save(f)

    # return raw topic_id
    def predict(self, x):
        x = np.array(x)
        x = x.reshape(1, x.shape[0])
        return self.model.predict(x)[0].argmax()

    def inference_html(self, adapter):
        topic_id = self.model.predict(adapter.x_infer)[0].argmax()
        return self.topic_name_from_id(topic_id)

    def topic_name_from_id(self, topic_id):
        return self.all_topics[topic_id]

    def train(self, adapter, epochs=400):
        # receive attributes from adapter
        self.dictionary = adapter.dictionary
        self.all_topics = adapter.all_topics
        self.model = self.__construct_neural_network()
        self.model.fit(adapter.x_train, adapter.y_train,
                       batch_size=self.batch_size,
                       epochs=epochs,
                       verbose=1,
                       validation_data=(adapter.x_test, adapter.y_test))

        score = self.model.evaluate(adapter.x_test, adapter.y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy', score[1])

        y_test_eval = self.make_y_evaluation(adapter, adapter.topic_vecs_test)
        print('Validation Acuracy',
              self.calc_accuracy(adapter.x_test, y_test_eval))

    def __construct_neural_network(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(len(self.dictionary.keys()),)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(self.all_topics), activation='softmax'))
        model.compile(loss=categorical_crossentropy,
                      optimizer=Adadelta(),
                      metrics=['accuracy'])
        return model

    def make_y_evaluation(self, adapter, vecs):
        return [adapter.all_topics.index(v) for v in vecs]


class LsiModel(OneToOneModel):
    """
    Currently, just for evaluation purpose.
    No support to save and load the model for api server.
    """
    def __init__(self):
        self.hidden_size = 1000
        self.lr_solver = 'newton-cg'
        self.lr_max_iter = 10000
        self.lr_multi_class = 'ovr'

    def train(self, adapter):
        lsi = self.make_lsi(adapter)
        x_train = self.make_x(adapter, lsi, adapter.word_vecs_train)
        y_train = self.make_y(adapter, adapter.topic_vecs_train)
        x_test = self.make_x(adapter, lsi, adapter.word_vecs_test)
        y_test = self.make_y(adapter, adapter.topic_vecs_test)

        print("Train samples: ", len(x_train))
        print("Validation samples: ", len(x_test))

        lr = LogisticRegression(solver=self.lr_solver,
                                max_iter=self.lr_max_iter,
                                multi_class=self.lr_multi_class)
        lr.fit(X=x_train, y=y_train)
        self.lr = lr

        print("Train :", lr.score(X=x_train, y=y_train))
        print("Validation :", lr.score(X=x_test, y=y_test))

        print('Validation Acuracy', self.calc_accuracy(x_test, y_test))

    # return raw topic_id
    def predict(self, x):
        return self.lr.predict([x])[0]

    def make_lsi(self, adapter):
        raw_corpus = [adapter.dictionary.doc2bow(v)
                      for v in adapter.word_vecs_train]
        lsi = models.LsiModel(raw_corpus,
                              id2word=adapter.dictionary,
                              num_topics=self.hidden_size)
        return lsi

    def make_x(self, adapter, lsi, vecs):
        corpus = [adapter.dictionary.doc2bow(v) for v in vecs]
        reduced_corpus = []
        for vec in lsi[corpus]:
            reduced_corpus.append(self.__sparse_to_dense(vec))
        return reduced_corpus

    def make_y(self, adapter, vecs):
        return [adapter.all_topics.index(v) for v in vecs]

    def __sparse_to_dense(self, vec):
        ret = [0 for e in range(self.hidden_size)]
        for v in vec:
            ret[v[0]] = v[1]
        return ret
