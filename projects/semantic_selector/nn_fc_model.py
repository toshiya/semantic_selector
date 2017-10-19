import os
import pickle
import numpy as np
import keras
from gensim import corpora, models, matutils
from keras.datasets import mnist
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from semantic_selector import tokenizer


class NNFullyConnectedModel:

    def __init__(self):
        self.batch_size = 200
        self.model = None
        self.dictionary = None
        self.label_types = None

    def load(self):
        self.model = load_model("models/nn_fc_model.h5")
        with open("models/labels.pickle", "r") as f:
            self.label_types = pickle.load(f)
        with open("models/inputs.dict", "r") as f:
            self.dictionary = pickle.load(f)

    def save(self):
        if not os.path.exists("models"):
            os.makedirs("models")
        self.model.save("models/nn_fc_model.h5")
        with open("models/labels.pickle", "wb") as f:
            pickle.dump(self.label_types, f)
        with open("models/inputs.dict", "wb") as f:
            self.dictionary.save(f)

    def inference_html(self, record):
        (word_vecs, _) = self.__convert_to_word_vecs([record])
        (numpy_vecs, _) = self.__adjust_format(word_vecs)
        label_id = self.model.predict(numpy_vecs)[0].argmax()
        return self.label_name_from_id(label_id)

    def label_name_from_id(self, label_id):
        return self.label_types[label_id]

    def train(self, training, test, epochs=400):
        self.__prepare_for_training(training, test)
        self.model = self.__construct_neural_network()
        self.model.fit(self.x_train, self.y_train,
                       batch_size=self.batch_size,
                       epochs=epochs,
                       verbose=1,
                       validation_data=(self.x_test, self.y_test))

        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy', score[1])

    def __prepare_for_training(self, training, tests):
        """
        set self.dictionary, self.lable_types and
        generate train_x(y) and test_x(y)
        """
        (word_vecs_train, labels_train) = self.__convert_to_word_vecs(training)
        (word_vecs_test, labels_test) = self.__convert_to_word_vecs(tests)

        # use dictionary and label_types of training set
        self.dictionary = corpora.Dictionary(word_vecs_train)
        self.label_types = list(set(labels_train))

        (self.x_train,
         self.y_train) = self.__adjust_format(word_vecs_train, labels_train)
        (self.x_test,
         self.y_test) = self.__adjust_format(word_vecs_test, labels_test)

    def __adjust_format(self, word_vecs, labels=None):
        bows = [self.dictionary.doc2bow(v) for v in word_vecs]
        x = matutils.corpus2dense(bows, len(self.dictionary.keys())).T

        y = None
        if labels is not None:
            y = [self.label_types.index(l) for l in labels]
            y = np.asarray(y, dtype=np.float32)
            y = keras.utils.to_categorical(y, len(self.label_types))
        return (x, y)

    def __convert_to_word_vecs(self, records):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        word_vecs = []
        labels = []
        test_labels = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            labels.append(r.label)
        return (word_vecs, labels)

    def __construct_neural_network(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(len(self.dictionary.keys()),)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(self.label_types), activation='softmax'))
        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])
        return model
