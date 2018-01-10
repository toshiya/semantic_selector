from .base import BaseEstimator
from keras.losses import categorical_crossentropy
from keras.optimizers import Adadelta
from keras.models import Sequential, load_model as keras_load_model
from keras.layers import Dense, Dropout
import numpy as np


class FNNSimpleEstimator(BaseEstimator):
    def __init__(self):
        super().__init__()
        self.batch_size = 200
        self.model = None
        self.model_filename = '/fnn_simple.h5'

    def train(self, options=None):
        if self.adapter is None:
            raise "please set adapter before training"
        adapter = self.adapter

        epochs = 400
        if 'epochs' in options:
            epochs = options['epochs']

        self.model = self.__construct_neural_network()

        # use bow element vectors directly
        x_train = self.__make_x(adapter.be_train)
        y_train = self.__make_y(adapter.ot_train)
        x_test = self.__make_x(adapter.be_test)
        y_test = self.__make_y(adapter.ot_test)

        self.model.fit(x_train, y_train,
                       batch_size=self.batch_size,
                       epochs=epochs,
                       verbose=1,
                       validation_data=(x_test, y_test))

        score = self.model.evaluate(x_test, y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy', score[1])

        y_test_eval = [v.argmax() for v in y_test]
        print('Validation Acuracy',
              self.calc_accuracy(x_test, y_test_eval, options["verbose"]))

    def predict(self):
        x_infer = self.__make_x(self.adapter.get_bow_element_vectors())
        topic_id = self.predict_x(x_infer[0])
        return self.all_topics[topic_id]

    def predict_with_prob_vec(self):
        x_infer = self.__make_x(self.adapter.get_bow_element_vectors())
        return self.predict_x_with_prob_vec(x_infer[0])

    def predict_x(self, x):
        x = np.array(x)
        x = x.reshape(1, x.shape[0])
        return self.model.predict(x)[0].argmax()

    def predict_x_with_prob_vec(self, x):
        x = np.array(x)
        x = x.reshape(1, x.shape[0])
        return self.model.predict(x)[0]

    def save_model(self, path):
        self.model.save(path + self.model_filename)

    def load_model(self, path):
        self.model = keras_load_model(path + self.model_filename)

    def __construct_neural_network(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(len(self.dictionary.keys()),)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(self.all_topics), activation='softmax'))
        model.summary()
        model.compile(loss=categorical_crossentropy,
                      optimizer=Adadelta(),
                      metrics=['accuracy'])
        return model

    def __make_x(self, vecs):
        flatten = []
        for v in vecs:
            for i in range(0, len(v)):
                a = np.array(v[i])
                v[i] = a / np.linalg.norm(a)
            flatten.extend(v)
        return np.array(flatten)

    def __make_y(self, vecs):
        flatten = []
        for v in vecs:
            flatten.extend(v)
        return np.array(flatten)
