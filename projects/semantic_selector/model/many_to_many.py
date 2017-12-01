import os
import pickle
import numpy as np
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, LSTM, TimeDistributed


class NNLSTMModel:

    def __init__(self):
        self.batch_size = 10
        self.model = None
        self.dictionary = None
        self.all_topics = None

    def load(self):
        self.model = load_model("models/lstm_model.h5")
        with open("models/topics.pickle", "rb") as f:
            self.all_topics = pickle.load(f)
        with open("models/inputs.dict", "rb") as f:
            self.dictionary = pickle.load(f)

    def save(self):
        if not os.path.exists("models"):
            os.makedirs("models")
        self.model.save("models/lstm_model.h5")
        with open("models/topics.pickle", "wb") as f:
            pickle.dump(self.all_topics, f)
        with open("models/inputs.dict", "wb") as f:
            self.dictionary.save(f)

    def inference_html(self, adapter):
        topic_vecs = self.model.predict(adapter.x_infer)[0]
        topic_ids = []
        for topic_vec in topic_vecs:
            if np.count_nonzero(topic_vec) == 0:
                topic_ids.append(-1)
            else:
                topic_ids.append(topic_vecs.argmax())
        return [self.topic_name_from_id(i) for i in topic_ids]

    def topic_name_from_id(self, topic_id):
        if topic_id == -1:
            return 'padding'
        else:
            return self.all_topics[topic_id]

    def train(self, adapter, epochs=400):
        # receive attributes from adapter
        self.dictionary = adapter.dictionary
        self.all_topics = adapter.all_topics
        self.max_num_input_tags = adapter.max_num_input_tags
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
        dict_size = len(self.dictionary.keys())
        topic_size = len(self.all_topics)
        input_shape = (self.max_num_input_tags, dict_size)
        model.add(LSTM(400,
                       activation='relu',
                       input_shape=input_shape,
                       return_sequences=True))
        model.add(Dropout(0.5))
        mlp = TimeDistributed(Dense(topic_size, activation='softmax'))
        model.add(mlp)
        model.compile(loss=categorical_crossentropy,
                      optimizer=Adam(),
                      metrics=['accuracy'])
        return model
