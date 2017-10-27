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
        self.topic_types = None

    def load(self):
        self.model = load_model("models/nn_fc_model.h5")
        with open("models/topics.pickle", "rb") as f:
            self.topic_types = pickle.load(f)
        with open("models/inputs.dict", "rb") as f:
            self.dictionary = pickle.load(f)

    def save(self):
        if not os.path.exists("models"):
            os.makedirs("models")
        self.model.save("models/nn_fc_model.h5")
        with open("models/topics.pickle", "wb") as f:
            pickle.dump(self.topic_types, f)
        with open("models/inputs.dict", "wb") as f:
            self.dictionary.save(f)

    def inference_html(self, record):
        (word_vecs, _) = self.__convert_to_word_vecs([record])
        (numpy_vecs, _) = self.__adjust_format(word_vecs)
        topic_id = self.model.predict(numpy_vecs)[0].argmax()
        return self.topic_name_from_id(topic_id)

    def topic_name_from_id(self, topic_id):
        return self.topic_types[topic_id]

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
        (word_vecs_train,
         topics_train) = self.__convert_to_word_vecs(training, with_topic=True)
        (word_vecs_test,
         topics_test) = self.__convert_to_word_vecs(tests, with_topic=True)

        # use dictionary and topic_types of training set
        self.dictionary = corpora.Dictionary(word_vecs_train)
        self.topic_types = list(set(topics_train))

        (self.x_train,
         self.y_train) = self.__adjust_format(word_vecs_train, topics_train)
        (self.x_test,
         self.y_test) = self.__adjust_format(word_vecs_test, topics_test)

    def __adjust_format(self, word_vecs, topics=None):
        bows = [self.dictionary.doc2bow(v) for v in word_vecs]
        x = matutils.corpus2dense(bows, len(self.dictionary.keys())).T

        y = None
        if topics is not None:
            y = [self.topic_types.index(l) for l in topics]
            y = np.asarray(y, dtype=np.float32)
            y = keras.utils.to_categorical(y, len(self.topic_types))
        return (x, y)

    def __convert_to_word_vecs(self, records, with_topic=False):
        input_tag_tokenizer = tokenizer.InputTagTokenizer()
        word_vecs = []
        topics = []
        test_topics = []
        for r in records:
            word_vecs.append(input_tag_tokenizer.get_attrs_value(r.html))
            if with_topic:
                # Note: use canonical topic instead of raw topic in mysql
                topics.append(r.canonical_topic)
        return (word_vecs, topics)

    def __construct_neural_network(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(len(self.dictionary.keys()),)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(self.topic_types), activation='softmax'))
        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])
        return model
