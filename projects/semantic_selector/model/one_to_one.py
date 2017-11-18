import os
import pickle
from keras.losses import categorical_crossentropy
from keras.optimizers import Adadelta
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K


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

    def train(self, adapter, epochs=400):
        # receive attributes from adapter
        for attr in adapter.__dict__.keys():
            setattr(self, attr, adapter.__dict__[attr])

        self.model = self.__construct_neural_network()
        self.model.fit(self.x_train, self.y_train,
                       batch_size=self.batch_size,
                       epochs=epochs,
                       verbose=1,
                       validation_data=(self.x_test, self.y_test))

        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy', score[1])

    def __construct_neural_network(self):
        model = Sequential()
        model.add(Dense(400,
                        activation='relu',
                        input_shape=(len(self.dictionary.keys()),)))
        model.add(Dropout(0.5))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(self.topic_types), activation='softmax'))
        model.compile(loss=categorical_crossentropy,
                      optimizer=Adadelta(),
                      metrics=['accuracy'])
        return model
