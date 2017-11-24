import os
import pickle
from keras.losses import categorical_crossentropy
from keras.optimizers import Adadelta
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout


class NNFullyConnectedModel:

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
