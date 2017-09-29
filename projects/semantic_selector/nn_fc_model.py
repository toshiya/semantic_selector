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
        self.vector_data = vectorizer.Vectorizer(training, tests)
        self.num_terms = self.vector_data.get_input_dim()
        self.num_classes = self.vector_data.get_output_dim()

        # data
        (self.x_train, y_train) = self.vector_data.get_training()
        (self.x_test, y_test) = self.vector_data.get_test()

        self.y_train = keras.utils.to_categorical(y_train, self.num_classes)
        self.y_test = keras.utils.to_categorical(y_test, self.num_classes)

        self.model = self.__construct()
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
        (word_vecs, _) = self.vector_data.convert_to_word_vecs([record])
        numpy_vecs = self.vector_data.convert_to_numpy_vecs(word_vecs)
        label_id = self.model.predict(numpy_vecs)[0].argmax()
        return self.vector_data.label_name_from_id(label_id)

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
