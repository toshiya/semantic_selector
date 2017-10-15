import os
import numpy as np
import keras
from gensim import corpora, models, matutils
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from semantic_selector import vectorizer


class NNFullyConnectedModel:

    def __init__(self, training, tests):
        self.training_data = vectorizer.Vectorizer(training)
        self.dictionary = self.training_data.dictionary
        self.num_terms = self.training_data.num_terms
        self.num_classes = self.training_data.num_classes

        self.x_train = self.training_data.x
        self.y_train = keras.utils.to_categorical(self.training_data.y,
                                                  self.num_classes)

        # use dictionary constructed by training data
        self.test_data = vectorizer.Vectorizer(tests,
                                               self.training_data.dictionary,
                                               self.training_data.label_types)
        self.x_test = self.test_data.x
        self.y_test = keras.utils.to_categorical(self.test_data.y,
                                                 self.num_classes)

        self.model = self.__construct()
        self.model.save("nn_fc_model.h5")
        self.train()

    def train(self):
        batch_size = 200
        epochs = 400
        self.model.fit(self.x_train, self.y_train,
                       batch_size=batch_size,
                       epochs=epochs,
                       verbose=1,
                       validation_data=(self.x_test, self.y_test))

        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy', score[1])

    def inference_html(self, record):
        (word_vecs, _) = self.training_data.convert_to_word_vecs([record])
        numpy_vecs = self.training_data.convert_to_numpy_vecs(word_vecs)
        label_id = self.model.predict(numpy_vecs)[0].argmax()
        return self.training_data.label_name_from_id(label_id)

    def __construct(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(self.num_terms,)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])
        return model
